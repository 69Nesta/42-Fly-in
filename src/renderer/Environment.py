from ..utils import Logger, Color
# from .models import DroneModel
from ..Level import Level
from enum import Enum


class EEnvironmentObject(Enum):
    EMPTY = 0
    START_NODE = 1
    NODE = 2
    END_NODE = 3


def make_even(n):
    return n if n % 2 == 0 else n + 1


class Environment:
    logger: Logger
    level: Level

    environment_height: int
    environment_width: int
    # environment_map: list[list[EEnvironmentObject]]

    def __init__(self, level: Level) -> None:
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='Environment',
            color=Color.CYAN
        )
        self.level = level

        self.init_environment()

    def init_environment(self):
        self.logger.log('Initializing environment...')
        self.environment_height = make_even(self.level.height * 3 + (3 * 2))
        self.environment_width = make_even(self.level.width * 3 + (3 * 2))
        # self.environment_map = [
        #     [
        #         EEnvironmentObject.EMPTY
        #         for _ in range(self.environment_width)
        #     ]
        #     for _ in range(self.environment_height)
        # ]
        # for node in self.level.hubs.values():
        #     if node.is_start():
        #         self.environment_map[node.y][node.x] = \
        # EEnvironmentObject.START_NODE
        #     elif node.is_end():
        #         self.environment_map[node.y][node.x] = \
        # EEnvironmentObject.END_NODE
        #     else:
        #         self.environment_map[node.y][node.x] = \
        # EEnvironmentObject.NODE
