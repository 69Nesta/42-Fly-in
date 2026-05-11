from ..map_loader import MapLoader
from ..utils import Logger, Color
from ..Drone import Drone
from . import Node, Connection


class Network:
    logger: Logger
    loaded_map: MapLoader

    nb_drones: int
    start_node: Node
    end_node: Node

    nodes: list[Node]
    connections: list[Connection]
    drones: list[Drone]

    def __init__(self, loaded_map: MapLoader, verbose: bool) -> None:
        self.logger = Logger(
            print_log=verbose,
            name='Network',
            color=Color.CYAN
        )
        self.loaded_map = loaded_map
        self.logger.log('Initializing the network...')

        self.nb_drones = loaded_map.nb_drones
        self.nodes = list(loaded_map.nodes.values())
        self.connections = loaded_map.connections.all
        self.drones = []

        self.start_node = loaded_map.get_start_node()
        self.end_node = loaded_map.get_end_node()

    def _create_drones(self) -> None:
        self.logger.log('Creating drones...')
        raise NotImplementedError(
            'Method _create_drones is not implemented yet.'
        )
