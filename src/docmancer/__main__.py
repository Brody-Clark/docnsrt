"""
Main entry point for the Docmancer application.
"""

import os
import sys
import logging
from docmancer.core.cli import parse_args
from docmancer.core.pipeline import DocumentationPipeline
from docmancer.generators.documentation_generators import (
    DefaultGenerator,
    LlmGenerator,
    GeneratorBase,
)
from docmancer.generators.llm.llm_agent_factory import LlmFactory
from docmancer.formatter.formatter_factory import FormatterFactory
from docmancer.core.presenter import Presenter
from docmancer.core.logging_config import configure_logging
from docmancer.parser.parser_factory import ParserFactory, ParserBase
from docmancer.config import DocmancerConfig, LLMType

logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for the Docmancer application.
    """
    config: DocmancerConfig = parse_args()

    configure_logging(config.log_level)

    if not os.path.isdir(config.project_dir):
        raise FileNotFoundError("Project directory does not exist.")

    try:

        # Accessing config settings
        llm_config = config.llm_config
        if not llm_config:
            raise ValueError("LLM configuration is missing in the config file.")
        llm_mode_enum = llm_config.get_mode_enum()

        logger.info(f"\nLLM Mode: {llm_mode_enum.value} (Enum: {llm_mode_enum.name})")
        logger.info(f"  Temperature: {llm_config.temperature}")
        logger.info(f"  Max Tokens per Response: {llm_config.max_tokens_per_response}")

        if llm_mode_enum == LLMType.LOCAL:
            if not llm_config.local:
                raise ValueError(
                    "Config error: 'local' settings missing for LOCAL mode."
                )
            local_settings = llm_config.local
            logger.info(f"  Model Path: {local_settings.model_path}")
            logger.info(f"  GPU Layers: {local_settings.n_gpu_layers}")
            # Use these settings to initialize the local LLM agent
            # llm_agent = LLMAgent(mode=llm_mode_enum, config=local_settings)

        elif llm_mode_enum == LLMType.REMOTE_API:
            if not llm_config.remote_api:
                raise ValueError(
                    "Config error: 'remote_api' settings missing for REMOTE_API mode."
                )
            remote_settings = llm_config.remote_api
            logger.info(f"  Endpoint: {remote_settings.api_endpoint}")
            logger.info(f"  Provider: {remote_settings.provider}")
            logger.info(f"  Track Tokens/Cost: {remote_settings.track_tokens_and_cost}")

            if remote_settings.track_tokens_and_cost:
                logger.info(
                    f"  User Max Prompt Tokens: {llm_config.max_tokens_per_response}"
                )

    except (FileNotFoundError, ValueError, RuntimeError, TypeError) as e:
        logger.exception(f"Configuration error: {e}", file=sys.stderr)
        logger.error("You will not be able to use LLM-based features.", file=sys.stderr)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

    presenter = Presenter()

    generator = get_generator(config)

    formatter_factory = FormatterFactory()
    formatter = formatter_factory.get_formatter(
        style=config.style, language=config.language
    )

    parser = get_parser(language=config.language)

    documentation_pipeline = DocumentationPipeline(
        generator=generator, formatter=formatter, presenter=presenter, parser=parser
    )

    documentation_pipeline.run(config)


def get_generator(config: DocmancerConfig) -> GeneratorBase:
    """Get the appropriate generator based on the configuration.

    Args:
        config (DocmancerConfig): The configuration for the Docmancer application.

    Returns:
        GeneratorBase: The appropriate generator for the documentation generation.
    """
    if config.no_summary:
        generator = DefaultGenerator()
    else:
        try:
            agent_factory = LlmFactory()
            agent = agent_factory.get_agent(llm_config=config.llm_config)
        except NotImplementedError as e:
            logger.exception(f"Error determining LLM agent type: {e}")
        generator = LlmGenerator(agent=agent)
    return generator


def get_parser(language: str) -> ParserBase:
    """Get the appropriate parser based on the language.

    Args:
        language (str): The programming language for the documentation.

    Returns:
        ParserBase: The appropriate parser for the specified language.
    """
    parser_factory = ParserFactory()
    return parser_factory.get_parser(language=language)


if __name__ == "__main__":
    main()
