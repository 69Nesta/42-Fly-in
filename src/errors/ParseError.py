from dataclasses import dataclass


@dataclass
class ParseError:
    line_number: int
    raw_line: str
    message: str

    def __str__(self) -> str:
        if not self.raw_line.strip():
            return f'Line {self.line_number}: {self.message}'
        return (
            f'Line {self.line_number}: {self.message!r} ← {self.raw_line!r}'
        )
