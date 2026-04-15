from ..utils import Logger, Color
from ..Level import Level
from ..Hub import Hub
from ..Drone import Drone
from pyray import Model, Vector3, Ray, RayCollision, BoundingBox
from typing import Any, Optional
import pyray as pr


t_RayCastValues = Hub | Drone


class RayCast:
    level: Level
    logger: Logger

    _entries: dict[tuple[Model, Vector3], t_RayCastValues]
    _entries_statics: dict[tuple[Model, Vector3, BoundingBox], t_RayCastValues]

    def __init__(self, level: Level) -> None:
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='RayCast',
            color=Color.YELLOW
        )
        self.logger.log('Initializing ray cast...')

        self._entries = {}
        self._entries_statics = {}

    def register(
                self,
                model: Model,
                position: Vector3,
                data: t_RayCastValues
            ) -> None:
        self.logger.log(
            f'Registering ray cast entry for {data!r} at {position}'
        )
        self._entries.update({
            (model, position): data
        })

    def register_static(
                self,
                model: Model,
                position: Vector3,
                data: t_RayCastValues
            ) -> None:
        self.logger.log(
            f'Registering ray cast static entry for {data!r} at {position}'
        )
        bounds: BoundingBox = pr.get_mesh_bounding_box(model.meshes[0])
        bounds.min = pr.vector3_add(bounds.min, position)
        bounds.max = pr.vector3_add(bounds.max, position)

        self._entries_statics.update({
            (model, position, bounds): data
        })

    def cast(self, ray: Ray) -> Optional[t_RayCastValues]:
        best_value: Optional[Any] = None
        best_col: Optional[RayCollision] = None

        for (entry, position, bounds), value in self._entries_statics.items():
            if not pr.get_ray_collision_box(ray, bounds).hit:
                continue

            transform = pr.matrix_translate(position.x, position.y, position.z)
            col: RayCollision = pr.get_ray_collision_mesh(
                ray, entry.meshes[0], transform
            )
            if col.hit:
                if best_col is None or col.distance < best_col.distance:
                    best_value = value
                    best_col = col

        if best_col is not None:
            return best_value

        for (entry, position), value in self._entries.items():
            bounds = pr.get_mesh_bounding_box(entry.meshes[0])
            bounds.min = pr.vector3_add(bounds.min, position)
            bounds.max = pr.vector3_add(bounds.max, position)

            if not pr.get_ray_collision_box(ray, bounds).hit:
                continue

            col = pr.get_ray_collision_mesh(
                ray, entry.meshes[0], entry.transform
            )
            if col.hit:
                if best_col is None or col.distance < best_col.distance:
                    best_value = value
                    best_col = col

        return best_value
