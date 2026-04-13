from ..Connections import Connection
from ..utils import Logger, Color
from .models import DroneModel
from ..Level import Level
from ..Hub import Hub
import pyray as pr


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

    def update(self) -> None:
        if (pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT) or
                pr.is_key_pressed(pr.KeyboardKey.KEY_RIGHT)):
            self.level.update_step(1)
        elif (pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_RIGHT) or
                pr.is_key_pressed(pr.KeyboardKey.KEY_LEFT)):
            self.level.update_step(-1)

    def draw(self) -> None:
        for drone in self.level.drones:
            for step, step_index in drone.path:
                if step_index == self.level.current_step:
                    if isinstance(step, Hub):
                        self.model.draw_from_vector(
                            pr.Vector2(step.x, step.y)
                        )
                    elif isinstance(step, Connection):
                        self.model.draw_from_vector(
                            step.calculate_middle_point()
                        )

    def unload(self) -> None:
        self.logger.log('Unloading drones renderer...')
        self.model.unload()
