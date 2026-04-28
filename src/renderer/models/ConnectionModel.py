from pyray import Mesh, Model, Vector2, Vector3, Color
from ...Connections import Connection
from ...utils import MathUtils
import pyray as pr
import math


class ConnectionModel:
    WORLD_SCALE: float = 3.0
    CONNECTION_Y: float = 0.96

    connection: Connection

    model: Model
    position: Vector3
    angle: float
    color: Color

    def __init__(self, connection: Connection) -> None:
        super().__init__()
        self.connection = connection
        self._generate_models()

        self.color = Color(156, 175, 183, 255)

    def _generate_models(self) -> None:
        p1 = Vector2(self.connection.hubs[0].x, self.connection.hubs[0].y)
        p2 = Vector2(self.connection.hubs[1].x, self.connection.hubs[1].y)
        length = (
            MathUtils.get_distance_between_points(p1, p2) * self.WORLD_SCALE
        )
        angle_rad = math.atan2(p2.y - p1.y, p1.x - p2.x)

        mesh: Mesh = pr.gen_mesh_cylinder(0.05, length, 8)
        self.model = pr.load_model_from_mesh(mesh)

        transform = pr.matrix_multiply(
            pr.matrix_rotate_z(math.pi / 2),
            pr.matrix_rotate_y(angle_rad)
        )
        self.model.transform = transform

        position = Vector3(
            self.connection.hubs[0].x * self.WORLD_SCALE,
            self.CONNECTION_Y,
            self.connection.hubs[0].y * self.WORLD_SCALE
        )
        self.position = position

    def update(self) -> None:
        pass

    def draw(self) -> None:
        pr.draw_model(
            self.model,
            self.position,
            1,
            self.color
        )

    def unload(self) -> None:
        pr.unload_model(self.model)
