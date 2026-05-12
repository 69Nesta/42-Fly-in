from .dfs_object import DFSObject
from ...network import Node
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dfs_edge import DFSEdge


class DFSNode(DFSObject):
    node: Node
    edges: list['DFSEdge']

    _need_to_be_sorted: bool

    def __init__(self, node: Node, level: int, capacity: int) -> None:
        super().__init__(capacity)

        self.node: Node = node
        self.level: int = level
        self.edges: list['DFSEdge'] = []

        self._need_to_be_sorted: bool = False

    def add_edge(self, edge: 'DFSEdge') -> None:
        self.edges.append(edge)
        self._need_to_be_sorted = True

    def sort_edges(self) -> list['DFSEdge']:
        if self._need_to_be_sorted:
            self.edges.sort(
                key=lambda edge: edge.get_other(self).node.is_priority(),
            )
            self._need_to_be_sorted = False
        return self.edges
