# from pyray import Mesh, Model, Vector3
from ..utils import Logger, Color
from .models import DroneModel
from ..Level import Level
# import pyray as pr


class DronesRenderer:
    level: Level
    logger: Logger

    model: DroneModel
    current_step: int = 0

    def __init__(self, level: Level) -> None:
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='DronesRenderer',
            color=Color.BRIGHT_YELLOW
        )
        self.logger.log('Initializing drones renderer...')

        self.model = DroneModel()

    # def update(self) -> None:

    def draw(self) -> None:
        for drone in self.level.drones:
            for hub, step in drone.path:
                if step == self.current_step:
                    self.model.draw(hub.x, hub.y)
                # self.model.draw(step.x, step.y)

    def unload(self) -> None:
        self.logger.log('Unloading drones renderer...')
        self.model.unload()
