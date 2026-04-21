from pyray import Mesh, Model, Vector3, Color
import pyray as pr


class SeaModel:
    mesh: Mesh
    model: Model
    color: Color

    def __init__(self) -> None:
        self.mesh = pr.gen_mesh_plane(100, 100, 1, 1)
        self.model = pr.load_model_from_mesh(self.mesh)
        self.color = Color(117, 191, 204, 255)

    def update(self, _: float) -> None:
        pass

    def draw(self) -> None:
        pr.draw_model(
            self.model,
            Vector3(0, -0.5, 0),
            1.0,
            self.color
        )

    def unload(self) -> None:
        pr.unload_model(self.model)
