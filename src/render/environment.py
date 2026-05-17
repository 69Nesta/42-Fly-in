from collections import defaultdict
from ..utils import Logger, Color
from ..network import Network
from pyray import Vector2
from enum import Enum
import random


class EEnvironmentObject(Enum):
    """Environment object types for grid cells."""
    EMPTY = 0
    START_NODE = 1
    NODE = 2
    END_NODE = 3
    BLOCKED_NODE = 9


object_weights: dict[EEnvironmentObject, float] = {}


def get_x(vec: Vector2) -> int:
    """Get the X coordinate from a Vector2.

    Args:
        vec: Vector2 instance.

    Returns:
        X coordinate as integer.
    """
    return int(vec.x)


def get_y(vec: Vector2) -> int:
    """Get the Y coordinate from a Vector2.

    Args:
        vec: Vector2 instance.

    Returns:
        Y coordinate as integer.
    """
    return int(vec.y)


class Environment:
    """Manages the 2D grid environment for pathfinding visualization.

    Converts the level topology into a discrete grid map and tracks
    environment objects at grid positions.

    Attributes:
        logger: Logger for debug output.
        network: The network instance.
        environment_height: Grid height in cells.
        environment_width: Grid width in cells.
        SCALE: Scaling factor for grid granularity.
        PADDING_X: Horizontal padding around network bounds.
        PADDING_Y: Vertical padding around network bounds.
        offset_x: X offset for grid-to-world conversion.
        offset_y: Y offset for grid-to-world conversion.
        environment_map: 2D grid mapping positions to objects.
    """
    logger: Logger
    network: Network

    environment_height: int
    environment_width: int
    SCALE: int = 3
    PADDING_X: int = 5
    PADDING_Y: int = 1
    offset_x: float
    offset_y: float

    environment_map: dict[int, dict[int, EEnvironmentObject]]

    def __init__(self, network: Network) -> None:
        """Initialize the environment grid.

        Args:
            network: The network instance.
        """
        self.logger = Logger(
            print_log=network.logger.print_log,
            name='Environment',
            color=Color.CYAN
        )
        self.network = network

        self.offset_x = -self.PADDING_X + (
            self.network.min_pos.x * self.SCALE
        )
        self.offset_y = -self.PADDING_Y + (
            self.network.min_pos.y * self.SCALE
        )

        self.init_environment()
        self.init_environment_map()
        self.pre_fill_environment_map()

    def init_environment_map(self) -> None:
        """Initialize the environment grid as nested defaultdicts."""
        self.environment_map = defaultdict(
            lambda: defaultdict(lambda: EEnvironmentObject.EMPTY)
        )

    def init_environment(self) -> None:
        """Calculate grid dimensions based on network bounds and scale."""
        self.logger.log('Initializing environment...')
        self.environment_height = 1 + (
            self.network.height * self.SCALE + (self.PADDING_Y * 2)
        )
        self.environment_width = 1 + (
            self.network.width * self.SCALE + (self.PADDING_X * 2)
        )

    def pre_fill_environment_map(self) -> None:
        """Populate grid with hubs, start, and end positions."""
        pos: Vector2
        pos = self.calculate_2d_position_vec(
            self.network.get_drone_start_position()
        )
        self.environment_map[get_y(pos)][get_x(pos)] = \
            EEnvironmentObject.START_NODE
        pos = self.calculate_2d_position_vec(
            self.network.get_drone_end_position()
        )
        self.environment_map[get_y(pos)][get_x(pos)] = \
            EEnvironmentObject.END_NODE

        for node in self.network.nodes:
            pos = self.calculate_2d_position(node.x, node.y)
            self.environment_map[get_y(pos)][get_x(pos)] = (
                EEnvironmentObject.NODE
                if not node.is_blocked() else
                EEnvironmentObject.BLOCKED_NODE
            )

    def calculate_2d_position(self, x: float, y: float) -> Vector2:
        """Convert world coordinates to grid coordinates.

        Args:
            x: World X coordinate.
            y: World Y coordinate.

        Returns:
            Vector2 with grid coordinates.
        """
        normalized_x = x - self.network.min_pos.x
        normalized_y = y - self.network.min_pos.y
        return Vector2(
            normalized_x * self.SCALE + self.PADDING_X,
            normalized_y * self.SCALE + self.PADDING_Y
        )

    def calculate_2d_position_vec(self, vec: Vector2) -> Vector2:
        """Convert a Vector2 from world to grid coordinates.

        Args:
            vec: World position vector.

        Returns:
            Vector2 with grid coordinates.
        """
        return self.calculate_2d_position(vec.x, vec.y)

    def fill_environment_map(
                self,
                seed: int | float | str | None,
                fill_percent: float,
                object_weights: dict[EEnvironmentObject, float]
            ) -> None:
        """Randomly fill environment grid with objects.

        Args:
            seed: Random seed for reproducibility.
            fill_percent: Probability of placing an object in each cell.
            object_weights: Weight distribution for object types.
        """
        random.seed(seed)
        objects = list(object_weights.keys())
        weights = list(object_weights.values())

        for x in range(self.environment_width):
            for y in range(self.environment_height):
                if (random.random() < fill_percent
                   and self.environment_map[y][x] == EEnvironmentObject.EMPTY):
                    self.environment_map[y][x] = random.choices(
                        objects, weights=weights
                    )[0]
                    self.logger.log(
                        f'Placed {self.environment_map[y][x].name} at '
                        f'({x}, {y})'
                    )
