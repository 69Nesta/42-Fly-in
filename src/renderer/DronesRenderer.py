# from ..Connections import Connection
from ..utils import Logger, Color
from .models import DroneModel
from .RayCast import RayCast
from ..Level import Level
# from ..Hub import Hub
import pyray as pr


class DronesRenderer:
    level: Level
    logger: Logger
    raycast: RayCast

    drones: list[DroneModel]
    current_step: int = 0
    ANNIMATION_DURATION: int = 500

    def __init__(self, level: Level, ray_cast: RayCast) -> None:
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='DronesRenderer',
            color=Color.BRIGHT_YELLOW
        )
        self.logger.log('Initializing drones renderer...')
        self.raycast = ray_cast

        self.drones = []
        for idx, drone in enumerate(self.level.drones):
            model: DroneModel = DroneModel(
                idx=idx,
                frame_rate=60,
                start=(drone.get_position_at_step(0), 0)
            )
            self.drones.append(model)
            self.raycast.register(idx, model)

    def update(self) -> None:
        if (pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT) or
                pr.is_key_pressed(pr.KeyboardKey.KEY_RIGHT)):
            if self.level.update_step(1):
                for idx, drone in enumerate(self.drones):
                    drone_pos = self.level.drones[idx].get_position_at_step(
                        self.level.current_step
                    )
                    drone.move_to(
                        position=drone_pos,
                        rotation=drone._get_angle_between_points(
                            drone.last_animation_pos()[0],
                            drone_pos
                        ),
                        animation_time=self.ANNIMATION_DURATION,
                    )
        elif (pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_RIGHT) or
                pr.is_key_pressed(pr.KeyboardKey.KEY_LEFT)):
            if self.level.update_step(-1):
                for idx, drone in enumerate(self.drones):
                    drone_pos = self.level.drones[idx].get_position_at_step(
                        self.level.current_step
                    )
                    drone.back_to(
                        position=drone_pos,
                        rotation=drone._get_angle_between_points(
                            drone.last_animation_pos()[0],
                            drone_pos
                        ),
                        animation_time=self.ANNIMATION_DURATION,
                    )

    def draw(self) -> None:
        for drone in self.drones:
            drone.draw()

    def unload(self) -> None:
        self.logger.log('Unloading drones renderer...')
        for drone in self.drones:
            drone.unload()
