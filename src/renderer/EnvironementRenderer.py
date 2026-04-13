from ..utils import Logger, Color, Bezier
from .models import SeaModel
from ..Level import Level

from pyray import Model, Mesh, Vector2, Vector3
import pyray as pr
import math


class EnvironementRenderer:
    level: Level
    logger: Logger

    sea: SeaModel

    mesh: Mesh
    model: Model
    bezier: Bezier

    def __init__(self, level: Level) -> None:
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='EnvironementRenderer',
            color=Color.BRIGHT_YELLOW
        )
        self.logger.log('Initializing drones renderer...')

        self.sea = SeaModel()
        self.mesh = pr.gen_mesh_cube(0.2, 0.2, 0.5)
        self.model = pr.load_model_from_mesh(self.mesh)
        self.bezier = Bezier(
            Vector2(-10, 0),
            Vector2(-5, 5),
            math.pi / 4,
            math.pi / 2,
            0.3
        )

    def update(self, time: float) -> None:
        self.sea.update(time)

    def draw(self) -> None:
        self.sea.draw()

        number_of_points = 10
        for i in range(number_of_points):
            t = i / (number_of_points - 1)
            pos = self.bezier.bezier_point(t)
            rot = -self.bezier.bezier_rotation(t) + 90

            pr.draw_model_ex(
                self.model,
                Vector3(pos.x, 2, pos.y),
                Vector3(0, 1, 0),
                rot,
                Vector3(1, 1, 1),
                pr.BLUE
            )

    def unload(self) -> None:
        self.logger.log('Unloading drones renderer...')
        self.sea.unload()
