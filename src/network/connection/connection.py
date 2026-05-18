from ..network_object import NetworkObject
from ..metadata import ConnectionMetadata
from ...utils import Logger
from ..node import Node

from typing import Match, Optional
from pyray import Vector2
import re


CONNECTION_PATTERN = re.compile(
    r'^connection: (\w+)-(\w+)(?:\s+\[([^\]]*)\])?$'
)


class Connection(NetworkObject):
    """Represents a connection between two nodes in the network.

    Attributes:
        nodes: A tuple containing the two connected Node objects.
        latency: The latency of the connection in milliseconds.
    """
    nodes: tuple[Node, Node]
    metadata: ConnectionMetadata
    drones: list[NetworkObject]

    _hash: int
    _position_cache: Optional[Vector2]

    def __init__(
                self,
                node_a: Node,
                node_b: Node,
                metadata: ConnectionMetadata
            ) -> None:
        """Initialize a connection between two nodes.

        Args:
            node_a: First node to connect.
            node_b: Second node to connect.
            metadata: Connection metadata (capacity, blocked status).
        """
        self.nodes = (node_a, node_b)
        self.metadata = metadata
        self.drones = []

        self._position_cache = None
        node_a._connections.append(self)
        node_b._connections.append(self)

    def get_position(self) -> Vector2:
        """Get the midpoint position of the connection.

        Returns:
            Vector2 position at the center between both nodes.
        """
        return self._position_cache or self._calculate_position()

    def get_name(self) -> str:
        """Get the connection's display name.

        Returns:
            String formatted as 'node1-node2'.
        """
        return f'{self.nodes[0].name}-{self.nodes[1].name}'

    def get_other(self, node: Node) -> Node:
        """Get the other node connected by this connection.

        Args:
            node: One of the two nodes in this connection.

        Returns:
            The other Node object connected by this connection.

        Raises:
            ValueError: If the provided node is not part of this connection.
        """
        if node == self.nodes[0]:
            return self.nodes[1]
        elif node == self.nodes[1]:
            return self.nodes[0]
        else:
            raise ValueError(
                f'Node {node.name!r} is not part of this connection '
                f'between {self.nodes[0].name!r} and {self.nodes[1].name!r}.'
            )

    def get_capacity(self) -> int:
        """Get the connection's capacity.

        Returns:
            Maximum number of drones allowed on the connection.
        """
        return self.metadata.capacity

    def get_capacity_from(self, node: Node) -> int:
        """Get the capacity available from a specific node.

        Returns the minimum of the connection capacity and the other node's
        capacity.

        Args:
            node: One of the connected nodes.

        Returns:
            Available capacity from the specified node.
        """
        return min(self.get_other(node).get_capacity(), self.get_capacity())

    def _calculate_hash(self) -> None:
        """Calculate and cache hash based on node names.

        Hash is computed from sorted node names to be independent of order.
        """
        self._hash = hash(tuple(sorted((
            self.nodes[0].name,
            self.nodes[1].name
        ))))

    def __hash__(self) -> int:
        """Get the hash value for this connection.

        Returns:
            Hash based on the connection's node pair.
        """
        if not hasattr(self, '_hash'):
            self._calculate_hash()
        return self._hash

    def _calculate_position(self) -> Vector2:
        """Calculate the midpoint between the two nodes.

        Returns:
            Vector2 at the center point between both nodes.
        """
        x: float = (self.nodes[0].x + self.nodes[1].x) / 2
        y: float = (self.nodes[0].y + self.nodes[1].y) / 2
        self._position_cache = Vector2(x, y)

        return self._position_cache

    @classmethod
    def from_str(
                cls,
                line: str,
                nodes: dict[str, Node],
                logger: Logger
            ) -> 'Connection':
        """Parse a connection from a formatted string line.

        Args:
            line: String in format 'connection: node1-node2 [key=value ...]'.
            nodes: Dictionary mapping Node IDs to node objects.
            logger: Logger for reporting parsing issues.

        Returns:
            A new Connection instance.

        Raises:
            ValueError: If line format is invalid or references unknown nodes.
        """
        match: Match[str] | None = CONNECTION_PATTERN.match(line.strip())
        if not match:
            raise ValueError(f'Invalid connection line format: {line!r}')

        raw_node_a, raw_node_b, attrs_str = match.groups()

        _nodes: list[Node | None] = [
            nodes.get(raw_node_a),
            nodes.get(raw_node_b)
        ]

        if not _nodes[0] or not _nodes[1]:
            raise ValueError(
                'Connection references unknown hub(s): '
                f'{raw_node_a!r}, {raw_node_b!r}'
            )

        if _nodes[0] == _nodes[1]:
            raise ValueError(
                f'Connection cannot link a hub to itself: {_nodes[0].name!r}'
            )

        return cls(
            node_a=_nodes[0],
            node_b=_nodes[1],
            metadata=ConnectionMetadata.from_str(attrs_str or '', line, logger)
        )
