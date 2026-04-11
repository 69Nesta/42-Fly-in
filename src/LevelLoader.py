from .errors import (
    FileNotFoundError as _FileNotFoundError,
    PermissionError as _PermissionError,
    NotAFileError,
    ParseError
)
from pydantic import BaseModel, Field, PrivateAttr, ValidationError
from .Connections import Connections, Connection
from dataclasses import dataclass, field
from typing import ClassVar, Any
from .utils import Color, Logger
from .Hub import Hub, HubType
import re


t_re = re.Pattern[str]


@dataclass
class ParseResult:
    nb_drones: int = 0
    hubs: dict[str, Hub] = field(default_factory=dict)
    errors: list[ParseError] = field(default_factory=list)
    connections: Connections = field(default_factory=Connections)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


class LevelLoader(BaseModel):
    filepath: str = Field()
    verbose: bool = Field(default=False)

    _RE_NB_DRONES: ClassVar[t_re] = re.compile(r'^nb_drones:\s*(\d+)$')
    _RE_HUB: ClassVar[t_re] = re.compile(r'^(start_hub|end_hub|hub):')
    _RE_CONNECTION: ClassVar[t_re] = re.compile(r'^connection:\s*')

    _logger: Logger = PrivateAttr()
    _result: ParseResult = PrivateAttr()

    @property
    def nb_drones(self) -> int:
        return self._result.nb_drones

    @property
    def hubs(self) -> dict[str, Hub]:
        return self._result.hubs

    @property
    def connections(self) -> Connections:
        return self._result.connections

    @property
    def errors(self) -> list[ParseError]:
        return self._result.errors

    def model_post_init(self, context: Any) -> None:
        self._logger = Logger(
            print_log=self.verbose,
            name='LevelLoader',
            color=Color.YELLOW
        )
        self._result = ParseResult()
        self._logger.log(f'Loading level from {self.filepath!r}...')

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
                self._logger.error(f'{err}')

        if not self._result.ok:
            raise ValueError(
                f'Failed to load map from {self.filepath!r} with '
                f'{len(self._result.errors)} error(s)'
            )

        self._logger.log(
            f'Level loaded successfully with {self.nb_drones} drones, '
            f'{len(self.hubs)} hubs and {len(self.connections.all)} '
            'connections.'
        )

        return super().model_post_init(context)

    def _check_map_validity(self) -> None:
        start_hubs = [
            hub for hub in self.hubs.values() if hub.type == HubType.START_HUB
        ]
        end_hubs = [
            hub for hub in self.hubs.values() if hub.type == HubType.END_HUB
        ]
        if not start_hubs:
            self._result.errors.append(ParseError(
                0, '',
                'Map must contain at least one start_hub'
            ))
        if not end_hubs:
            self._result.errors.append(ParseError(
                0, '',
                'Map must contain at least one end_hub'
            ))

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

        self._check_map_validity()

    def _strip_comments(self, data: str) -> list[tuple[int, str]]:
        result: list[tuple[int, str]] = []
        for lineno, raw in enumerate(data.splitlines(), start=1):
            cleaned = raw.split('#')[0].strip()
            if cleaned:
                result.append((lineno, cleaned))
        return result

    def _parse_nb_drones(
                self,
                lines: list[tuple[int, str]],
                index: int
            ) -> int:
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
            if (not self._RE_HUB.match(line)
               and self._RE_CONNECTION.match(line)):
                break
            try:
                hub = Hub.from_str(line)
                if self.hubs.get(hub.name):
                    self._result.errors.append(ParseError(
                        lineno, line, 'Hub name must be unique, got duplicate'
                        f' name {hub.name!r}'
                    ))
                self.hubs.update({
                    hub.name: hub
                })
            except ValidationError as e:
                for err in e.errors():
                    loc = ' → '.join(str(_loc) for _loc in err['loc'])
                    msg = err.get('ctx', {}).get('error') or err['msg']
                    self._result.errors.append(ParseError(
                        lineno, line, f'[{loc}] {msg}'
                    ))
            except ValueError as e:
                self._result.errors.append(ParseError(lineno, line, str(e)))
            index += 1
        return index

    def _parse_connections(
                self,
                lines: list[tuple[int, str]],
                index: int
            ) -> None:
        while index < len(lines):
            lineno, line = lines[index]
            if not self._RE_CONNECTION.match(line):
                self._result.errors.append(ParseError(
                    lineno, line,
                    f'Unexpected line outside known sections: {line!r}'
                ))

            try:
                self._result.connections.add(
                    Connection.from_str(line, self.hubs)
                )
            except ValueError as e:
                self._result.errors.append(ParseError(lineno, line, str(e)))

            index += 1
