from dataclasses import dataclass
from typing import List
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class FormattedSummaryModel:
    """Model representing a formatted summary for documentation."""
    start_line: int  # Start line of documentation
    formatted_documentation: List[str]  # Formatted doc string lines
    offset_spaces: int = 0  # Number of spaces to offset formatted_documentation