from .errors import (
    FileNotFoundError as _FileNotFoundError,
    PermissionError as _PermissionError,
    NotAFileError,
    ParseError
)
from .utils import Color, Logger, MathUtils
from .network import Connection, ConnectionManager
from .network import Node, NodeType

from pydantic import BaseModel, Field, PrivateAttr, ValidationError
from dataclasses import dataclass, field
from typing import ClassVar, Any
import re


t_re = re.Pattern[str]


@dataclass
class ParseResult:
    """Result of parsing a map file.

    Attributes:
        nb_drones: Number of drones from the map.
        nodes: Dictionary of all parsed nodes.
        errors: List of parsing errors encountered.
        connections: All parsed connections.
    """
    nb_drones: int = 0
    nodes: dict[str, Node] = field(default_factory=dict)
    errors: list[ParseError] = field(default_factory=list)
    connections: ConnectionManager = field(default_factory=ConnectionManager)

    @property
    def ok(self) -> bool:
        """Check if parsing was successful.

        Returns:
            True if no errors occurred during parsing, False otherwise.
        """
        return len(self.errors) == 0


class MapLoader(BaseModel):
    """Loads and parses map files to create map objects.

    Attributes:
        filepath: Path to the map file to load.
        verbose: Whether to enable verbose logging.
    """
    filepath: str = Field()
    verbose: bool = Field(default=False)

    _RE_NB_DRONES: ClassVar[t_re] = re.compile(r'^nb_drones:\s*(\d+)$')
    _RE_NODE: ClassVar[t_re] = re.compile(r'^(start_hub|end_hub|hub):')
    _RE_CONNECTION: ClassVar[t_re] = re.compile(r'^connection:\s*')

    _logger: Logger = PrivateAttr()
    _result: ParseResult = PrivateAttr()
    _start_node: Node = PrivateAttr()
    _end_node: Node = PrivateAttr()

    @property
    def nb_drones(self) -> int:
        """Get the number of drones.

        Returns:
            Number of drones from the parsed map.
        """
        return self._result.nb_drones

    @property
    def nodes(self) -> dict[str, Node]:
        """Get all nodes.

        Returns:
            Dictionary of nodes indexed by name.
        """
        return self._result.nodes

    @property
    def connections(self) -> ConnectionManager:
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
            name='MapLoader',
            color=Color.YELLOW
        )
        self._result = ParseResult()
        self._logger.log(f'Loading map from {self.filepath!r}...')

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
            f'Map loaded successfully with {self.nb_drones} drones, '
            f'{len(self.nodes)} nodes and {len(self.connections.all)} '
            'connections.'
        )

        return super().model_post_init(context)

    def _check_map_validity(self) -> None:
        """Validate that the map has required start and end nodes.

        Appends errors to _result if validation fails.
        """
        start_nodes = [
            node
            for node in self.nodes.values()
            if node.type == NodeType.START_NODE
        ]
        end_nodes = [
            node
            for node in self.nodes.values()
            if node.type == NodeType.END_NODE
        ]
        if not start_nodes:
            self._result.errors.append(ParseError(
                0, '',
                'Map must contain at least one start_hub'
            ))
        if not end_nodes:
            self._result.errors.append(ParseError(
                0, '',
                'Map must contain at least one end_hub'
            ))
        if len(start_nodes) > 1:
            self._result.errors.append(ParseError(
                0, '',
                'Map must contain at most one start_hub, got '
                f'{len(start_nodes)}'
            ))
        if len(end_nodes) > 1:
            self._result.errors.append(ParseError(
                0, '',
                f'Map must contain at most one end_hub, got {len(end_nodes)}'
            ))
        if start_nodes and end_nodes:
            self._start_node = start_nodes[0]
            self._end_node = end_nodes[0]

    def get_start_node(self) -> Node:
        """Get the start node.

        Returns:
            The start node of the map.

        Raises:
            ValueError: If the map doesn't have a valid start node.
        """
        if not self._start_node:
            raise ValueError('Map does not have a valid start node')
        return self._start_node

    def get_end_node(self) -> Node:
        """Get the end node.

        Returns:
            The end node of the map.

        Raises:
            ValueError: If the map doesn't have a valid end node.
        """
        if not self._end_node:
            raise ValueError('Map does not have a valid end node')
        return self._end_node

    def _load(self) -> None:
        """Load and parse the map file.

        Reads the file and parses drones, nodes, and connections sections.
        """
        with open(self.filepath, 'r') as f:
            raw: str = f.read()

        lines: list[tuple[int, str]] = self._strip_comments(raw)
        if not lines:
            self._result.errors.append(ParseError(0, '', 'File is empty'))
            return

        index: int = 0
        index = self._parse_nb_drones(lines, index)
        index = self._parse_nodes(lines, index)

        if (self._result.ok):
            self._parse_connections(lines, index)

        self._check_map_validity()
        self._update_nodes_capacities()

    def _update_nodes_capacities(self) -> None:
        """Update start/end node capacities if needed.

        Ensures start and end nodes can accommodate all drones.
        """
        for node in self.nodes.values():
            if node.is_start() and node.metadata.max_drones < self.nb_drones:
                self._logger.warning(
                    f'Start node {node.name!r} has max_drones='
                    f'{node.metadata.max_drones}, but nb_drones='
                    f'{self.nb_drones}. Updating max_drones to '
                    f'{self.nb_drones}.'
                )
                node.metadata.max_drones = self.nb_drones
            elif node.is_end() and node.metadata.max_drones < self.nb_drones:
                self._logger.warning(
                    f'End node {node.name!r} has max_drones='
                    f'{node.metadata.max_drones}, but nb_drones='
                    f'{self.nb_drones}. Updating max_drones to '
                    f'{self.nb_drones}.'
                )
                node.metadata.max_drones = self.nb_drones

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

    def _parse_nodes(self, lines: list[tuple[int, str]], index: int) -> int:
        """Parse node definitions from the map file.

        Args:
            lines: List of (line_number, content) tuples.
            index: Current line index.

        Returns:
            The next line index after parsing all nodes.
        """
        while index < len(lines):
            lineno, line = lines[index]
            if (not self._RE_NODE.match(line)
               and self._RE_CONNECTION.match(line)):
                break
            try:
                node = Node.from_str(line, self._logger)
                if self.nodes.get(node.name):
                    self._result.errors.append(ParseError(
                        lineno, line, 'hub name must be unique, got duplicate'
                        f' name {node.name!r}'
                    ))
                for existing in self.nodes.values():
                    if MathUtils.is_same_2d_pos(
                                existing.get_position(),
                                node.get_position()
                            ):
                        self._result.errors.append(ParseError(
                            lineno, line,
                            f'hub {node.name!r} has duplicate position '
                            f'{node.get_position().x}, {node.get_position().y}'
                            f' with hub {existing.name!r}'
                        ))
                self.nodes.update({
                    node.name: node
                })
                if node.is_start() and node.is_blocked():
                    self._result.errors.append(ParseError(
                        lineno, line,
                        'Start node cannot be blocked'
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
                    Connection.from_str(line, self.nodes, self._logger)
                )
            except ValueError as e:
                self._result.errors.append(ParseError(lineno, line, str(e)))

            index += 1
