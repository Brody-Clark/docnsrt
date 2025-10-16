import logging
import os
from typing import Optional

LEVELS = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}


def configure_logging(level: Optional[str] = None) -> None:
    """
    Configure root logger. level order: explicit arg > DOCMANCER_LOG_LEVEL env > INFO.
    """
    if level is None:
        level = os.getenv("DOCMANCER_LOG_LEVEL", "INFO")
    level = level.upper()
    if level not in LEVELS:
        level = "INFO"

    root = logging.getLogger()
    root.setLevel(getattr(logging, level))
    # Avoid adding duplicate handlers if called multiple times
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        handler = logging.StreamHandler()
        fmt = "%(asctime)s %(levelname)-7s [%(name)s] %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
        root.addHandler(handler)
    # optional: reduce verbosity of noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)