from .errors import (
    FileNotFoundError as _FileNotFoundError,
    PermissionError as _PermissionError,
    NotAFileError,
    ParseError
)
from pydantic import BaseModel, Field, PrivateAttr, ValidationError
from dataclasses import dataclass, field
from .utils import Color, Logger
from typing import ClassVar
from .Hub import Hub
import re


@dataclass
class ParseResult:
    nb_drones: int = 0
    hubs: list[Hub] = field(default_factory=list)
    errors: list[ParseError] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


class MapLoader(BaseModel):
    filepath: str = Field()
    verbose: bool = Field(default=False)

    _RE_NB_DRONES: ClassVar[re.Pattern] = re.compile(r'^nb_drones:\s*(\d+)$')
    _RE_HUB: ClassVar[re.Pattern] = re.compile(r'^(start_hub|end_hub|hub):')
    _RE_CONNECTION: ClassVar[re.Pattern] = re.compile(r'^connection:\s*')

    _logger: Logger = PrivateAttr()
    _result: ParseResult = PrivateAttr()

    @property
    def nb_drones(self) -> int:
        return self._result.nb_drones

    @property
    def hubs(self) -> list[Hub]:
        return self._result.hubs

    @property
    def errors(self) -> list[ParseError]:
        return self._result.errors

    def model_post_init(self, context) -> None:
        self._logger = Logger(
            ACTIVE=self.verbose,
            name='MapLoader',
            color=Color.CYAN
        )
        self._result = ParseResult()

        try:
            self._load()
        except FileNotFoundError:
            raise _FileNotFoundError(self.filepath)
        except PermissionError:
            raise _PermissionError(self.filepath)
        except IsADirectoryError:
            raise NotAFileError(self.filepath)

        if not self._result.ok:
            for err in self._result.errors:
                self._logger.error(str(err))

        return super().model_post_init(context)

    def _load(self) -> None:
        with open(self.filepath, 'r') as f:
            raw: str = f.read()

        lines: list[tuple[int, str]] = self._strip_comments(raw)
        if not lines:
            self._result.errors.append(ParseError(0, '', 'File is empty'))
            return

        index: int = 0
        index = self._parse_nb_drones(lines, index)
        index = self._parse_hubs(lines, index)

        self._parse_connections(lines, index)

    def _strip_comments(self, data: str) -> list[tuple[int, str]]:
        result: list[tuple[int, str]] = []
        for lineno, raw in enumerate(data.splitlines(), start=1):
            cleaned = raw.split('#')[0].strip()
            if cleaned:
                result.append((lineno, cleaned))
        return result

    def _parse_nb_drones(self, lines: list[tuple[int, str]], index: int) -> int:
        lineno, line = lines[index]
        match = self._RE_NB_DRONES.match(line)
        if not match:
            self._result.errors.append(ParseError(
                lineno, line,
                f'Expected \'nb_drones: <int>\', got {line!r}'
            ))
        else:
            self._result.nb_drones = int(match.group(1))
        return index + 1

    def _parse_hubs(self, lines: list[tuple[int, str]], index: int) -> int:
        while index < len(lines):
            lineno, line = lines[index]
            if not self._RE_HUB.match(line):
                break
            try:
                hub = Hub.from_str(line)
                self._result.hubs.append(hub)
            except ValueError as e:
                self._result.errors.append(ParseError(lineno, line, str(e)))
            except ValidationError as e:
                for err in e.errors():
                    loc = ' → '.join(str(_loc) for _loc in err['loc'])
                    msg = err.get('ctx', {}).get('error') or err['msg']
                    self._result.errors.append(ParseError(
                        lineno, line, f'[{loc}] {msg}'
                    ))
            index += 1
        return index

    def _parse_connections(self, lines: list[tuple[int, str]], index: int) -> None:
        while index < len(lines):
            lineno, line = lines[index]
            if not self._RE_CONNECTION.match(line):
                self._result.errors.append(ParseError(
                    lineno, line,
                    f'Unexpected line outside known sections: {line!r}'
                ))

            # TODO: add logic for parsing connectios

            index += 1
