from ..network_object import NetworkObject
from ..metadata import ConnectionMetadata
from ...utils import Logger
from ..node import Node

from typing import Match
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

    def __init__(
                self,
                node_a: Node,
                node_b: Node,
                metadata: ConnectionMetadata
            ) -> None:
        self.nodes = (node_a, node_b)
        self.metadata = metadata
        self.drones = []

        node_a._connections.append(self)
        node_b._connections.append(self)

    def get_name(self) -> str:
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
        return self.metadata.capacity

    def get_capacity_from(self, node: Node) -> int:
        return min(self.get_other(node).get_capacity(), self.get_capacity())

    def _calculate_hash(self) -> None:
        self._hash = hash(tuple(sorted((
            self.nodes[0].name,
            self.nodes[1].name
        ))))

    def __hash__(self) -> int:
        if not hasattr(self, '_hash'):
            self._calculate_hash()
        return self._hash

    @classmethod
    def from_str(
                cls,
                line: str,
                nodes: dict[str, Node],
                logger: Logger
            ) -> 'Connection':
        """Parse a connection from a formatted string line.

        Args:
            line: String in format 'connection: hub1-hub2 [key=value ...]'.
            hubs: Dictionary mapping hub IDs to Hub objects.

        Returns:
            A new Connection instance.

        Raises:
            ValueError: If line format is invalid or references unknown hubs.
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
