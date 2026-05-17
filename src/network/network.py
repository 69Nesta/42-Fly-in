from ..map_loader import MapLoader
from ..utils import Logger, Color
from ..Drone import Drone
from . import Node, Connection

from pyray import Vector2
from math import inf


class Network:
    logger: Logger
    loaded_map: MapLoader

    nb_drones: int
    start_node: Node
    end_node: Node

    nodes: list[Node]
    connections: list[Connection]
    drones: list[Drone]

    simulation_length: int
    current_step: int

    min_pos: Vector2
    max_pos: Vector2
    height: int
    width: int

    def __init__(self, loaded_map: MapLoader, verbose: bool) -> None:
        self.logger = Logger(
            print_log=verbose,
            name='Network',
            color=Color.CYAN
        )
        self.loaded_map = loaded_map
        self.logger.log('Initializing the network...')

        self.nb_drones = loaded_map.nb_drones

        self.start_node = loaded_map.get_start_node()
        self.end_node = loaded_map.get_end_node()

        self.nodes = list(loaded_map.nodes.values())
        self.connections = loaded_map.connections.all
        self.drones = []

        self.simulation_length = 0
        self.current_step = 0

        self._calculate_height_and_width()
        self._create_drones()

    # def create_load_map()

    def update_step(self, move: int) -> bool:
        """Move the simulation step forward or backward.

        Args:
            move: Number of steps to move (positive or negative).

        Returns:
            True if step was updated successfully, False if out of bounds.
        """

        if (self.current_step + move < 0 or
           self.current_step + move > self.simulation_length):
            return False
        self.current_step = min(
            max(0, self.current_step + move), self.simulation_length
        )
        self.logger.log(
            f'Current step: {self.current_step}/{self.simulation_length}'
        )
        return True

    def get_drone_start_position(self) -> Vector2:
        """Get the starting position for drones.

        Returns:
            Vector2 position offset to the left of the start node.
        """
        pos: Vector2 = self.start_node.get_position()
        return Vector2(pos.x - 1, pos.y)

    def get_drone_end_position(self) -> Vector2:
        """Get the ending position for drones.

        Returns:
            Vector2 position offset to the right of the end node.
        """
        pos: Vector2 = self.end_node.get_position()
        return Vector2(pos.x + 1, pos.y)

    def _create_drones(self) -> None:
        """Create all drones with starting and ending positions.

        Creates nb_drones Drone objects with default paths.
        """

        self.logger.log('Creating drones...')
        self.drones = []
        for i in range(self.nb_drones):
            self.drones.append(Drone(
                id=i,
                start_point=self.get_drone_start_position(),
                end_point=self.get_drone_end_position(),
            ))
        self.logger.log('Drones initialized successfully.')

    def _update_simlation_length(self) -> None:
        self.simulation_length = 0
        for drone in self.drones:
            if (drone.path is not None and
               len(drone.path) > self.simulation_length):
                self.simulation_length = len(drone.path)
        self.simulation_length -= 1

    def _calculate_height_and_width(self) -> None:
        self.logger.log('Calculating network dimensions...')
        self.min_pos = Vector2(inf, inf)
        self.max_pos = Vector2(-inf, -inf)

        for node in self.nodes:
            if node.x < self.min_pos.x:
                self.min_pos.x = node.x
            if node.x > self.max_pos.x:
                self.max_pos.x = node.x
            if node.y < self.min_pos.y:
                self.min_pos.y = node.y
            if node.y > self.max_pos.y:
                self.max_pos.y = node.y

        self.width = int(self.max_pos.x - self.min_pos.x)
        self.height = int(self.max_pos.y - self.min_pos.y)
