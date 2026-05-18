from ..utils import Logger, Color
from ..network import Network

from .time_graph import TimeGraph
from .bfs import BFS, BFSNode
from .dfs import DFS


class Dinic:
    logger: Logger
    network: Network

    def __init__(self, network: Network, verbose: bool) -> None:
        self.logger = Logger(
            print_log=verbose,
            name='Dinic',
            color=Color.YELLOW
        )
        self.network = network

    def solve(self) -> None:
        self.logger.log('Running Dinic\'s algorithm...')
        verbose: bool = self.logger.print_log

        time_graph: TimeGraph = TimeGraph(
            verbose=self.logger.print_log,
            network=self.network
        )
        bfs: BFS = BFS(verbose, time_graph)
        dfs: DFS = DFS(verbose, bfs, self.network)
        dfs.solve()

        for idx, drone in enumerate(self.network.drones):
            drone.path = [
                step.node
                for step in (dfs.paths[idx] if idx < len(dfs.paths) else [])
                if isinstance(step, BFSNode)
            ]
            self.logger.log(
                f'Drone {drone.id} path: ' +
                str([
                    f'{obj.get_name()} at time {obj.time}'
                    for obj in drone.path
                ])
            )

        self.network.update_simlation_length()
        self.network.create_load_map()

    def print_stats(self) -> None:
        """Print statistics about the planned paths and reservations."""
        self.logger.info('--- Solver Statistics ---')
        self.logger.info(f'Total drones: {len(self.network.drones)}')
        self.logger.info(f'Total steps: {self.network.simulation_length}')
        self.logger.info('--- End of Statistics ---')
