from pyray import Model, Vector3, Vector2
import pyray as pr
import math


t_drone_animation = tuple[Vector2, float]  # position, rotation


class DroneModel:
    model: Model
    frame_rate: int

    animations_pos: list[t_drone_animation]
    last_postion: t_drone_animation

    def __init__(self) -> None:
        self.model = pr.load_model('src/assets/models/boat.glb')

    def init_animations(self) -> None:
        self.animations_pos = []

    def last_animation_pos(self) -> t_drone_animation:
        if len(self.animations_pos) > 0:
            return self.animations_pos[-1]
        else:
            return self.last_postion

    # def move_to(
    #             self,
    #             position: Vector2,
    #             rotation: float,
    #             animation_time: int
    #         ) -> None:
    #     current_pos, current_rot = self.last_animation_pos()
    #     number_of_frames = round(animation_time / (1000 / self.frame_rate))
    #     middle_rotation: float = self._get_angle_between_points(
    #         current_pos,
    #         position
    #     )

    #     for i in range(number_of_frames):
    #         # push the position of the drone at each frame to the list of
    #         # animations
    #         pos = Vector2(
    #             current_pos.x + (position.x - current_pos.x) * (i / number_of_frames),
    #             current_pos.y + (position.y - current_pos.y) * (i / number_of_frames)
    #         )
    #         rot = current_rot + (rotation - current_rot) * (i / number_of_frames)

    #         self.animations_pos.append((
    #             pos,
    #             rot
    #         ))

    def set_position(self, position: Vector2, rotation: float = 0) -> None:
        self.animations_pos.clear()
        self.animations_pos.append(
            (position, rotation)
        )

    @staticmethod
    def _get_angle_between_points(p1: Vector2, p2: Vector2) -> float:
        return math.atan2(p2.y - p1.y, p2.x - p1.x) * (180 / math.pi)

    def draw(self, x: int, y: int) -> None:
        pr.draw_model_ex(
            self.model,
            Vector3(x, 1.0, y),
            Vector3(0, 1, 0),
            90,
            Vector3(0.1, 0.1, 0.1),
            pr.WHITE
        )

    def draw_from_vector(self, position: Vector2) -> None:
        pr.draw_model_ex(
            self.model,
            Vector3(position.x, 1.0, position.y),
            Vector3(0, 1, 0),
            90,
            Vector3(0.1, 0.1, 0.1),
            pr.WHITE
        )

    def unload(self) -> None:
        pr.unload_model(self.model)
