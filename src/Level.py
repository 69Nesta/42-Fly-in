from .Connections import Connections, Connection
from .LevelLoader import LevelLoader
from .utils import Logger, Color
from pyray import Vector2
from .Drone import Drone
from .Hub import Hub
from math import inf


class Level:
    """Represents the complete delivery network level/map.

    Manages the state of hubs, connections, drones, and their reservations.
    Tracks simulation steps and handles drone initialization.

    Attributes:
        logger: Logger instance for debug/info messages.
        nb_drones: Number of drones in the level.
        hubs: Dictionary of all hubs indexed by name.
        start_hub: The starting hub for drone routes.
        end_hub: The destination hub for drone routes.
        connections: All connections between hubs.
        drones: List of drones in the simulation.
        number_of_steps: Total simulation steps in the solution.
        current_step: Current step in the simulation playback.
        reservations: Hub reservation tracking (hub -> time -> count).
        reservations_connection: Connection reservation tracking
        (connection-> time -> count).
        min_pos: Minimum position coordinates of all hubs.
        max_pos: Maximum position coordinates of all hubs.
        height: Height of the bounding box.
        width: Width of the bounding box.
    """
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
        """Initialize a level from a map file.

        Args:
            map_path: Path to the map file to load.
            verbose: Whether to enable verbose logging. Defaults to False.

        Raises:
            ValueError: If the map is missing start/end hubs or is invalid.
        """
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
        self._nodes_positions()

    def _nodes_positions(self) -> None:
        """Calculate bounding box of all hubs.

        Sets min_pos, max_pos, width, and height based on hub coordinates.
        """
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
        """Get a hub by its ID.

        Args:
            hub_id: The hub's unique identifier.

        Returns:
            The Hub object with the given ID.

        Raises:
            ValueError: If no hub with the given ID exists.
        """
        if hub_id not in self.hubs:
            raise ValueError(f'Hub with id {hub_id} not found')
        return self.hubs[hub_id]

    def update_number_of_steps(self) -> None:
        """Update the total number of simulation steps.

        Sets number_of_steps to the maximum path length across all drones.
        """
        self.number_of_steps = max(
            self.number_of_steps,
            max((len(drone.path) for drone in self.drones), default=0)
        )

    def update_step(self, move: int) -> bool:
        """Move the simulation step forward or backward.

        Args:
            move: Number of steps to move (positive or negative).

        Returns:
            True if step was updated successfully, False if out of bounds.
        """
        if (self.current_step + move < 0 or
           self.current_step + move > self.number_of_steps - 1):
            return False
        self.current_step = min(
            max(0, self.current_step + move), self.number_of_steps - 1
        )
        self.logger.log(
            f'Current step: {self.current_step}/{self.number_of_steps - 1}'
        )
        return True

    def get_current_step(self) -> int:
        """Get the current simulation step.

        Returns:
            The current step number.
        """
        return self.current_step

    def get_drone_start_position(self) -> Vector2:
        """Get the starting position for drones.

        Returns:
            Vector2 position offset to the left of the start hub.
        """
        pos: Vector2 = self.start_hub.get_position()
        return Vector2(pos.x - 1, pos.y)

    def get_drone_end_position(self) -> Vector2:
        """Get the ending position for drones.

        Returns:
            Vector2 position offset to the right of the end hub.
        """
        pos: Vector2 = self.end_hub.get_position()
        return Vector2(pos.x + 1, pos.y)

    def init_drones(self) -> None:
        """Initialize all drones with starting and ending positions.

        Creates nb_drones Drone objects with default paths.
        """
        self.logger.log(f'Initializing {self.nb_drones} drones...')
        self.drones = []
        for i in range(self.nb_drones):
            self.drones.append(Drone(
                id=i,
                start_point=self.get_drone_start_position(),
                end_point=self.get_drone_end_position(),
            ))
        self.logger.log('Drones initialized successfully.')
