import os
from pathlib import Path
from typing import Any, Type

from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import (
    BaseOutputParser,
    JsonOutputParser,
    StrOutputParser,
)
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables import RunnableSerializable
from openai import APIStatusError
from pydantic import BaseModel

from src.utils.step import Step


class PromptTemplates(BaseModel):
    """The prompt templates for the LLM extension."""

    system_prompt: str | None = None
    """The system message template"""
    user_prompt: str | None = None
    """The user message template"""

    def to_dict(self) -> dict:
        """Convert the prompt templates to a dictionary representation.

        Returns:
            dict: the dictionary representation of the prompt templates.
        """
        return dict(self)


class GptBase(Step):

    def __init__(self, config, context):

        super().__init__(config=config, context=context)

    def _bind_function_calling(self):
        raise NotImplementedError()

    def _bind_json_mode(self):
        self._llm = self._llm.bind(response_format={"type": "json_object"})

    async def run(self, run_input: dict | BaseModel) -> LLMExtractionResult:
        """Runs the LLM extraction extension.

        Args:
            run_input (dict | BaseModel): the input data for the extension.

        Returns:
            LLMExtractionResult: the extraction result.
        """
        chain_kwargs = self._get_chain_args(run_input)

        if self._request_format == _RequestFormatMode.FUNCTION_CALLING:
            self._bind_function_calling()
            chain_kwargs["_format"] = ""
        else:
            chain_kwargs["_format"] = self._get_format_instructions()
            if self._request_format == _RequestFormatMode.JSON:
                self._bind_json_mode()

        chain = self._chat_prompt_template | self._llm | self._output_parser()
        output = await self._run_chain(chain, chain_kwargs)
        answer, details = self._get_answer_and_details(output, run_input)
        prompt = self._chat_prompt_template.format_prompt(**chain_kwargs).to_string()
        response = self.build_response(answer, details, prompt)
        return response

    def _get_chain_args(self, run_input: dict | BaseModel) -> dict[str, Any]:
        if isinstance(run_input, dict):
            return run_input.copy()
        elif isinstance(run_input, BaseModel):
            return run_input.model_dump()
        raise ValueError(f"Run input type is not supported: {run_input}")

    def _get_format_instructions(self) -> str:
        return ""

    def _get_prompt_template(self) -> ChatPromptTemplate:
        """
        Gets the prompt template that is used to create the chain.

        Returns:
            ChatPromptTemplate: template to be used in the chain
        """

        messages_templates = []
        if self._system_prompt_template:
            messages_templates.append(
                SystemMessagePromptTemplate.from_template(self._system_prompt_template)
            )
        if self._user_prompt_template:
            messages_templates.append(
                HumanMessagePromptTemplate.from_template(self._user_prompt_template)
            )

        return ChatPromptTemplate.from_messages(messages_templates)

    def _get_prompt_template_from_file(
        self, template_path: Path | None, default_template_name: str
    ) -> str | None:
        # 1. Relative path
        if self._extension_path and template_path:
            return read_prompt_file(self._extension_path.parent / template_path)

        # 2. Absolute path
        if template_path:
            return read_prompt_file(template_path)

        # 3. Try default path
        if self._extension_path:
            try:
                return read_prompt_file(
                    self._extension_path.parent / default_template_name
                )
            except FileNotFoundError:
                return None

        return None

    def _get_prompt_templates_from_file(
        self, extension_input: LLMExtractionBuildInput
    ) -> PromptTemplates:
        system_prompt = self._get_prompt_template_from_file(
            extension_input.system_template_path, "system_template.md"
        )
        user_prompt = self._get_prompt_template_from_file(
            extension_input.user_template_path, "user_template.md"
        )

        if not (system_prompt or user_prompt):
            raise ValueError(
                "No prompt provided. To use default prompt templates,\
                add `_extension_path = pathlib.Path(__file__)` to your extension"
            )

        return PromptTemplates(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )


def read_prompt_file(path: Path) -> str:
    """Get the content of a file as a string.

    Args:
        path (Path): The path to the file.

    Raises:
        FileNotFoundError: If the file does not exist or is a directory

    Returns:
        str: The content of the file
    """
    if os.path.isdir(path):
        raise FileNotFoundError(f"Provided path {str(path)} is a directory, not a file")
    if os.path.exists(path):
        with open(path, "r") as fp:
            return fp.read()

    raise FileNotFoundError(f"Missing file {path} in path {str(path)}")
