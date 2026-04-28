from dataclasses import dataclass


@dataclass
class ParseError:
    """Represents a parsing error encountered during map file loading.

    Attributes:
        line_number: Line number where the error occurred (1-indexed).
        raw_line: The actual line content that caused the error.
        message: Description of the error.
    """
    line_number: int
    raw_line: str
    message: str

    def __str__(self) -> str:
        """Get a formatted string representation of the parse error.

        Returns:
            Formatted error message with line number and context.
        """
        if not self.raw_line.strip():
            return f'Line {self.line_number}: {self.message}'
        return (
            f'Line {self.line_number}: {self.message!r} ← {self.raw_line!r}'
        )
