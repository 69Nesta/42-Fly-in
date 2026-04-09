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
            color=Color.GREEN
        )
        self.logger.log('Initializing hub renderer...')

    def update(self) -> None:
        pass

    def draw(self) -> None:
        for connection in self.level.connections.get():
            pr.draw_line_3d(
                Vector3(connection.hubs[0].x, 0, connection.hubs[0].y),
                Vector3(connection.hubs[1].x, 0, connection.hubs[1].y),
                pr.RED
            )

    def unload(self) -> None:
        pass
        # self.logger.log('Unloading hub renderer...')
        # pr.unload_model(self.hub_model)
