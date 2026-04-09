from .utils import Logger, Color
from .LevelLoader import LevelLoader
from .Connections import Connections
from .Hub import Hub


class Level:
    logger: Logger

    nb_drones: int
    hubs: dict[str, Hub]
    start_hub: Hub
    connections: Connections

    def __init__(self, loader: LevelLoader, verbose: bool = False):
        self.logger = Logger(
            print_log=verbose,
            name='Level',
            color=Color.YELLOW
        )

        self.hubs = loader.hubs
        self.connections = loader.connections
        self.nb_drones = loader.nb_drones

        for hub in self.hubs.values():
            if hub.is_start:
                self.start_hub = hub
                break
        if not hasattr(self, 'start_hub'):
            raise ValueError('No start hub found in the level')

    def get_hub(self, hub_id: str) -> Hub:
        if hub_id not in self.hubs:
            raise ValueError(f'Hub with id {hub_id} not found')
        return self.hubs[hub_id]

    # @property
    # def connections(self) -> list[Connection]:
    #     return self._connections.get()

    # def get_connection(self, hub: Hub) -> list[Connection]:
    #     return self._connections.get_connection(hub)
