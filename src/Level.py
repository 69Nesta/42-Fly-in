from .utils import Logger, Color
from .LevelLoader import LevelLoader
from .Connections import Connections
from .Hub import Hub


class Level:
    logger: Logger
    loader: LevelLoader

    nb_drones: int
    hubs: dict[str, Hub]
    connections: Connections

    def __init__(self, loader: LevelLoader, verbose: bool = False):
        self.logger = Logger(
            print_log=loader.verbose,
            name='Level',
            color=Color.YELLOW
        )

        self.hubs = loader.hubs
        self.connections = loader.connections
        self.nb_drones = loader.nb_drones
