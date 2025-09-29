"""Models for docstring handling"""

import enum


class DocstringLocation(enum.Enum):
    """Enumeration for docstring locations."""

    INLINE = "inline"
    ABOVE = "above"
    BELOW = "below"
