from pyray import Model, Vector3
from ...Hub import Hub
import pyray as pr


class HubModel:
    model: Model
    colliton_model: Model
    hub: Hub
    is_selected: bool

    def __init__(self, hub: Hub, model: Model) -> None:
        self.hub = hub
        self.model = model
        self.colliton_model = pr.load_model_from_mesh(
            pr.gen_mesh_cube(1, 0.1, 1)
        )
        self.is_selected = False

    def set_selected(self, selected: bool) -> None:
        self.is_selected = selected

    def get_position(self) -> Vector3:
        return Vector3(self.hub.x * 3, 1, self.hub.y * 3)

    def get_coll_position(self) -> Vector3:
        return Vector3(self.hub.x * 3, 1.05, self.hub.y * 3)

    def draw(self) -> None:
        pr.draw_model_ex(
            self.model,
            self.get_position(),
            Vector3(0, 1, 0),
            0,
            Vector3(0.5, 0.5, 0.5),
            pr.WHITE
        )
        if self.is_selected:
            self.is_selected = False
            pr.draw_model_wires_ex(
                self.colliton_model,
                self.get_coll_position(),
                Vector3(0, 1, 0),
                0,
                Vector3(1, 1, 1),
                pr.WHITE
            )
        pass

    def unload(self) -> None:
        pr.unload_model(self.colliton_model)
        pass
