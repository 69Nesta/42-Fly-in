from .CollisionModel import CollisionModel
from pyray import Model, Vector3
from ...Hub import Hub
import pyray as pr


class HubModel(CollisionModel):
    model: Model
    collision_model: Model
    hub: Hub

    def __init__(self, hub: Hub, model: Model) -> None:
        super().__init__()
        self.hub = hub
        self.model = model
        self.collision_model = pr.load_model_from_mesh(
            pr.gen_mesh_cube(1, 0.1, 1)
        )

    def get_collision_model(self) -> Model:
        return self.collision_model

    def get_position(self) -> Vector3:
        return Vector3(self.hub.x * 3, 1, self.hub.y * 3)

    def get_collision_position(self) -> Vector3:
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
                self.collision_model,
                self.get_collision_position(),
                self.get_collision_rotation_axis(),
                self.get_collision_rotation(),
                Vector3(1, 1, 1),
                pr.WHITE
            )
        pass

    def unload(self) -> None:
        pr.unload_model(self.collision_model)
        pass
