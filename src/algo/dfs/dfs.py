from ...utils import Logger, Color
from ..bfs import BFSEdge, BFSNode, BFSObject
from ..time_graph import TimeGraph, Node  # noqa: F401

# from collections import deque


class DFS:
    logger: Logger
    time_graph: TimeGraph

    nodes: list[BFSNode]
    edges: list[BFSEdge]
    path: list[BFSObject]

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
        self.path = []

    def run(self) -> None:
        self.logger.log('Running DFS...')
        self.logger.error('DFS is not implemented yet.')
