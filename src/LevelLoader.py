from .errors import (
    FileNotFoundError as _FileNotFoundError,
    PermissionError as _PermissionError,
    NotAFileError,
    ParseError
)
from pydantic import BaseModel, Field, PrivateAttr, ValidationError
from .Connections import Connections, Connection
from .utils import Color, Logger, MathUtils
from dataclasses import dataclass, field
from typing import ClassVar, Any
from .Hub import Hub, HubType
import re


t_re = re.Pattern[str]


@dataclass
class ParseResult:
    """Result of parsing a map file.

    Attributes:
        nb_drones: Number of drones from the map.
        hubs: Dictionary of all parsed hubs.
        errors: List of parsing errors encountered.
        connections: All parsed connections.
    """
    nb_drones: int = 0
    hubs: dict[str, Hub] = field(default_factory=dict)
    errors: list[ParseError] = field(default_factory=list)
    connections: Connections = field(default_factory=Connections)

    @property
    def ok(self) -> bool:
        """Check if parsing was successful.

        Returns:
            True if no errors occurred during parsing, False otherwise.
        """
        return len(self.errors) == 0


class LevelLoader(BaseModel):
    """Loads and parses map files to create Level objects.

    Attributes:
        filepath: Path to the map file to load.
        verbose: Whether to enable verbose logging.
    """
    filepath: str = Field()
    verbose: bool = Field(default=False)

    _RE_NB_DRONES: ClassVar[t_re] = re.compile(r'^nb_drones:\s*(\d+)$')
    _RE_HUB: ClassVar[t_re] = re.compile(r'^(start_hub|end_hub|hub):')
    _RE_CONNECTION: ClassVar[t_re] = re.compile(r'^connection:\s*')

    _logger: Logger = PrivateAttr()
    _result: ParseResult = PrivateAttr()

    @property
    def nb_drones(self) -> int:
        """Get the number of drones.

        Returns:
            Number of drones from the parsed map.
        """
        return self._result.nb_drones

    @property
    def hubs(self) -> dict[str, Hub]:
        """Get all hubs.

        Returns:
            Dictionary of hubs indexed by name.
        """
        return self._result.hubs

    @property
    def connections(self) -> Connections:
        """Get all connections.

        Returns:
            Connections container with all connections.
        """
        return self._result.connections

    @property
    def errors(self) -> list[ParseError]:
        """Get all parsing errors.

        Returns:
            List of ParseError objects encountered during loading.
        """
        return self._result.errors

    def model_post_init(self, context: Any) -> None:
        """Initialize the loader after model creation.

        Loads and parses the map file.

        Args:
            context: Pydantic context parameter.

        Raises:
            FileNotFoundError: If the map file doesn't exist.
            PermissionError: If there's no permission to read the file.
            NotAFileError: If the path is a directory.
            ValueError: If parsing produces errors.
        """
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
        """Validate that the map has required start and end hubs.

        Appends errors to _result if validation fails.
        """
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
        if len(start_hubs) > 1:
            self._result.errors.append(ParseError(
                0, '',
                'Map must contain at most one start_hub, got '
                f'{len(start_hubs)}'
            ))
        if len(end_hubs) > 1:
            self._result.errors.append(ParseError(
                0, '',
                f'Map must contain at most one end_hub, got {len(end_hubs)}'
            ))

    def _load(self) -> None:
        """Load and parse the map file.

        Reads the file and parses drones, hubs, and connections sections.
        """
        with open(self.filepath, 'r') as f:
            raw: str = f.read()

        lines: list[tuple[int, str]] = self._strip_comments(raw)
        if not lines:
            self._result.errors.append(ParseError(0, '', 'File is empty'))
            return

        index: int = 0
        index = self._parse_nb_drones(lines, index)
        index = self._parse_hubs(lines, index)

        if (self._result.ok):
            self._parse_connections(lines, index)

        self._check_map_validity()
        self._update_hubs_capacities()

    def _update_hubs_capacities(self) -> None:
        """Update start/end hub capacities if needed.

        Ensures start and end hubs can accommodate all drones.
        """
        for hub in self.hubs.values():
            if hub.is_start() and hub.metadata.max_drones < self.nb_drones:
                self._logger.warning(
                    f'Start hub {hub.name!r} has max_drones='
                    f'{hub.metadata.max_drones}, but nb_drones='
                    f'{self.nb_drones}. Updating max_drones to '
                    f'{self.nb_drones}.'
                )
                hub.metadata.max_drones = self.nb_drones
            elif hub.is_end() and hub.metadata.max_drones < self.nb_drones:
                self._logger.warning(
                    f'End hub {hub.name!r} has max_drones='
                    f'{hub.metadata.max_drones}, but nb_drones='
                    f'{self.nb_drones}. Updating max_drones to '
                    f'{self.nb_drones}.'
                )
                hub.metadata.max_drones = self.nb_drones

    def _strip_comments(self, data: str) -> list[tuple[int, str]]:
        """Strip comments from map file content.

        Args:
            data: Raw file content.

        Returns:
            List of (line_number, content) tuples with comments removed.
        """
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
        """Parse the number of drones from the map file.

        Args:
            lines: List of (line_number, content) tuples.
            index: Current line index.

        Returns:
            The next line index after parsing.
        """
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
        """Parse hub definitions from the map file.

        Args:
            lines: List of (line_number, content) tuples.
            index: Current line index.

        Returns:
            The next line index after parsing all hubs.
        """
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
                for existing in self.hubs.values():
                    if MathUtils.is_same_2d_pos(
                                existing.get_position(),
                                hub.get_position()
                            ):
                        self._result.errors.append(ParseError(
                            lineno, line,
                            f'Hub {hub.name!r} has duplicate position '
                            f'{hub.get_position().x}, {hub.get_position().y} '
                            f'with hub {existing.name!r}'
                        ))
                self.hubs.update({
                    hub.name: hub
                })
                if hub.is_start() and hub.is_blocked():
                    self._result.errors.append(ParseError(
                        lineno, line,
                        'Start hub cannot be blocked'
                    ))
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
        """Parse connection definitions from the map file.

        Args:
            lines: List of (line_number, content) tuples.
            index: Current line index to start parsing connections.
        """
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
