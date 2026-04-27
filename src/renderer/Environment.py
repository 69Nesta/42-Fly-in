from collections import defaultdict
from ..utils import Logger, Color
from ..Level import Level
from pyray import Vector2
from enum import Enum
import random


class EEnvironmentObject(Enum):
    EMPTY = 0
    START_NODE = 1
    NODE = 2
    END_NODE = 3
    BLOCKED_NODE = 9


object_weights: dict[EEnvironmentObject, float] = {}


class Environment:
    logger: Logger
    level: Level

    environment_height: int
    environment_width: int
    SCALE: float = 3
    PADDING_X: int = 5
    PADDING_Y: int = 1
    offset_x: float
    offset_y: float

    environment_map: dict[int, dict[int, EEnvironmentObject]]

    def __init__(self, level: Level) -> None:
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='Environment',
            color=Color.CYAN
        )
        self.level = level

        self.offset_x = -self.PADDING_X + (
            self.level.min_pos.x * self.SCALE
        )
        self.offset_y = -self.PADDING_Y + (
            self.level.min_pos.y * self.SCALE
        )

        self.init_environment()
        self.init_environment_map()
        self.pre_fill_environment_map()

    def init_environment_map(self) -> None:
        self.environment_map = defaultdict(
            lambda: defaultdict(lambda: EEnvironmentObject.EMPTY)
        )

    def init_environment(self):
        self.logger.log('Initializing environment...')
        self.environment_height = 1 + (
            self.level.height * self.SCALE + (self.PADDING_Y * 2)
        )
        self.environment_width = 1 + (
            self.level.width * self.SCALE + (self.PADDING_X * 2)
        )

    def pre_fill_environment_map(self) -> None:
        pos: Vector2
        pos = self.calculate_2d_position_vec(
            self.level.get_drone_start_position()
        )
        self.environment_map[pos.y][pos.x] = EEnvironmentObject.START_NODE
        pos = self.calculate_2d_position_vec(
            self.level.get_drone_end_position()
        )
        self.environment_map[pos.y][pos.x] = EEnvironmentObject.END_NODE

        for node in self.level.hubs.values():
            pos = self.calculate_2d_position(node.x, node.y)
            self.environment_map[pos.y][pos.x] = (
                EEnvironmentObject.NODE
                if not node.is_blocked() else
                EEnvironmentObject.BLOCKED_NODE
            )

    def calculate_2d_position(self, x: int, y: int) -> Vector2:
        normalized_x = x - self.level.min_pos.x
        normalized_y = y - self.level.min_pos.y
        return Vector2(
            normalized_x * self.SCALE + self.PADDING_X,
            normalized_y * self.SCALE + self.PADDING_Y
        )

    def calculate_2d_position_vec(self, vec: Vector2) -> Vector2:
        return self.calculate_2d_position(vec.x, vec.y)

    def fill_environment_map(
                self,
                seed: int | float | str | None,
                fill_percent: float,
                object_weights: dict[EEnvironmentObject, float]
            ) -> None:
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
