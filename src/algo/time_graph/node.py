from ...network import Node as NetworkNode, Connection


class Node:
    """A node in the time-expanded graph.

    Represents a network object (node or zone) at a specific time step,
    with outgoing edges to other nodes at later time steps.

    Attributes:
        time: The time step of this node.
        object: The network node/zone this represents.
        connections: List of (destination_node, connection) tuples.
    """
    time: int
    object: NetworkNode
    connections: list[tuple['Node', Connection | None]]

    def __init__(
                self,
                time: int,
                object: NetworkNode,
            ) -> None:
        """Initialize a time-graph node.

        Args:
            time: The time step.
            object: The network object at this time step.
        """
        self.time = time
        self.object = object
        self.connections = []

    def add_connection(
                self,
                node: 'Node',
                connection: Connection | None = None
            ) -> None:
        """Add an outgoing edge to another time-graph node.

        Args:
            node: The destination node.
            connection: Optional Connection object (None for waiting edges).
        """
        if (node, connection) in self.connections:
            return
        self.connections.append((node, connection))

    def get_name(self) -> str:
        """Get the display name of this node.

        Returns:
            The name of the underlying network object.
        """
        return self.object.get_name()

    def get_connections(self) -> list[tuple['Node', Connection | None]]:
        """Get all outgoing edges from this node.

        Returns:
            List of (destination_node, connection) tuples.
        """
        return self.connections
