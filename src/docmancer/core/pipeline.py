"""
Main processing pipeline for documentation generation
"""

from typing import List
from docmancer.models.functional_models import DocstringModel
from docmancer.parser.parser_base import ParserBase
from docmancer.generators.documentation_generators import GeneratorBase
from docmancer.formatter.formatter_base import FormatterBase
from docmancer.core.presenter import Presenter, UserResponse
from docmancer.models.documentation_model import DocumentationModel
from docmancer.models.docstring_models import DocstringLocation
from docmancer.config import DocmancerConfig
from docmancer.utils import file_utils


class DocumentationPipeline:
    """
    Pipeline for processing documentation generation. Parses source code files,
    extracts function context, generates documentation, and presents it to the user.
    """

    def __init__(
        self,
        generator: GeneratorBase,
        parser: ParserBase,
        presenter: Presenter,
        formatter: FormatterBase,
    ):
        self._generator = generator
        self._parser = parser
        self._presenter = presenter
        self._formatter = formatter

    def run(self, settings: DocmancerConfig):
        """
        Runs the documentation generation pipeline.
        """
        errors = []

        # Step 1. Parse all files/functions into {file_path: List[FunctionContextModel]} map
        file_contexts = {}
        files = file_utils.get_files_by_pattern(
            settings.project_dir, settings.files, settings.ignore_files
        )
        for f in files:
            func_contexts = self._parser.parse(
                f, settings.functions, settings.ignore_functions
            )
            file_contexts[f] = func_contexts

        # TODO: implement display message for all function context models that dont
        # have existing docstrings. Make sure existing docstrings are parsed depending on language
        # if settings.check:
        #     self._presenter.display_message()

        # Loop through function context and get formatted docs
        doc_model_database = {}
        for file_path, func_contexts in file_contexts.items():
            for func_context in func_contexts:

                # Step 2. Generate summary for function context
                try:
                    summary = self._generator.get_summary(func_context[0])
                except Exception as e:
                    errors.append(e)
                    continue

                # Step 3. Convert function summary to formatted summary
                formatted_summary = self._formatter.get_formatted_documentation(
                    file_path=file_path,
                    func_context=func_context[0],
                    func_summary=summary,
                )

                # Step 4. Create documentation model database from function context and formatted summary
                doc = DocumentationModel(
                    new_docstring=DocstringModel(
                        lines=formatted_summary.formatted_documentation,
                        start_line=formatted_summary.start_line,
                    ),
                    qualified_name=func_context[0].qualified_name,
                    signature=func_context[0].signature,
                    offset_spaces=formatted_summary.offset_spaces,
                    file_path=file_path,
                    existing_docstring=func_context[0].docstring,
                    docstring_location=formatted_summary.docstring_location,
                )

                if file_path in doc_model_database:
                    doc_model_database[file_path].append(doc)
                else:
                    doc_model_database[file_path] = [doc]

        # Step 5. Present the user with generated docs and get approval if "force-all" is not present
        if not settings.force_all:
            doc_model_database = self.get_approved_docstrings(doc_model_database)

        if doc_model_database:
            # Step 6. Write formatted docstrings to files and save
            self.write_docstrings(errors, doc_model_database)

        if len(errors) > 0:
            for e in errors:
                self._presenter.print_error(f"Error: {e}")
        else:
            self._presenter.clear_console()
            self._presenter.print_success("Documentation Generation Complete")

    def write_docstrings(self, errors, doc_model_database):
        """
        Writes the generated docstrings to the appropriate files.
        """
        for file_path, doc_models in doc_model_database.items():
            if len(doc_models) > 0:
                try:
                    self.commit(file_path=file_path, docs=doc_models)
                except Exception as e:
                    errors.append(e)

    def get_approved_docstrings(self, doc_model_database):
        """
        Gets user approval for the generated docstrings.
        """
        for file_path, doc_models in doc_model_database.copy().items():
            approved_docs = []
            while doc_models:
                doc = doc_models.pop()
                approval_response = self._presenter.get_user_approval(doc)
                if approval_response.response == UserResponse.QUIT:
                    return None
                if approval_response.response == UserResponse.SKIP:
                    continue
                if approval_response.response == UserResponse.ACCEPT:
                    approved_docs.append(doc)
            doc_model_database[file_path] = approved_docs
        return doc_model_database

    def commit(self, file_path: str, docs: List[DocumentationModel]):
        """
        Commits the generated documentation to the specified file.
        """

        # Sort docs by start_line and write to files
        # Read the file into memory
        with open(file_path, "r", encoding="utf-8") as f:
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
            
            # If docstring is above the function, adjust the line to insert at if lines were removed
            if doc.docstring_location == DocstringLocation.ABOVE:
                adjusted_line = max(0, adjusted_line - removed_lines)
            
            lines[adjusted_line:adjusted_line] = list(indented_documentation)

            offset += len(doc.new_docstring.lines) - removed_lines

        # Write modified lines back to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
