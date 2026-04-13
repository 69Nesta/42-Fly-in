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
    drones: list[DroneModel]
    current_step: int = 0

    def __init__(self, level: Level) -> None:
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='DronesRenderer',
            color=Color.BRIGHT_YELLOW
        )
        self.logger.log('Initializing drones renderer...')

        # self.model = DroneModel()
        self.drones = []
        for drone in self.level.drones:
            self.drones.append(DroneModel(
                frame_rate=60,
                start=(drone.get_first_position(), 0)
            ))

    def update(self) -> None:
        if (pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT) or
                pr.is_key_pressed(pr.KeyboardKey.KEY_RIGHT)):
            if self.level.update_step(1):
                for idx, drone in enumerate(self.drones):
                    drone_pos = self.level.drones[idx].get_position_at_step(self.level.current_step)
                    drone.move_to(
                        position=drone_pos,
                        rotation=drone._get_angle_between_points(
                            drone.last_animation_pos()[0],
                            drone_pos
                        ),
                        animation_time=300,
                    )
        elif (pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_RIGHT) or
                pr.is_key_pressed(pr.KeyboardKey.KEY_LEFT)):
            if self.level.update_step(-1):
                for idx, drone in enumerate(self.drones):
                    drone_pos = self.level.drones[idx].get_position_at_step(self.level.current_step)
                    
                    drone.back_to(
                        position=drone_pos,
                        rotation=drone._get_angle_between_points(
                            drone.last_animation_pos()[0],
                            drone_pos
                        ),
                        animation_time=300,
                    )

    def draw(self) -> None:
        for drone in self.drones:
            drone.draw()
        # for drone in self.level.drones:
        #     for step, step_index in drone.path:
        #         if step_index == self.level.current_step:
        #             if isinstance(step, Hub):
        #                 self.model.draw(
        #                     pr.Vector2(step.x, step.y)
        #                 )
        #             elif isinstance(step, Connection):
        #                 self.model.draw(
        #                     step.calculate_middle_point()
        #                 )

    def unload(self) -> None:
        self.logger.log('Unloading drones renderer...')
        for drone in self.drones:
            drone.unload()
