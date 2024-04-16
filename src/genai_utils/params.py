from dataclasses import dataclass
from typing import Literal, Optional, TypedDict


class ResponseFormat(TypedDict):
    type: Literal["json_object"] | Literal["text"]


class Params:
    def get_params(self):
        return {k: v for k, v in vars(self).items() if v is not None}

    def set_params(self, **params):
        self.__dict__ |= params
        return self


def params_to_dict(params: Params | dict | None):
    return (getattr(params, "get_params", lambda: {})() or params or {}).copy()


@dataclass
class vLLMExtraCompletionParams(Params):
    use_beam_search: Optional[bool] = None
    top_k: Optional[int] = None
    min_p: Optional[float] = None
    repetition_penalty: Optional[float] = None
    length_penalty: Optional[float] = None
    early_stopping: Optional[bool] = None
    stop_token_ids: Optional[list[int]] = None
    ignore_eos: Optional[bool] = None
    min_tokens: Optional[int] = None
    skip_special_tokens: Optional[bool] = None
    spaces_between_special_tokens: Optional[bool] = None
    include_stop_str_in_output: Optional[bool] = None
    response_format: Optional[ResponseFormat] = None
    guided_json: Optional[str | dict] = None
    guided_regex: Optional[str] = None
    guided_choice: Optional[list[str]] = None
    guided_grammar: Optional[str] = None

    def __repr__(self):
        return (
            self.__class__.__name__
            + "("
            + ", ".join(
                [f"{k}={v}" for k, v in vars(self).items() if v is not None]
            )
            + ")"
        )


@dataclass
class OpenAICompletionParams(Params):
    # Ordered by official OpenAI API documentation
    # https://platform.openai.com/docs/api-reference/completions/create
    # The completion API is branded as legacy but legacy in LLM-lingo means stable.
    model: Optional[str] = None
    best_of: Optional[int] = None
    echo: Optional[bool] = None
    frequency_penalty: Optional[float] = None
    logit_bias: Optional[dict[str, float]] = None
    logprobs: Optional[int] = None
    max_tokens: Optional[int] = None
    n: Optional[int] = None
    presence_penalty: Optional[float] = None
    seed: Optional[int] = None
    stop: Optional[str | list[str]] = None
    stream: Optional[bool] = None
    suffix: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    user: Optional[str] = None

    def __repr__(self):
        return (
            self.__class__.__name__
            + "("
            + ", ".join(
                [f"{k}={v}" for k, v in vars(self).items() if v is not None]
            )
            + ")"
        )
