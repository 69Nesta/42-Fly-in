from dataclasses import dataclass


@dataclass
class ParseError:
    line_number: int
    raw_line: str
    message: str

    def __str__(self) -> str:
        return (
            f'Line {self.line_number}: {self.message!r}  ← {self.raw_line!r}'
        )
