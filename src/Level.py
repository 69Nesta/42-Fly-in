from .Connections import Connections, Connection
from .LevelLoader import LevelLoader
from .utils import Logger, Color
from pyray import Vector2
from .Drone import Drone
from .Hub import Hub
from math import inf


class Level:
    logger: Logger

    nb_drones: int
    hubs: dict[str, Hub]
    start_hub: Hub
    end_hub: Hub
    connections: Connections
    drones: list[Drone]
    number_of_steps: int
    current_step: int

    reservations: dict[Hub, dict[int, int]]
    reservations_connection: dict[Connection, dict[int, int]]

    min_pos: Vector2
    max_pos: Vector2
    height: int
    width: int

    def __init__(self, map_path: str, verbose: bool = False):
        self.logger = Logger(
            print_log=verbose,
            name='Level',
            color=Color.YELLOW
        )
        loader: LevelLoader = LevelLoader(
            filepath=map_path,
            verbose=verbose
        )

        self.hubs = loader.hubs
        self.connections = loader.connections
        self.nb_drones = loader.nb_drones
        self.number_of_steps = 0
        self.current_step = 0
        self.reservations = {}
        self.reservations_connection = {}

        for hub in self.hubs.values():
            if hub.is_start():
                self.start_hub = hub
            elif hub.is_end():
                self.end_hub = hub
            if hasattr(self, 'start_hub') and hasattr(self, 'end_hub'):
                break
        if not hasattr(self, 'start_hub'):
            raise ValueError('No start hub found in the level')
        if not hasattr(self, 'end_hub'):
            raise ValueError('No end hub found in the level')

        self.init_drones()

    def _nodes_positions(self) -> None:
        self.min_pos = Vector2(inf, inf)
        self.max_pos = Vector2(-inf, -inf)

        for hub in self.hubs.values():
            if hub.x < self.min_pos.x:
                self.min_pos.x = hub.x
            if hub.x > self.max_pos.x:
                self.max_pos.x = hub.x
            if hub.y < self.min_pos.y:
                self.min_pos.y = hub.y
            if hub.y > self.max_pos.y:
                self.max_pos.y = hub.y

        self.width = int(self.max_pos.x - self.min_pos.x)
        self.height = int(self.max_pos.y - self.min_pos.y)

    def get_hub(self, hub_id: str) -> Hub:
        if hub_id not in self.hubs:
            raise ValueError(f'Hub with id {hub_id} not found')
        return self.hubs[hub_id]

    def update_number_of_steps(self) -> None:
        self.number_of_steps = max(
            self.number_of_steps,
            max((len(drone.path) for drone in self.drones), default=0)
        )

    def update_step(self, move: int) -> bool:
        if (self.current_step + move < 0 or
           self.current_step + move > self.number_of_steps):
            return False
        self.current_step = min(
            max(0, self.current_step + move), self.number_of_steps
        )
        self.logger.log(
            f'Current step: {self.current_step}/{self.number_of_steps}'
        )
        return True

    def get_current_step(self) -> int:
        return self.current_step

    def init_drones(self) -> None:
        self.logger.log(f'Initializing {self.nb_drones} drones...')
        self.drones = []
        for i in range(self.nb_drones):
            self.drones.append(Drone(
                id=i,
                start_point=Vector2(-1, 0),
                end_point=Vector2(self.end_hub.x + 1, self.end_hub.y)
            ))
        self.logger.log('Drones initialized successfully.')
