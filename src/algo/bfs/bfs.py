from ...network import Network, Connection
from ...utils import Logger, Color
from ..time_graph import TimeGraph, Node
from . import BFSNode, BFSEdge

from functools import lru_cache


class BFS:
    logger: Logger
    time_graph: TimeGraph
    network: Network

    steps: dict[int, set[BFSNode]]
    current_step: int

    start_node: BFSNode
    reached_end_node: bool

    def __init__(self, verbose: bool, time_graph: TimeGraph) -> None:
        self.logger = Logger(
            name='BFS',
            print_log=verbose,
            color=Color.BLUE
        )
        self.logger.log('Initializing BFS...')
        self.time_graph = time_graph
        self.network = time_graph.network

        self.start_node = self.create_node(
            node=list(time_graph.get_step(0))[0],
            level=0,
            capacity=time_graph.network.start_node.get_capacity()
        )
        self.steps = {
            0: set([self.start_node])
        }
        self.current_step = 0

        self.create_edges_of_node(self.start_node)

        self.reached_end_node = self.start_node.node.object.is_end()

    def get_step(self, step: int) -> list[BFSNode]:
        while self.current_step < step:
            self.expend()
        return list(self.steps.get(step, set()))

    def next_step(self) -> None:
        nodes: set[BFSNode] = self.steps.get(self.current_step, set())
        if not nodes:
            return

        for node in nodes:
            if not self.reached_end_node:
                if node.node.object.is_end():
                    self.reached_end_node = True

            for edge in node.edges:
                other_node = edge.get_other(node)
                self.steps.setdefault(
                    self.current_step + 1, set()
                ).add(other_node)

        self.current_step += 1

        for node in self.steps.get(self.current_step, set()):
            self.create_edges_of_node(node)

    def expend(self) -> None:
        self.time_graph.next_step()
        max_step: int = max(self.steps.keys(), default=0)

        for step in range(max_step + 1):
            for _node in self.get_step(step):
                self.create_edges_of_node(_node)

        if not self.steps.get(self.current_step, set()):
            for step in range(max_step - 1, -1, -1):
                if self.steps.get(step, set()):
                    self.current_step = step
                    break

        self.next_step()

    @lru_cache(maxsize=None)
    def create_node(
                self,
                node: Node,
                level: int,
                capacity: int
            ) -> BFSNode:
        return BFSNode(node, level, capacity)

    def create_edge(
                self,
                from_node: BFSNode,
                to_node: BFSNode,
                connection: Connection | None = None
                ) -> BFSEdge:
        edge: BFSEdge = BFSEdge(
            nodes=(from_node, to_node),
            capacity=to_node.capacity,
            connection=connection
        )
        from_node.add_edge(edge)
        return edge

    def create_edges_of_node(self, node: BFSNode) -> None:
        for connected_node, connection in node.node.get_connections():
            if connected_node.time <= node.node.time:
                continue
            bfs_connected_node: BFSNode = self.create_node(
                node=connected_node,
                level=node.level + 1,
                capacity=connected_node.object.get_capacity()
            )
            if any(
                edge.get_other(node).node == connected_node
                for edge in node.edges
            ):
                continue
            self.create_edge(
                from_node=node,
                to_node=bfs_connected_node,
                connection=connection
            )
