"""Model for function documentation."""

from dataclasses import dataclass
from typing import Optional
from dataclasses_json import dataclass_json
from docmancer.models.functional_models import DocstringModel
from docmancer.models.docstring_models import DocstringLocation


@dataclass_json
@dataclass
class DocumentationModel:
    """Model for function writable documentation."""

    qualified_name: str  # Full function name. e.g., module.Class.method
    signature: str  # Full function signature
    new_docstring: Optional[DocstringModel] = (
        None  # New docstring to replace the existing one
    )
    offset_spaces: int = 0  # Number of spaces to offset formatted_documentation
    file_path: Optional[str] = None  # Relative file path
    existing_docstring: Optional[DocstringModel] = None  # If present
    docstring_location: DocstringLocation = (
        DocstringLocation.INLINE
    )  # Location of the docstring
