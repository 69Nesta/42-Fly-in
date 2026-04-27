from ..utils import Logger, Color
from ..Level import Level
from pyray import Vector3
import pyray as pr


class ConnectionRenderer:
    level: Level
    logger: Logger

    def __init__(self, level: Level) -> None:
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='ConnectionRenderer',
            color=Color.BLUE
        )
        self.logger.log('Initializing hub renderer...')

    def update(self) -> None:
        pass

    def draw(self) -> None:
        for connection in self.level.connections.all:
            pr.draw_line_3d(
                Vector3(connection.hubs[0].x * 3, 1.1, connection.hubs[0].y*3),
                Vector3(connection.hubs[1].x * 3, 1.1, connection.hubs[1].y*3),
                pr.RED
            )

    def unload(self) -> None:
        self.logger.log('Unloading connection renderer...')
        pass
