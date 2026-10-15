"""Lemqo: an explicit certificate checker for propositional natural deduction."""

__version__ = "0.3.0"

from .api import verify_bytes
from .errors import Rejection

__all__ = ["Rejection", "__version__", "verify_bytes"]
