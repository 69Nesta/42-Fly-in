from pyray import Mesh, Model, Vector2, Vector3, Color
from ...Connections import Connection
from ...utils import MathUtils
import pyray as pr
import math


class ConnectionModel:
    """Visual 3D model for a connection between two hubs.

    Renders connections as cylinders with proper positioning and rotation
    based on the connected hubs' positions.

    Attributes:
        WORLD_SCALE: Scale factor for converting map coordinates to world space
        CONNECTION_Y: Y-axis height for connections.
        connection: The Connection object this model represents.
        model: The PyRay Model for the connection geometry.
        position: World position of the connection.
        angle: Rotation angle of the connection.
        color: Color of the connection.
    """
    WORLD_SCALE: float = 3.0
    CONNECTION_Y: float = 0.96

    connection: Connection

    model: Model
    position: Vector3
    angle: float
    color: Color

    def __init__(self, connection: Connection) -> None:
        """Initialize a connection model.

        Args:
            connection: The Connection object to visualize.
        """
        super().__init__()
        self.connection = connection
        self._generate_models()

        self.color = Color(156, 175, 183, 255)

    def _generate_models(self) -> None:
        """Generate the 3D cylinder model for the connection.

        Calculates distance and angle between hubs and creates a cylinder
        mesh rotated to connect them.
        """
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
        """Update the connection model (placeholder for future logic)."""
        pass

    def draw(self) -> None:
        """Draw the connection model to the screen."""
        pr.draw_model(
            self.model,
            self.position,
            1,
            self.color
        )

    def unload(self) -> None:
        """Unload and clean up the connection model."""
        pr.unload_model(self.model)
