from ..bfs import BFSObject
from ..time_graph import Node
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bfs import BFSEdge


class BFSNode(BFSObject):
    node: Node
    edges: list['BFSEdge']

    _need_to_be_sorted: bool

    def __init__(self, node: Node, level: int, capacity: int) -> None:
        super().__init__(capacity)

        self.node: Node = node
        self.level: int = level
        self.edges: list['BFSEdge'] = []

        self._need_to_be_sorted: bool = False

    def add_edge(self, edge: 'BFSEdge') -> None:
        self.edges.append(edge)
        self._need_to_be_sorted = True

    def sort_edges(self) -> list['BFSEdge']:
        if self._need_to_be_sorted:
            self.edges.sort(
                key=lambda edge: edge.get_other(self).node.object.is_priority()
            )
            self._need_to_be_sorted = False
        return self.edges
