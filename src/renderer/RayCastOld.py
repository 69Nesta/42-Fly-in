from pyray import Vector3, Ray, RayCollision, BoundingBox
from .models import DroneModel, HubModel
from ..utils import Logger, Color
from typing import Any, Optional
from ..Level import Level
import pyray as pr


t_RayCastValues = HubModel | DroneModel


class RayCast:
    level: Level
    logger: Logger

    _entries: dict[int, DroneModel]
    _entries_statics: dict[BoundingBox, t_RayCastValues]

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

    def register_drone(
                self,
                ids: int,
                model: DroneModel,
            ) -> None:
        self.logger.log(
            f'Registering ray cast entry for drone id : {ids!r}'
        )
        self._entries.update({
            ids: model
        })

    def register_hub(
                self,
                model: HubModel,
            ) -> None:
        position: Vector3 = model.get_coll_position()
        self.logger.log(
            f'Registering ray cast static entry for {model.hub.name!r} at '
            f'{position}'
        )
        bounds: BoundingBox = pr.get_mesh_bounding_box(
            model.colliton_model.meshes[0]
        )
        bounds.min = pr.vector3_add(bounds.min, position)
        bounds.max = pr.vector3_add(bounds.max, position)

        self._entries_statics.update({
            (bounds): model
        })

    def cast(self, ray: Ray) -> Optional[t_RayCastValues]:
        best_value: Optional[Any] = None
        best_col: Optional[RayCollision] = None

        for bounds, value in self._entries_statics.items():
            if not pr.get_ray_collision_box(ray, bounds).hit:
                continue
            position: Vector3 = value.get_coll_position()
            transform = pr.matrix_translate(position.x, position.y, position.z)
            col: RayCollision = pr.get_ray_collision_mesh(
                ray, value.colliton_model.meshes[0], transform
            )
            if col.hit:
                if best_col is None or col.distance < best_col.distance:
                    best_value = value
                    best_col = col

        if best_col is not None:
            return best_value

        for _, data in self._entries.items():
            bounds = pr.get_mesh_bounding_box(data.colliton_model.meshes[0])
            bounds.min = pr.vector3_add(bounds.min, data.get_coll_position())
            bounds.max = pr.vector3_add(bounds.max, data.get_coll_position())

            if not pr.get_ray_collision_box(ray, bounds).hit:
                continue

            position = data.get_coll_position()
            transform = pr.matrix_translate(position.x, position.y, position.z)
            col = pr.get_ray_collision_mesh(
                ray, data.colliton_model.meshes[0], transform
            )
            if col.hit:
                if best_col is None or col.distance < best_col.distance:
                    best_value = data
                    best_col = col

        return best_value
