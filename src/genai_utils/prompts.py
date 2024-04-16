from dataclasses import dataclass, field

from jinja2 import Template
from sklearn.base import BaseEstimator


def template_field(template: str):
    return field(default=template, init=False, repr=False)


@dataclass
class PromptTemplate(BaseEstimator):
    """
    Example:
    ```python
    from genai_utils.day1.prompts import template_field, dataclass, PromptTemplate

    @dataclass
    class BasicPromptTemplate(PromptTemplate):
        template: str = template_field("[INST]{{ instruction }}\n{{ x }}[/INST]")
        instruction: str = ""

    prompt_template = BasicPromptTemplate(instruction="Answer the following user query:")

    prompt = prompt_template("How is the weather today?")
    ```
    """

    template: str = template_field(
        "Please provide a template with `genai_utils.day1.prompts.template_field`.\n"
        "With a field x for the prediction input.\n"
        "Everything else is considered an hyperparameter.\n"
        "Here x = {{ x }}"
    )

    def _render(self, **kwargs):
        return Template(self.template).render(kwargs | vars(self))

    def __call__(self, **kwargs):
        return _Prompt(prompt=self._render(**kwargs), prompt_template=self)

    def get_prompt_params(self):
        """Return all attributes but the template"""
        return {k: v for k, v in vars(self).items() if k != "template"}


@dataclass
class _Prompt:
    prompt: str  # the actual
    prompt_template: PromptTemplate  # this is useful for tracing purposes

    # make this object behave like a simple string
    def __repr__(self):
        return self.prompt

    @property
    def template(self):
        return self.prompt_template.template

    @property
    def template_variables(self):
        return self.prompt_template.get_prompt_params()
