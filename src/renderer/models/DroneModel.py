from pyray import Mesh, Model, Vector3, Vector2
import pyray as pr


class DroneModel:
    mesh: Mesh
    model: Model

    def __init__(self) -> None:
        self.mesh = pr.gen_mesh_cube(0.5, 0.5, 0.5)
        self.model = pr.load_model_from_mesh(self.mesh)

    def draw(self, x: int, y: int) -> None:
        pr.draw_model(
            self.model,
            Vector3(x, 1.0, y),
            0.4,
            pr.YELLOW
        )

    def draw_from_vector(self, position: Vector2) -> None:
        pr.draw_model(
            self.model,
            Vector3(position.x, 1.0, position.y),
            0.4,
            pr.YELLOW
        )

    def unload(self) -> None:
        pr.unload_model(self.model)
