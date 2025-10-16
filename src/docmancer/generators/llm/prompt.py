"""
This module contains the prompt class for providing prompts to the LLM summary generator.
"""
import logging
from typing import List
from pathlib import Path
import yaml
from docmancer.models.function_context import FunctionContextModel
from docmancer.models.function_summary import FunctionSummaryModel
from docmancer.models.functional_models import ParameterModel, ExceptionModel

logger = logging.getLogger(__name__)

class Prompt:
    """LLM Prompt class for generating prompts based on function context."""

    def __init__(self):
        self._prompt_template = self._load_prompt_template()

    def create(self, context: FunctionContextModel) -> str:
        """Creates a prompt for the LLM based on the function context.

        Args:
            context (FunctionContextModel): The context of the function being documented.

        Returns:
            str: The generated prompt for the LLM.
        """
        # At runtime, inject values
        prompt = self._prompt_template.format(
            signature=context.signature,
            preceding_comments=self._get_leading_comments_str(
                context.docstring.lines if context.docstring else []
            ),
            qualified_name=context.qualified_name,
            body=context.body,
            expected_json_format=self._get_expected_json_format(),
        )

        return prompt

    def _get_leading_comments_str(self, comments: List[str]) -> str:
        comment = ""
        if comments:
            comment = "\n".join(comments)
        return comment

    def _get_expected_json_format(self):

        model = FunctionSummaryModel(
            summary="A summary of what the function does based on its definition.",
            parameters=[
                ParameterModel(
                    name="parameter", type="type", desc="description of parameter"
                )
            ],
            return_description="A description of the return value if there is one.",
            remarks="A remark about usage if necessary.",
            exceptions=[ExceptionModel(type="type", desc="description of exception")],
            return_type="Type of return value",
        )
        return model.to_json(indent=2)

    def _load_prompt_template(self) -> str:
        try:
            with open(Path("prompt.yaml"), encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            logger.exception("No valid prompt.yaml file found for LLM.")

        prompt_template = config["prompt_template"]
        return prompt_template
