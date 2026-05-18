from .. import NetworkObject, ZoneType, NodeMetadata
from .node_type import NodeType
from ...utils import Logger

from pydantic import BaseModel, Field, PrivateAttr
from typing import cast, TYPE_CHECKING
from functools import lru_cache
from pyray import Vector2
import re

if TYPE_CHECKING:
    from ..connection import Connection


HUB_PATTERN = re.compile(
    r'^(\w+):\s+(\w+)\s+(-?\d+)\s+(-?\d+)(?:\s+\[([^\]]*)\])?$'
)


class Node(NetworkObject, BaseModel):
    """Represents a node (network node) in the delivery system.

    Attributes:
        type: The type of node (regular, start, or end).
        name: Unique identifier/name for the node.
        x: X coordinate of the node position.
        y: Y coordinate of the node position.
        metadata: Node metadata including zone type, color, and capacity.
    """
    type: NodeType = Field()
    name: str = Field()
    x: int = Field()
    y: int = Field()
    metadata: NodeMetadata = Field(default_factory=NodeMetadata)
    _connections: list['Connection'] = PrivateAttr(default=[])

    @classmethod
    def from_str(cls, line: str, logger: Logger) -> 'Node':
        """Parse a node from a formatted string line.

        Args:
            line: String in format 'name: type x y [key=value ...]'.

        Returns:
            A new Node instance.

        Raises:
            ValueError: If line format is invalid or attributes are malformed.
        """
        match = HUB_PATTERN.match(line.strip())
        if not match:
            raise ValueError(f'Invalid hub line format: {line!r}')

        node_type, node_name, x, y, attrs_str = match.groups()

        attrs: dict[str, str] = {}
        if attrs_str:
            for pair in attrs_str.split(' '):
                key, sep, value = pair.strip().partition('=')
                if not sep:
                    raise ValueError(
                        f'Malformed attribute {pair.strip()!r} '
                        f'(expected key=value) in line: {line!r}'
                    )
                attrs[key.strip()] = value.strip()

        metadata = NodeMetadata.from_attrs(attrs, logger)

        return cls(
            type=cast(NodeType, node_type),
            name=node_name,
            x=int(x),
            y=int(y),
            metadata=metadata,
        )

    def get_connections(self) -> list[tuple['Node', 'Connection']]:
        """
        Get all connections (edges) from this node.

        Returns:
            A list of tuples containing connected nodes and their connections.
        """
        return self._get_connections_cached()

    @lru_cache(maxsize=None)
    def _get_connections_cached(
                self
            ) -> list[tuple['Node', 'Connection']]:
        """
        Get all connections (edges) from this node, with caching.

        Returns:
            A list of tuples containing connected nodes and their connections.
        """
        connections: list[tuple['Node', 'Connection']] = []

        for connection in self._connections:
            if connection.nodes[0] is self:
                connections.append((connection.nodes[1], connection))
            else:
                connections.append((connection.nodes[0], connection))

        return connections

    def is_blocked(self) -> bool:
        """Check if the node is in a blocked zone.

        Returns:
            True if node is blocked, False otherwise.
        """
        return self.metadata.zone == ZoneType.BLOCKED

    def is_priority(self) -> bool:
        """Check if the node is in a priority zone.

        Returns:
            True if node is priority, False otherwise.
        """
        return self.metadata.zone == ZoneType.PRIORITY

    def is_restricted(self) -> bool:
        """Check if the node is in a restricted zone.

        Returns:
            True if node is restricted, False otherwise.
        """
        return self.metadata.zone == ZoneType.RESTRICTED

    def is_start(self) -> bool:
        """Check if this is a starting node.

        Returns:
            True if node type is START_HUB, False otherwise.
        """
        return self.type == NodeType.START_NODE

    def is_end(self) -> bool:
        """Check if this is an ending node.

        Returns:
            True if node type is END_HUB, False otherwise.
        """
        return self.type == NodeType.END_NODE

    def get_position(self) -> Vector2:
        """Get the node's position in 2D space.

        Returns:
            The node's coordinates as a Vector2.
        """
        return Vector2(self.x, self.y)

    def get_name(self) -> str:
        """Get the node's name/identifier.

        Returns:
            The node's name.
        """
        return self.name

    def get_capacity(self) -> int:
        """Get the node's capacity for drone traffic.

        Returns:
            The node's capacity as an integer.
        """
        return self.metadata.max_drones

    def __lt__(self, other: 'Node') -> bool:
        """Check if this node's name is lexicographically less than another.

        Args:
            other: Another Node instance.

        Returns:
            True if self.name < other.name, False otherwise.
        """
        return self.name < other.name

    def __eq__(self, other: object) -> bool:
        """Check equality based on node name.

        Args:
            other: Another object.

        Returns:
            True if other is a Node with the same name, False otherwise.
        """
        return isinstance(other, Node) and self.name == other.name

    def __hash__(self) -> int:
        """Get hash based on node name for use in sets and dicts.

        Returns:
            Hash value of the node's name.
        """
        return hash(self.name)
