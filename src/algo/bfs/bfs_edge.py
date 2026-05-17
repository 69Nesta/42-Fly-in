from .bfs_object import BFSObject
from .bfs_node import BFSNode
from ...network import Connection


class BFSEdge(BFSObject):
    nodes: tuple[BFSNode, BFSNode]
    connection: Connection | None

    def __init__(
                self,
                nodes: tuple[BFSNode, BFSNode],
                capacity: int,
                connection: Connection | None = None
            ) -> None:
        super().__init__(capacity)

        self.nodes = nodes
        self.connection = connection

    def get_other(self, node: BFSNode) -> BFSNode:
        if self.nodes[0] == node:
            return self.nodes[1]
        elif self.nodes[1] == node:
            return self.nodes[0]
        else:
            raise ValueError('Node not in edge')

    def get_connection(self) -> Connection | None:
        return self.connection
