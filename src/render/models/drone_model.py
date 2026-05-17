from .collision_model import CollisionModel
from pyray import Model, Vector3, Vector2
from ...utils import Bezier
import pyray as pr
import math


t_drone_animation = tuple[Vector2, float]
"""Type alias for drone animation state: (position, rotation)."""


class DroneModel(CollisionModel):
    """3D model for a delivery drone with animation support.

    Manages drone visualization, movement animations using Bézier curves,
    and collision detection for raycasting.

    Attributes:
        idx: Unique identifier for the drone.
        model: PyRay model for drone geometry.
        collision_model: Cube mesh for collision detection.
        frame_rate: Animation frame rate in FPS.
        animations_pos: Queue of animation frames (position, rotation).
        last_postion: Current drone position and rotation.
    """
    idx: int
    model: Model
    collision_model: Model
    frame_rate: int

    animations_pos: list[t_drone_animation]
    last_postion: t_drone_animation

    def __init__(
                self,
                idx: int,
                frame_rate: int,
                model: Model,
                start: t_drone_animation
            ) -> None:
        """Initialize a drone model.

        Args:
            idx: Unique drone identifier.
            frame_rate: Animation frame rate in FPS.
            model: The PyRay model for drone geometry.
            start: Starting position and rotation tuple.
        """
        super().__init__()
        self.idx = idx
        self.model = model
        self.collision_model = pr.load_model_from_mesh(
            pr.gen_mesh_cube(0.55, 0.8, 0.55)
        )
        self.frame_rate = frame_rate
        self.last_postion = start

        self.init_animations()

    def get_id(self) -> int:
        """Get the drone's unique identifier.

        Returns:
            The drone's ID.
        """
        return self.idx

    def get_pos(self) -> tuple[float, float]:
        """Get the drone's current position.

        Returns:
            Tuple of (x, y) coordinates.
        """
        return (self.last_postion[0].x, self.last_postion[0].y)

    def init_animations(self) -> None:
        """Initialize the animation queue."""
        self.animations_pos = []

    def last_animation_pos(self) -> t_drone_animation:
        """Get the last animation frame or current position.

        Returns:
            Last animation frame if available, otherwise current position.
        """
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
        """Animate drone movement to a new position using Bézier curves.

        Args:
            position: Target position.
            rotation: Target rotation in degrees.
            animation_time: Duration of animation in milliseconds.
        """
        current_pos, current_rot = self.last_animation_pos()
        number_of_frames = round(animation_time / (1000 / self.frame_rate))
        cuve = Bezier(
            current_pos,
            position,
            math.radians(-current_rot),
            math.radians(rotation),
            0.3
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
        """Animate drone movement backward to a position.

        Args:
            position: Target position.
            rotation: Target rotation in degrees.
            animation_time: Duration of animation in milliseconds.
        """
        self.move_to(position, rotation, animation_time)

    def set_position(self, position: Vector2, rotation: float = 0) -> None:
        """Directly set drone position without animation.

        Args:
            position: New position.
            rotation: New rotation in degrees. Defaults to 0.
        """
        self.animations_pos.clear()
        self.animations_pos.append(
            (position, rotation)
        )

    def get_position(self) -> Vector3:
        """Get the drone's 3D world position.

        Returns:
            Vector3 position in world space.
        """
        return Vector3(
            self.last_postion[0].x * 3,
            1.1,
            self.last_postion[0].y * 3
        )

    def get_collision_position(self) -> Vector3:
        """Get the collision model's world position.

        Returns:
            Vector3 position slightly above the drone.
        """
        return Vector3(
            self.last_postion[0].x * 3,
            1.1 + .4,
            self.last_postion[0].y * 3
        )

    def get_collision_model(self) -> Model:
        """Get the collision model for raycasting.

        Returns:
            The collision model mesh.
        """
        return self.collision_model

    def get_collision_rotation_axis(self) -> Vector3:
        """Get the rotation axis for the drone.

        Returns:
            Y-axis (0, 1, 0).
        """
        return Vector3(0, 1, 0)

    def get_collision_rotation(self) -> float:
        """Get the drone's current rotation angle.

        Returns:
            Rotation in degrees.
        """
        return self.last_postion[1]

    def draw(self) -> None:
        """
        Draw the drone model and optionally its collision box if selected.
        """
        if len(self.animations_pos) > 0:
            self.last_postion = self.animations_pos.pop(0)
        _, rotation = self.last_postion

        pr.draw_model_ex(
            self.model,
            self.get_position(),
            Vector3(0, 1, 0),
            rotation - 90,
            Vector3(0.1, 0.1, 0.1),
            pr.WHITE
        )
        if self.is_selected:
            self.is_selected = False
            pr.draw_model_wires_ex(
                self.collision_model,
                self.get_collision_position(),
                Vector3(0, 1, 0),
                rotation,
                Vector3(1, 1, 1),
                pr.WHITE
            )

    def unload(self) -> None:
        """Unload and clean up the collision model."""
        pr.unload_model(self.collision_model)
