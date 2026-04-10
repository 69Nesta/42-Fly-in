from pyray import Mesh, Model, Vector3
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
            Vector3(x, 0.0, y),
            0.4,
            pr.YELLOW
        )

    def unload(self) -> None:
        pr.unload_model(self.model)
