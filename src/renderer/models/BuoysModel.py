from ...Level import Level
from pyray import Model, Mesh
import pyray as pr
# import math


class BuoysModel:
    level: Level

    mesh: Mesh
    model: Model

    def __init__(self, level: Level) -> None:
        self.level = level

        self.mesh = pr.gen_mesh_sphere(0.5, 16, 16)
        self.model = pr.load_model_from_mesh(self.mesh)

    def update(self, _: float) -> None:
        pass

    def draw(self) -> None:
        pass
        # for _, _, pos in self.level.connections.get_intersections():
        #     print('intersection at', pos)
        #     pr.draw_model(
        #         self.model,
        #         Vector3(pos.x, 0, pos.y),
        #         1.0,
        #         pr.RED
        #     )
        # pr.draw_model_ex(
        #     self.model,
        #     Vector3(1.0, 1.0, 1.0),
        #     Vector3(0, 1, 0),
        #     0,
        #     Vector3(0.1, 0.1, 0.1),
        #     pr.WHITE
        # )

    def unload(self) -> None:
        pr.unload_model(self.model)
