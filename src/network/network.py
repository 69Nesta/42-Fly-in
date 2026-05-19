from ..algo.time_graph import ConnectionNode
from ..map_loader import MapLoader
from ..utils import Logger, Color
from . import Node, Connection
from .drone import Drone

from collections import defaultdict
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

    load_map: dict[tuple[Node, int], list[Drone]]

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

    def create_load_map(self) -> None:
        """Create a mapping of drones to node/step positions.

        Builds a dictionary keyed by (node, step) containing lists of drones
        at those positions during simulation.
        """
        self.load_map = defaultdict(list)

        for drone in self.drones:
            if drone.path is None:
                continue
            for step, node in enumerate(drone.path):
                if isinstance(node, ConnectionNode):
                    continue
                key = (node.object, step)
                self.load_map[key].append(drone)

            for step in range(len(drone.path), self.simulation_length + 1):
                key = (self.end_node, step)
                self.load_map[key].append(drone)

    def update_simlation_length(self) -> None:
        """Update the total simulation length based on drone paths.

        Sets simulation_length to the maximum path length minus one.
        """
        self.simulation_length = 0
        for drone in self.drones:
            if (drone.path is not None and
               len(drone.path) > self.simulation_length):
                self.simulation_length = len(drone.path)
        self.simulation_length -= 1

    def _calculate_height_and_width(self) -> None:
        """Calculate network dimensions from node positions.

        Computes min/max coordinates and calculates width and height.
        """
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

    def unload(self) -> None:
        """Clear caches and drop references to help GC between runs.

        This clears per-node and per-drone caches and empties main lists so
        subsequent map loads don't retain references to previous map objects.
        """
        try:
            self.logger.log('Unloading network and clearing caches...')
        except Exception:
            pass

        for node in list(getattr(self, 'nodes', []) or []):
            try:
                node.unload()
            except Exception:
                pass

        for drone in list(getattr(self, 'drones', []) or []):
            try:
                drone._cached_positions.clear()
            except Exception:
                pass

        if getattr(self, 'load_map', None) is not None:
            try:
                self.load_map.clear()
            except Exception:
                pass

        try:
            self.nodes.clear()
        except Exception:
            pass
        try:
            self.connections.clear()
        except Exception:
            pass
        try:
            self.drones.clear()
        except Exception:
            pass
        try:
            del self.loaded_map
        except Exception:
            pass
