from ..Environment import Environment
from pyray import Model, Vector3
import pyray as pr


class PlatformModel:
    model: Model
    environment: Environment

    # offset_x: float
    # offset_y: float

    def __init__(self, environment: Environment) -> None:
        self.environment = environment
        self.model = pr.load_model('src/assets/models/platform.glb')

    def draw(self) -> None:
        for x in range(self.environment.environment_width):
            for y in range(self.environment.environment_height):
                pr.draw_model_ex(
                    self.model,
                    Vector3(
                        (x + self.environment.offset_x),
                        0.82,
                        (y + self.environment.offset_y)
                    ),
                    Vector3(0, 1, 0),
                    0,
                    Vector3(1.3, 1.5, 1.3),
                    pr.WHITE
                )
        pass

    def unload(self) -> None:
        pr.unload_model(self.model)
