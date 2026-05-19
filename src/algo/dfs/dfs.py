from ..bfs import BFSEdge, BFSNode, BFSObject, BFS
from ..time_graph import ConnectionNode
from ...utils import Logger, Color
from ...errors import FlyInError
from ...network import Network


class DFS:
    """Depth-First Search for finding augmenting paths in flow network.

    Uses DFS to find augmenting paths from start to end nodes, computing
    blocking flows and updating residual capacities.

    Attributes:
        logger: Logger instance for algorithm progress.
        bfs: The BFS instance providing the level graph.
        network: The Network instance being solved.
        nodes: BFS nodes encountered during search.
        edges: BFS edges encountered during search.
        paths: List of computed paths, each a list of BFSObjects.
    """
    logger: Logger
    bfs: BFS
    network: Network

    nodes: list[BFSNode]
    edges: list[BFSEdge]
    paths: list[list[BFSObject]]

    def __init__(self, verbose: bool, bfs: BFS, network: Network) -> None:
        """Initialize the DFS algorithm.

        Args:
            verbose: Whether to enable verbose logging.
            bfs: The BFS instance providing the level graph.
            network: The Network instance to solve.
        """
        self.logger = Logger(
            name='DFS',
            print_log=verbose,
            color=Color.CYAN
        )
        self.logger.log('Initializing DFS...')
        self.bfs = bfs
        self.network = network

        self.nodes = []
        self.edges = []
        self.paths = []

    def generate_path(
                self,
                path: list[BFSObject],
                visited: set[BFSObject],
                deadlock: set[BFSNode]
            ) -> list[BFSObject] | None:
        """Generate an augmenting path from start to end node.

        Uses DFS to find a valid path avoiding full edges and deadlock nodes.

        Args:
            path: Current path being built.
            visited: Set of visited nodes and edges to avoid cycles.
            deadlock: Set of nodes identified as deadlocked (no way forward).

        Returns:
            Complete augmenting path if found, None otherwise.
        """
        if not path:
            return None

        start_node: BFSObject = path[-1]
        if not isinstance(start_node, BFSNode):
            return None

        if (start_node.node.object.is_end()
           and not isinstance(start_node.node, ConnectionNode)):
            return path

        visited.add(start_node)

        for edge in start_node.sort_edges():
            if edge.is_full() or edge in visited:
                continue

            other_node: BFSNode = edge.get_other(start_node)
            if other_node in visited or other_node in deadlock:
                continue
            if other_node.is_full():
                continue

            path_length: int = len(path)
            path.append(edge)
            visited.add(edge)
            path.append(other_node)

            if (other_node.node.object.is_end()
               and not isinstance(other_node.node, ConnectionNode)):
                return path

            result = self.generate_path(path, visited, deadlock)
            if result is not None:
                return result

            del path[path_length:]
            visited.discard(edge)

        visited.discard(start_node)
        deadlock.add(start_node)
        return None

    def _debug_path(self, path: list[BFSObject]) -> None:
        """Helper method to format a path for debugging.

        Args:
            path: List of BFSObjects representing the path.
        """
        self.logger.log('Current path:')
        for obj in path:
            self.logger.log(
                f'  {obj.get_name():20} (remaining capacity:'
                f' {obj.get_remaining_capacity()})'
            )

    @staticmethod
    def get_blocking_flow(path: list[BFSObject]) -> int:
        """Calculate the maximum flow that can traverse the path.

        The flow is limited by the object with minimum capacity.

        Args:
            path: List of BFSObjects (nodes and edges) in the path.

        Returns:
            The bottleneck (minimum) capacity along the path.
        """
        return min(
            current_object.get_remaining_capacity()
            for current_object in path
        )

    @staticmethod
    def apply_flow(path: list[BFSObject], flow: int) -> None:
        """Apply flow to all objects in a path, reducing their capacity.

        Args:
            path: List of BFSObjects to apply flow to.
            flow: Amount of flow to apply.
        """
        for current_object in path:
            current_object.add_load(flow)

    def store_path(self, path: list[BFSObject], flow: int) -> None:
        """Store multiple copies of a path for each unit of flow.

        Args:
            path: The path to store.
            flow: Number of copies to store.
        """
        for _ in range(flow):
            self.paths.append(path.copy())

    def solve(self) -> None:
        """Solve using Dinic's algorithm (BFS + DFS).

        Iteratively finds blocking flows until all drones are routed.
        """
        self.logger.log('Running DFS...')

        total_flow: int = 0

        max_retries: int = 1000
        retries: int = 0

        while total_flow < self.network.nb_drones:
            path: list[BFSObject] | None = self.generate_path(
                [self.bfs.start_node],
                set(),
                set()
            )
            if path is None:
                retries += 1
                if retries > max_retries:
                    raise FlyInError(
                        f'Exceeded maximum retries ({max_retries}) without'
                        ' finding a path. Possible deadlock or unsolvable '
                        'network.'
                    )
                self.bfs.expend()
                continue

            flow: int = self.get_blocking_flow(path)
            if flow == 0:
                raise FlyInError('Found path with zero flow')

            self.apply_flow(path, flow)
            self.store_path(path, flow)
            total_flow += flow

        self.logger.log(
            f'Successfully routed all {total_flow} drones!'
        )
