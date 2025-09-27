""" Utility functions for platform-specific tasks """

import os
import platform  

def get_default_editor():
    """
    Returns the default text editor for the current platform.
    """
    if platform.system() == "Windows":
        return os.environ.get("EDITOR", "notepad")
    return os.environ.get("EDITOR", "nano")
