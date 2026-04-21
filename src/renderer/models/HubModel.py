from pyray import Model, Vector3
from ...Hub import Hub
import pyray as pr


class HubModel:
    model: Model
    hub: Hub

    def __init__(self, hub: Hub) -> None:
        self.model = pr.load_model('src/assets/models/island.glb')

    def get_position(self) -> Vector3:
        return Vector3(self.hub.x, 1, self.hub.y)

    def draw(self) -> None:
        pr.draw_model_ex(
            self.model,
            self.get_position(),
            Vector3(0, 1, 0),
            0,
            Vector3(0.1, 0.1, 0.1),
            pr.WHITE
        )

    def unload(self) -> None:
        pr.unload_model(self.model)
