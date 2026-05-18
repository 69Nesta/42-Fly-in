from ..bfs import BFSObject
from ..time_graph import Node
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bfs import BFSEdge


class BFSNode(BFSObject):
    """Node in a breadth-first search tree.

    Wraps a time-graph Node with BFS-specific metadata including level
    in the search tree, associated edges, and edge sorting state.

    Attributes:
        node: The underlying time-graph Node.
        level: The distance from the start node in the BFS tree.
        edges: List of BFSEdge objects connected to this node.
    """
    node: Node
    edges: list['BFSEdge']

    _need_to_be_sorted: bool

    def __init__(self, node: Node, level: int, capacity: int) -> None:
        """Initialize a BFS node.

        Args:
            node: The time-graph Node to wrap.
            level: The BFS level (distance from start).
            capacity: The capacity of the node.
        """
        super().__init__(capacity)

        self.node: Node = node
        self.level: int = level
        self.edges: list['BFSEdge'] = []

        self._need_to_be_sorted: bool = False

    def add_edge(self, edge: 'BFSEdge') -> None:
        """Add an edge connected to this node.

        Args:
            edge: The BFSEdge to add.
        """
        self.edges.append(edge)
        self._need_to_be_sorted = True

    def sort_edges(self) -> list['BFSEdge']:
        """Sort edges by priority of destination nodes.

        Priority nodes are sorted last. Caches the result until new edges
        are added.

        Returns:
            The sorted list of edges.
        """
        if self._need_to_be_sorted:
            self.edges.sort(
                key=lambda edge: edge.get_other(self).node.object.is_priority()
            )
            self._need_to_be_sorted = False
        return self.edges
