from .dfs_object import DFSObject
from .dfs_node import DFSNode
from ...network import Connection


class DFSEdge(DFSObject):
    nodes: tuple[DFSNode, DFSNode]
    connection: Connection | None

    def __init__(
                self,
                nodes: tuple[DFSNode, DFSNode],
                capacity: int,
                connection: Connection | None = None
            ) -> None:
        super().__init__(capacity)

        self.nodes = nodes
        self.connection = connection

    def get_other(self, node: DFSNode) -> DFSNode:
        if self.nodes[0] == node:
            return self.nodes[1]
        elif self.nodes[1] == node:
            return self.nodes[0]
        else:
            raise ValueError('Node not in edge')

    def get_connection(self) -> Connection | None:
        return self.connection
