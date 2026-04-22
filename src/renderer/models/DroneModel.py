from pyray import Model, Vector3, Vector2
from ...utils import Bezier
import pyray as pr
import math


t_drone_animation = tuple[Vector2, float]  # position, rotation


class DroneModel:
    idx: int
    model: Model
    colliton_model: Model
    frame_rate: int

    animations_pos: list[t_drone_animation]
    last_postion: t_drone_animation

    selected: bool

    def __init__(
                self,
                idx: int,
                frame_rate: int,
                model: Model,
                start: t_drone_animation
            ) -> None:
        self.idx = idx
        self.model = model
        self.colliton_model = pr.load_model_from_mesh(
            pr.gen_mesh_cube(0.55, 0.8, 0.55)
        )
        self.frame_rate = frame_rate
        self.last_postion = start

        self.init_animations()

        self.selected = False

    def get_id(self) -> int:
        return self.idx

    def init_animations(self) -> None:
        self.animations_pos = []

    def last_animation_pos(self) -> t_drone_animation:
        if len(self.animations_pos) > 0:
            return self.animations_pos[-1]
        else:
            return self.last_postion

    def is_selected(self) -> bool:
        return self.selected

    def set_selected(self, selected: bool) -> None:
        self.selected = selected

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
        if self.idx == 0:
            print(
                f"Drone {self.idx} move to {position} with rotation "
                f"{rotation} in {animation_time}ms ({number_of_frames} "
                "frames)"
            )

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

    def get_position(self) -> Vector3:
        return Vector3(self.last_postion[0].x * 3, 1.1, self.last_postion[0].y * 3)

    def get_coll_position(self) -> Vector3:
        return Vector3(self.last_postion[0].x * 3, 1.1 + .4, self.last_postion[0].y * 3)

    def draw(self) -> None:
        if len(self.animations_pos) > 0:
            self.last_postion = self.animations_pos.pop(0)
        _, rotation = self.last_postion

        pr.draw_model_ex(
            self.model,
            self.get_position(),
            Vector3(0, 1, 0),
            rotation + 90,
            Vector3(0.1, 0.1, 0.1),
            pr.WHITE
        )
        if self.is_selected():
            pr.draw_model_wires_ex(
                self.colliton_model,
                self.get_coll_position(),
                Vector3(0, 1, 0),
                rotation,
                Vector3(1, 1, 1),
                pr.WHITE
            )
            self.selected = False

    def unload(self) -> None:
        # pr.unload_model(self.model)
        pr.unload_model(self.colliton_model)
