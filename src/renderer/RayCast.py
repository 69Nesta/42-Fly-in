from pyray import Vector3, Ray, RayCollision, BoundingBox, Matrix
from .models import CollisionModel
from ..utils import Logger, Color
from typing import Optional
from ..Level import Level
import pyray as pr


class RayCast:
    level: Level
    logger: Logger

    _entries: dict[CollisionModel, BoundingBox]

    def __init__(self, level: Level) -> None:
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='RayCast',
            color=Color.YELLOW
        )
        self.logger.log('Initializing ray cast...')

        self._entries = {}

    def register(self, model: CollisionModel) -> None:
        position: Vector3 = model.get_collision_position()
        bounds: BoundingBox = pr.get_mesh_bounding_box(
            model.get_collision_model().meshes[0]
        )

        self.logger.log(
            f'Registering ray cast static entry for {model!r} at '
            f'{position}'
        )

        self._entries.update({
            model: bounds
        })

    def cast(self, ray: Ray) -> CollisionModel | None:
        best_value: Optional[CollisionModel] = None
        best_col: Optional[RayCollision] = None
        bounds: BoundingBox = BoundingBox()

        for model, local_bounds in self._entries.items():
            position: Vector3 = model.get_collision_position()

            bounds.min = pr.vector3_add(local_bounds.min, position)
            bounds.max = pr.vector3_add(local_bounds.max, position)

            if not pr.get_ray_collision_box(ray, bounds).hit:
                continue

            translation: Matrix = pr.matrix_translate(
                position.x, position.y, position.z
            )
            rotation: Matrix = pr.matrix_rotate(
                model.get_collision_rotation_axis(),
                model.get_collision_rotation()
            )

            transform: Matrix = pr.matrix_multiply(rotation, translation)
            col: RayCollision = pr.get_ray_collision_mesh(
                ray, model.get_collision_model().meshes[0], transform
            )
            if col.hit:
                if best_col is None or col.distance < best_col.distance:
                    best_value = model
                    best_col = col

        if best_value is not None:
            best_value.set_selected(True)
        return best_value
