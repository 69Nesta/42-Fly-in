from ...utils import Logger, Color
from .dfs_edge import DFSEdge  # noqa: F401
from .dfs_node import DFSNode  # noqa: F401
from ..time_graph import TimeGraph


class DFS:
    logger: Logger
    time_graph: TimeGraph

    nodes: list[DFSNode]
    edges: list[DFSEdge]

    def __init__(self, verbose: bool, time_graph: TimeGraph) -> None:
        self.logger = Logger(
            name='DFS',
            print_log=verbose,
            color=Color.CYAN
        )
        self.logger.log('Initializing DFS...')
        self.time_graph = time_graph

        self.nodes = []
        self.edges = []
