"""
Main entry point for the docnsrt application.
"""

import os
import logging
from docnsrt.core.cli import parse_args
from docnsrt.core.pipeline import DocumentationPipeline
from docnsrt.core.generator import DocstringGenerator
from docnsrt.formatter.formatter_factory import FormatterFactory
from docnsrt.core.presenter import Presenter
from docnsrt.core.logging_config import configure_logging
from docnsrt.parsers.parser_factory import ParserFactory
from docnsrt.config import DocnsrtConfig

logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for the docnsrt application.
    """
    config: DocnsrtConfig = parse_args()

    configure_logging(config.log_level)

    if not os.path.isdir(config.project_dir):
        raise FileNotFoundError("Project directory does not exist.")

    presenter = Presenter()
    generator = DocstringGenerator()
    formatter_factory = FormatterFactory()
    formatter = formatter_factory.get_formatter(
        style=config.style, language=config.language
    )
    parser_factory = ParserFactory()
    parser = parser_factory.get_parser(language=config.language)

    documentation_pipeline = DocumentationPipeline(
        generator=generator, formatter=formatter, presenter=presenter, parser=parser
    )

    documentation_pipeline.run(config)


if __name__ == "__main__":
    main()
