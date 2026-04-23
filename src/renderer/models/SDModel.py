from ..Environment import Environment
from pyray import Model, Vector3
from ...Level import Level
import pyray as pr


class SDModel:
    environment: Environment
    model: Model
    level: Level

    scale: float
    offset_x: float
    offset_y: float

    def __init__(self, environment: Environment) -> None:
        self.environment = environment
        self.level = environment.level
        self.model = pr.load_model('src/assets/models/node_start_end.glb')

        self.scale = environment.SCALE
        self.offset_x = environment.SCALE
        self.offset_y = 0

    def draw(self) -> None:
        pr.draw_model_ex(
            self.model,
            Vector3(
                self.level.start_hub.x * self.scale - self.offset_x,
                1,
                self.level.start_hub.y * self.scale - self.offset_y
            ),
            Vector3(0, 1, 0),
            0,
            Vector3(1, 1, 1),
            pr.WHITE
        )

        pr.draw_model_ex(
            self.model,
            Vector3(
                (self.level.end_hub.x) * self.scale + self.offset_x,
                1,
                self.level.end_hub.y * self.scale - self.offset_y
            ),
            Vector3(0, 1, 0),
            180,
            Vector3(1, 1, 1),
            pr.WHITE
        )

    def unload(self) -> None:
        pr.unload_model(self.model)
