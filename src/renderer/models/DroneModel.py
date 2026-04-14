from pyray import Model, Vector3, Vector2
from ...utils import Bezier
import pyray as pr
import math


t_drone_animation = tuple[Vector2, float]  # position, rotation


class DroneModel:
    model: Model
    frame_rate: int

    animations_pos: list[t_drone_animation]
    last_postion: t_drone_animation

    def __init__(self, frame_rate: int, start: t_drone_animation) -> None:
        self.model = pr.load_model('src/assets/models/boat.glb')
        self.frame_rate = frame_rate
        self.last_postion = start

        self.init_animations()

    def init_animations(self) -> None:
        self.animations_pos = []

    def last_animation_pos(self) -> t_drone_animation:
        if len(self.animations_pos) > 0:
            return self.animations_pos[-1]
        else:
            return self.last_postion

    def move_to(
                self,
                position: Vector2,
                rotation: float,
                animation_time: int
            ) -> None:
        current_pos, current_rot = self.last_animation_pos()
        number_of_frames = round(animation_time / (1000 / self.frame_rate))
        cuve = Bezier(
            current_pos,
            position,
            math.radians(current_rot),
            math.radians(rotation),
            0.5
        )

        for i in range(number_of_frames):
            cuve_time = i / (number_of_frames - 1)
            pos = cuve.bezier_point(cuve_time)
            rot = -cuve.bezier_rotation(cuve_time)

            self.animations_pos.append((
                pos,
                rot
            ))

    def back_to(
                self,
                position: Vector2,
                rotation: float,
                animation_time: int
            ) -> None:
        self.move_to(position, rotation, animation_time)

    def set_position(self, position: Vector2, rotation: float = 0) -> None:
        self.animations_pos.clear()
        self.animations_pos.append(
            (position, rotation)
        )

    @staticmethod
    def _get_angle_between_points(p1: Vector2, p2: Vector2) -> float:
        return math.atan2(p2.y - p1.y, p2.x - p1.x) * (180 / math.pi)

    def draw(self) -> None:
        if len(self.animations_pos) > 0:
            self.last_postion = self.animations_pos.pop(0)
        position, rotation = self.last_postion

        pr.draw_model_ex(
            self.model,
            Vector3(position.x, 1.0, position.y),
            Vector3(0, 1, 0),
            rotation + 90,
            Vector3(0.1, 0.1, 0.1),
            pr.WHITE
        )

    def unload(self) -> None:
        pr.unload_model(self.model)
