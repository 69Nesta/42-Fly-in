from ...network import Network, Connection, Node as NetworkNode
from ...utils import Logger, Color
from ..time_graph import TimeGraph, Node
from ...errors import FlyInError
from . import BFSNode, BFSEdge

from functools import lru_cache


class BFS:
    """Breadth-First Search in a time-expanded network graph.

    Performs BFS to explore reachable nodes from the start node, expanding
    the time graph dynamically and detecting if the end node is reachable.

    Attributes:
        logger: Logger instance for BFS progress.
        time_graph: The TimeGraph instance to search.
        network: The Network instance from the time graph.
        steps: Dictionary mapping time steps to sets of reachable BFSNodes.
        current_step: Current time step being explored.
        start_node: BFSNode representing the start at time 0.
        reached_end_node: Flag indicating if end node has been reached.
        LOOK_UP_HISTORY: Steps to look back for convergence detection.
    """
    logger: Logger
    time_graph: TimeGraph
    network: Network

    steps: dict[int, set[BFSNode]]
    current_step: int

    start_node: BFSNode
    reached_end_node: bool
    LOOK_UP_HISTORY: int = 3

    def __init__(self, verbose: bool, time_graph: TimeGraph) -> None:
        """Initialize BFS with a time-expanded graph.

        Args:
            verbose: Whether to enable verbose logging.
            time_graph: The TimeGraph instance to search.
        """
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
        """Get all reachable nodes at a given time step.

        Args:
            step: The time step to retrieve nodes for.

        Returns:
            List of BFSNode objects reachable at the specified step.
        """
        while self.current_step < step:
            self.expend()
        return list(self.steps.get(step, set()))

    def next_step(self) -> None:
        """Advance to the next time step by expanding edges."""
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
        """Expand the search to the next time step.

        Raises:
            FlyInError: If the end node becomes unreachable (path converged).
        """
        self.time_graph.next_step()

        max_step: int = max(self.steps.keys(), default=0)
        if not self.reached_end_node and max_step > 5:
            old_nodes: set[NetworkNode] = {
                node.node.object
                for node in self.get_step(
                    max_step - self.LOOK_UP_HISTORY
                )
            }
            has_new_nodes: list[bool] = []
            for i in range(self.LOOK_UP_HISTORY - 1, -1, -1):
                step_nodes: set[NetworkNode] = {
                    node.node.object
                    for node in self.get_step(max_step - i)
                }
                if step_nodes - old_nodes:
                    has_new_nodes.append(True)
                    old_nodes = step_nodes
                else:
                    has_new_nodes.append(False)
            if not any(has_new_nodes):
                raise FlyInError(
                    'End node is unreachable.'
                )

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
        """Create or retrieve a cached BFSNode.

        Args:
            node: The time-graph node to wrap.
            level: The BFS level (distance from start).
            capacity: The flow capacity of the node.

        Returns:
            A BFSNode wrapper around the time-graph node.
        """
        return BFSNode(node, level, capacity)

    def create_edge(
                self,
                from_node: BFSNode,
                to_node: BFSNode,
                connection: Connection | None = None
                ) -> BFSEdge:
        """Create a BFS edge between two nodes.

        Args:
            from_node: Source BFSNode.
            to_node: Target BFSNode.
            connection: Optional Connection object representing the link.

        Returns:
            A BFSEdge connecting the two nodes.
        """
        edge: BFSEdge = BFSEdge(
            nodes=(from_node, to_node),
            capacity=(
                to_node.capacity
                if not connection
                else connection.get_capacity()
            ),
            connection=connection
        )
        from_node.add_edge(edge)
        return edge

    def create_edges_of_node(self, node: BFSNode) -> None:
        """Create edges from a node to all connected neighbors.

        Args:
            node: The BFSNode to create edges from.
        """
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
