from .bfs_object import BFSObject
from .bfs_node import BFSNode
from ...network import Connection


class BFSEdge(BFSObject):
    """Edge connecting two BFS nodes.

    Represents a directed edge in the BFS tree with capacity constraints
    and an optional associated network Connection.

    Attributes:
        nodes: Tuple of (from_node, to_node) BFSNodes.
        connection: Optional Connection from the network graph.
    """
    nodes: tuple[BFSNode, BFSNode]
    connection: Connection | None

    def __init__(
                self,
                nodes: tuple[BFSNode, BFSNode],
                capacity: int,
                connection: Connection | None = None
            ) -> None:
        """Initialize a BFS edge.

        Args:
            nodes: Tuple of two BFSNode objects to connect.
            capacity: Flow capacity of the edge.
            connection: Optional network Connection object.
        """
        super().__init__(capacity)

        self.nodes = nodes
        self.connection = connection

    def get_name(self) -> str:
        """Get a string name for the edge based on its nodes.

        Returns:
            A string in the format "NodeA-NodeB".
        """
        return (
            f'{self.nodes[0].node.get_name()}-{self.nodes[1].node.get_name()}'
        )

    def get_other(self, node: BFSNode) -> BFSNode:
        """Get the other endpoint of the edge.

        Args:
            node: One endpoint of the edge.

        Returns:
            The other BFSNode in the edge.

        Raises:
            ValueError: If the provided node is not part of this edge.
        """
        if self.nodes[0] == node:
            return self.nodes[1]
        elif self.nodes[1] == node:
            return self.nodes[0]
        else:
            raise ValueError('Node not in edge')

    def is_full(self) -> bool:
        """Check if the edge or any adjacent node is at capacity.

        Returns:
            True if edge or any node is full, False otherwise.
        """
        return super().is_full()

    def get_connection(self) -> Connection | None:
        """Get the network connection associated with this edge.

        Returns:
            The Connection object, or None if this is a waiting edge.
        """
        return self.connection
