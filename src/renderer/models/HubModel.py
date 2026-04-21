from pyray import Model, Vector3, Vector2
import pyray as pr

class HubModel:
    model: Model

    def __init__(self, x: float, y: float) -> None:
        self.model = pr.load_model('src/assets/models/boat.glb')


    def get_position(self) -> Vector3:
        return Vector3(self.last_postion[0].x, 1.0, self.last_postion[0].y)

    def draw(self) -> None:

        pr.draw_model_ex(
            self.model,
            self.get_position(),
            Vector3(0, 1, 0),
            rotation + 90,
            Vector3(0.1, 0.1, 0.1),
            pr.WHITE
        )

    def unload(self) -> None:
        pr.unload_model(self.model)
