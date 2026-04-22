from ..Environment import Environment
from pyray import Model, Vector3
import pyray as pr


class PlatformModel:
    model: Model
    environment: Environment

    offset_x: float = 0
    offset_y: float = 0

    def __init__(self, environment: Environment) -> None:
        self.environment = environment
        self.model = pr.load_model('src/assets/models/platform.glb')

        self.offset_x = -(3 * 2 / 2) + (environment.level.min_pos.x * 3)
        self.offset_y = -(3 * 2 / 2) + (environment.level.min_pos.y * 3)

    def draw(self) -> None:
        for x in range(self.environment.environment_width):
            for y in range(self.environment.environment_height):
                pr.draw_model_ex(
                    self.model,
                    Vector3(x + self.offset_x, 0.82, y + self.offset_y),
                    Vector3(0, 1, 0),
                    0,
                    Vector3(1.5, 1.5, 1.5),
                    pr.WHITE
                )
        pass

    def unload(self) -> None:
        pr.unload_model(self.model)
