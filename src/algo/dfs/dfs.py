from ..bfs import BFSEdge, BFSNode, BFSObject, BFS
from ...utils import Logger, Color
from ...network import Network


class DFS:
    logger: Logger
    bfs: BFS
    network: Network

    nodes: list[BFSNode]
    edges: list[BFSEdge]
    paths: list[list[BFSObject]]

    def __init__(self, verbose: bool, bfs: BFS, network: Network) -> None:
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
        if not path:
            return None

        start_node: BFSObject = path[-1]
        if not isinstance(start_node, BFSNode):
            return None

        if start_node.node.object.is_end():
            return path

        visited.add(start_node)

        for edge in start_node.sort_edges():
            if edge.is_full() or edge in visited:
                continue

            other_node: BFSNode = edge.get_other(start_node)
            if other_node in visited or other_node in deadlock:
                continue

            path_length: int = len(path)
            path.append(edge)
            visited.add(edge)
            path.append(other_node)

            if other_node.node.object.is_end():
                return path

            result = self.generate_path(path, visited, deadlock)
            if result is not None:
                return result

            del path[path_length:]
            visited.discard(edge)

        visited.discard(start_node)
        deadlock.add(start_node)
        return None

    @staticmethod
    def get_blocking_flow(path: list[BFSObject]) -> int:
        return min(
            current_object.get_remaining_capacity()
            for current_object in path
        )

    @staticmethod
    def apply_flow(path: list[BFSObject], flow: int) -> None:
        for current_object in path:
            current_object.add_load(flow)

    def store_path(self, path: list[BFSObject], flow: int) -> None:
        for _ in range(flow):
            self.paths.append(path.copy())

    def solve(self) -> None:
        self.logger.log('Running DFS...')

        total_flow: int = 0
        while total_flow < self.network.nb_drones:
            path: list[BFSObject] | None = self.generate_path(
                [self.bfs.start_node],
                set(),
                set()
            )
            if path is None:
                self.bfs.expend()
                continue

            flow: int = self.get_blocking_flow(path)
            self.apply_flow(path, flow)
            self.store_path(path, flow)
            self.logger.log(f'Found path with flow {flow}!')
            total_flow += flow

        self.logger.log(f'Found path with total flow {total_flow}!')
