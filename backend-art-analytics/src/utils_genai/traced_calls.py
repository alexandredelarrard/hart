import json
from contextlib import contextmanager
from pprint import pformat

from openai import AsyncOpenAI, RateLimitError
from openai.types import Completion
from openinference.semconv.trace import (
    OpenInferenceMimeTypeValues,
    OpenInferenceSpanKindValues,
    SpanAttributes,
)
from opentelemetry.trace import Status, StatusCode, get_tracer
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
    wait_random,
)

from src.genai_utils.deepmerge import deepmerge
from src.genai_utils.memoize import memoize
from src.genai_utils.params import (
    OpenAICompletionParams,
    params_to_dict,
    vLLMExtraCompletionParams,
)
from src.genai_utils.prompts import _Prompt

CONFIG__TRACER_NAME = __name__


def get_text_of_completion_first_choice(completion: Completion):
    return completion.choices[0].text


# shortcut
get_text = get_text_of_completion_first_choice


class TracedVLLMCompletion:
    def __init__(
        self,
        client: AsyncOpenAI,
        openai_completion_params: OpenAICompletionParams | dict | None = None,
        vllm_extra_completion_params: vLLMExtraCompletionParams | dict | None = None,
        metadata: dict | None = None,
        span_name: str = "llm completion",
        use_cache: bool = True,
    ):
        self.client = client
        self.openai_completion_params = openai_completion_params
        self.vllm_extra_completion_params = vllm_extra_completion_params
        self.span_name = span_name
        self.metadata = metadata
        self.use_cache = use_cache

    async def __call__(
        self,
        prompt: str | _Prompt,
        openai_completion_params: OpenAICompletionParams | dict | None = None,
        vllm_extra_completion_params: vLLMExtraCompletionParams | dict | None = None,
        ground_truth=None,
        metadata: dict | None = None,
        span_name: str | None = None,
        use_cache: bool | None = None,
    ):
        #
        # Process arguments (merge defaults etc..)
        #
        use_cache = use_cache if use_cache is not None else self.use_cache

        span_name = span_name or self.span_name
        metadata = deepmerge(self.metadata or {}, metadata or {})

        init_openai_params = params_to_dict(self.openai_completion_params)
        call_openai_params = params_to_dict(openai_completion_params)

        # those are actually for vLLM
        init_extra_body = init_openai_params.pop("extra_body", {})
        call_extra_body = call_openai_params.pop("extra_body", {})

        openai_params = deepmerge(init_openai_params, call_openai_params)
        vllm_params = deepmerge(
            init_extra_body,
            params_to_dict(self.vllm_extra_completion_params),
            call_extra_body,
            params_to_dict(vllm_extra_completion_params),
        )

        if openai_params.get("stream", False):
            raise NotImplementedError("`stream=True` is not supported.")

        if "model" not in openai_params:
            raise KeyError(
                'It\'s necessary to pass a "model" key to the openai params.'
            )

        #
        # Traced LLM Call
        #
        tracer = get_tracer(CONFIG__TRACER_NAME)
        with tracer.start_as_current_span(span_name) as top_level_span:
            top_level_span.set_attributes(
                {
                    SpanAttributes.LLM_MODEL_NAME: openai_params["model"],
                    SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.LLM.value,
                    SpanAttributes.INPUT_MIME_TYPE: OpenInferenceMimeTypeValues.TEXT.value,
                    SpanAttributes.INPUT_VALUE: str(prompt),
                    SpanAttributes.LLM_INVOCATION_PARAMETERS: json.dumps(
                        {
                            **openai_params,
                            **vllm_params,
                        },
                        sort_keys=True,
                    ),
                }
            )
            if isinstance(prompt, _Prompt):
                top_level_span.set_attributes(
                    {
                        SpanAttributes.LLM_PROMPT_TEMPLATE: prompt.template,
                        SpanAttributes.LLM_PROMPT_TEMPLATE_VARIABLES: json.dumps(
                            prompt.template_variables
                        ),
                    }
                )

            # -- RETRY
            # "When multiple processes are in contention for a shared resource,
            # exponentially increasing jitter helps minimise collisions."
            # -- https://tenacity.readthedocs.io/en/latest/#waiting-before-retrying
            @retry(
                retry=retry_if_exception_type(RateLimitError),
                stop=stop_after_attempt(8),
                wait=wait_fixed(15) + wait_random(5),
                reraise=True,
            )
            async def create_completion(**kwargs):
                return await self.client.completions.create(**kwargs)

            # -- CACHE
            if use_cache:
                create_completion = memoize(user_friendly_id=span_name)(
                    create_completion
                )

            # completion = await self.client.completions.create(
            completion = await create_completion(
                prompt=str(prompt),
                extra_body=vllm_params,
                **openai_params,
            )

            OUTPUT_KIND = OpenInferenceMimeTypeValues.TEXT.value
            OUTPUT_VALUE = (
                completion.choices[0].text
                if len(completion.choices) == 1
                else json.dumps([choice.text for choice in completion.choices])
            )
            # vllm specific
            # https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html#extra-parameters-for-completions-api
            if vllm_params:
                guided_json = vllm_params.get("guided_json", None)
                response_format = vllm_params.get("response_format", {"type": "text"})
                if guided_json or response_format["type"] == "json_object":
                    OUTPUT_KIND = OpenInferenceMimeTypeValues.JSON.value

            ground_truth = {"ground_truth": ground_truth} if ground_truth else {}
            metadata = metadata or {}

            top_level_span.set_status(Status(StatusCode.OK))
            top_level_span.set_attributes(
                {
                    SpanAttributes.OUTPUT_MIME_TYPE: OUTPUT_KIND,
                    SpanAttributes.OUTPUT_VALUE: OUTPUT_VALUE,
                    SpanAttributes.LLM_TOKEN_COUNT_TOTAL: completion.usage.total_tokens,
                    SpanAttributes.LLM_TOKEN_COUNT_PROMPT: completion.usage.prompt_tokens,
                    SpanAttributes.LLM_TOKEN_COUNT_COMPLETION: completion.usage.completion_tokens,
                    SpanAttributes.METADATA: json.dumps(
                        {
                            "finish_reason": (
                                completion.choices[0].finish_reason
                                if len(completion.choices) == 1
                                else {
                                    choice.index: choice.finish_reason
                                    for choice in completion.choices
                                }
                            ),
                            **openai_params,
                            **vllm_params,
                            **ground_truth,
                            **metadata,
                        }
                    ),
                }
            )

        return completion

    def __repr__(self):
        return pformat(vars(self))


@contextmanager
def chain(chain_name="chain"):
    """
    ```python
    # dummy example
    with chain("demo_chain") as chain_trace:
        x = "Hello"
        chain_trace.set_text_input(x)
        chain_trace.set_metadata({
            **make_experiment_tracking_metadata("demo_chain"),
            "message": "world"
        })

        res = await llm_call(
        client=client,
        prompt="[INST]Hello[/INST]",
        openai_completion_params={
            "model": CONFIG__MODEL,
            "max_tokens": 200,
        })

        res = get_text(res)

        with chain("sub_chain") as nested_chain_trace:
            nested_chain_trace.set_text_input(res)
            for _ in range(2):
                res = await llm_call(
                client=client,
                prompt=f"[INST]{res}[/INST]",
                openai_completion_params={
                    "model": CONFIG__MODEL,
                    "max_tokens": 200,
                })
                res = get_text(res)
            nested_chain_trace.set_text_output(res)

        chain_trace.set_text_output(res)
    ```
    """
    tracer = get_tracer(CONFIG__TRACER_NAME)
    with tracer.start_as_current_span(chain_name) as chain_span:
        chain_span.set_attributes(
            {
                SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.CHAIN.value,
            }
        )
        yield SpanHandle(chain_span)
        chain_span.set_status(Status(StatusCode.OK))


class SpanHandle:
    def __init__(self, span):
        self.span = span

    def set_text_input(self, input):
        self.span.set_attributes(
            {
                SpanAttributes.INPUT_MIME_TYPE: OpenInferenceMimeTypeValues.TEXT.value,
                SpanAttributes.INPUT_VALUE: str(input),
            }
        )

    def set_json_output(self, output):
        output = output if isinstance(output, str) else json.dumps(output)

        self.span.set_attributes(
            {
                SpanAttributes.OUTPUT_MIME_TYPE: OpenInferenceMimeTypeValues.TEXT.value,
                SpanAttributes.OUTPUT_VALUE: output,
            }
        )

    def set_text_output(self, output):
        self.span.set_attributes(
            {
                SpanAttributes.OUTPUT_MIME_TYPE: OpenInferenceMimeTypeValues.TEXT.value,
                SpanAttributes.OUTPUT_VALUE: str(output),
            }
        )

    def set_metadata(self, metadata):
        self.span.set_attributes({SpanAttributes.METADATA: json.dumps(metadata)})
