# from .connection_node import ConnectionNode
from ...utils import Logger, Color
from ...network.network import Network
from .node import Node


class TimeGraph:
    logger: Logger

    network: Network
    nodes: list[Node]

    def __init__(self, verbose: bool, network: Network) -> None:
        self.logger = Logger(
            name='TimeGraph',
            print_log=verbose,
            color=Color.GREEN
        )
        self.logger.log('Initializing TimeGraph...')
        self.network = network

        self.nodes: list[Node] = []
