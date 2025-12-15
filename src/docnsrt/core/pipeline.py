"""
Main processing pipeline for documentation generation
"""

import logging
import os
from typing import List
from docnsrt.core.models import (
    WritableFileModel,
    DocstringPresentationModel,
    DocstringModel,
    FileProcessingContextModel,
)
from docnsrt.parsers.parser_base import ParserBase
from docnsrt.core.generator import DocstringGenerator
from docnsrt.formatter.formatter_base import FormatterBase
from docnsrt.core.presenter import Presenter, UserResponse
from docnsrt.core.models import DocstringLocation
from docnsrt.config import DocnsrtConfig
from docnsrt.utils import file_utils
from docnsrt.core.languages import SupportedFileExtensions
import portalocker

logger = logging.getLogger(__name__)


class DocumentationPipeline:
    """
    Pipeline for processing documentation generation. Parses source code files,
    extracts function context, generates docstring template, and presents it to the user.
    """

    def __init__(
        self,
        generator: DocstringGenerator,
        parser: ParserBase,
        presenter: Presenter,
        formatter: FormatterBase,
    ):
        self._generator = generator
        self._parser = parser
        self._presenter = presenter
        self._formatter = formatter

    def run(self, settings: DocnsrtConfig):
        """
        Runs the documentation generation pipeline.
        """
        errors = []

        # Step 1. Parse all files/functions into {file_path: List[FunctionContextModel]} map
        file_contexts = {}
        files = file_utils.get_files_by_pattern(
            settings.project_dir,
            settings.files,
            settings.ignore_files,
            SupportedFileExtensions[settings.language],
        )
        for f in files:
            func_contexts = self._parser.parse(
                f, settings.functions, settings.ignore_functions
            )
            stat = os.stat(f)
            mtime = stat.st_mtime
            size = stat.st_size
            f = WritableFileModel(
                file_path=f, last_time_modified=mtime, last_size_bytes=size
            )

            file_context = FileProcessingContextModel(
                file=f, functions=func_contexts, docstrings=[]
            )

            # TODO: implement display message for all function context models that dont
            # have existing docstrings. Make sure existing docstrings are parsed depending on language
            # if settings.check:
            #     self._presenter.display_message()

            # Loop through function context and get formatted docs
            if not file_context.functions:
                continue
            for func_context in file_context.functions:

                # Step 2. Generate summary for function context
                try:
                    docstring_template_values = self._generator.get_template_values(
                        func_context
                    )
                except Exception as e:
                    errors.append(e)
                    continue

                # Step 3. Convert function summary to formatted summary
                formatted_docstring = self._formatter.get_formatted_docstring(
                    file_path=file_context.file.file_path,
                    func_context=func_context,
                    template_values=docstring_template_values,
                )

                # Step 4. Create documentation model database from function context and formatted summary
                doc = DocstringPresentationModel(
                    new_docstring=DocstringModel(
                        lines=formatted_docstring.formatted_documentation,
                        start_line=formatted_docstring.start_line,
                    ),
                    qualified_name=func_context.qualified_name,
                    signature=func_context.signature,
                    offset_spaces=formatted_docstring.offset_spaces,
                    file_path=file_context.file.file_path,
                    existing_docstring=func_context.docstring,
                    docstring_location=formatted_docstring.docstring_location,
                )

                file_context.docstrings.append(doc)
            # Step 5. Present the user with generated docs and get approval if "force-all" is not present
            if not settings.force_all:
                file_context.docstrings = self.get_approved_docstrings(
                    file_context.docstrings
                )

            if file_context.docstrings is not None and len(file_context.docstrings) > 0:
                # Step 6. Write formatted docstrings to files and save
                self.write_docstrings(errors, file_context)

        if len(errors) > 0:
            for e in errors:
                self._presenter.print_error(f"Error: {e}")
        else:
            self._presenter.clear_console()
            self._presenter.print_success("Docstrings written succesfully")

    def write_docstrings(self, errors, file_context: FileProcessingContextModel):
        """
        Writes the generated docstrings to the appropriate files.
        """
        if len(file_context.docstrings) > 0:
            try:
                self.commit(
                    file_path=file_context.file.file_path,
                    docs=file_context.docstrings,
                    orig_mtime=file_context.file.last_time_modified,
                    orig_size=file_context.file.last_size_bytes,
                )
            except Exception as e:
                errors.append(e)

    def get_approved_docstrings(
        self, docstring_models: List[DocstringPresentationModel]
    ) -> FileProcessingContextModel:
        """
        Gets user approval for the generated docstrings.
        """
        approved_docs = []
        while docstring_models:
            doc = docstring_models.pop()
            approval_response = self._presenter.get_user_approval(doc)
            if approval_response.response == UserResponse.QUIT:
                return None
            if approval_response.response == UserResponse.SKIP:
                continue
            if approval_response.response == UserResponse.ACCEPT:
                approved_docs.append(doc)
        return approved_docs

    def commit(
        self,
        file_path: str,
        docs: List[DocstringPresentationModel],
        orig_mtime: float,
        orig_size: int,
    ):
        """
        Commits the generated documentation to the specified file.
        """

        logger.debug(f"Writing {len(docs)} docstrings to file {file_path}")

        # Sort docs by start_line and write to files
        # Read the file into memory
        with open(file_path, "r+", encoding="utf-8") as f:
            portalocker.lock(f, portalocker.LOCK_EX)

            # Detect external changes
            st = os.stat(file_path)
            if st.st_mtime != orig_mtime or st.st_size != orig_size:
                logger.error(
                    f"File {file_path} changed externally (mtime or size mismatch)"
                )
                raise RuntimeError(f"File {file_path} changed externally")
            lines = f.readlines()

            # Sort insertions by line number (ascending)
            docs.sort(key=lambda x: x.new_docstring.start_line)

            offset = 0
            for doc in docs:

                adjusted_line = doc.new_docstring.start_line + offset

                # Remove existing docstring if there is one
                removed_lines = 0
                if doc.existing_docstring:
                    start_line = doc.existing_docstring.start_line + offset
                    end_line = start_line + len(doc.existing_docstring.lines)
                    del lines[start_line:end_line]
                    removed_lines = len(doc.existing_docstring.lines)

                # Write the docstring to the appropriate location
                indented_documentation = [
                    " " * doc.offset_spaces + doc_line
                    for doc_line in doc.new_docstring.lines
                ]
                logger.debug(
                    f"Inserting docstring at line {adjusted_line} in file {file_path}"
                )

                # If docstring is above the function, adjust the line to insert at for removed lines
                if doc.docstring_location == DocstringLocation.ABOVE:
                    adjusted_line = max(0, adjusted_line - removed_lines)

                lines[adjusted_line:adjusted_line] = list(indented_documentation)

                offset += len(doc.new_docstring.lines) - removed_lines

            # Write the modified lines back to the file
            f.writelines(lines)
        portalocker.unlock(f)
        logger.info(f"Wrote {len(docs)} docstrings to file {file_path}")
