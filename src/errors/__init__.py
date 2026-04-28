"""Custom exception hierarchy for Fly-In application.

Defines application-specific errors:
- FlyInError: Base exception for all Fly-In errors
- FileError: File I/O errors (not found, permission, not a file)
- ParseError: Level file parsing errors
"""

from .FlyInError import FlyInError
from .FileError import (
    FileError,
    FileNotFoundError,
    PermissionError,
    NotAFileError
)
from .ParseError import ParseError

__all__: list[str] = [
    'FlyInError',
    'FileError',
    'FileNotFoundError',
    'PermissionError',
    'NotAFileError',
    'ParseError'
]
