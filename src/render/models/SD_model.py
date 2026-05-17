from ..environment import Environment
from pyray import Model, Vector3
from ...network import Network
import pyray as pr


class SDModel:
    """Renders visual indicators for start and end nodes.

    Attributes:
        environment: The Environment instance.
        model: PyRay model for start/end node indicators.
        network: The Network instance.
        scale: Scaling factor for positioning.
        offset_x: Horizontal offset for start node.
        offset_y: Vertical offset for start node.
    """
    environment: Environment
    model: Model
    network: Network

    scale: float
    offset_x: float
    offset_y: float

    def __init__(self, environment: Environment) -> None:
        """Initialize the start/end node indicator model.

        Args:
            environment: The Environment instance.
        """
        self.environment = environment
        self.network = environment.network
        self.model = pr.load_model('src/assets/models/node_start_end.glb')

        self.scale = environment.SCALE
        self.offset_x = environment.SCALE
        self.offset_y = 0

    def draw(self) -> None:
        """Draw indicators for start and end nodes."""
        """Draw indicators for start and end nodes."""
        pr.draw_model_ex(
            self.model,
            Vector3(
                self.network.start_node.x * self.scale - self.offset_x,
                1,
                self.network.start_node.y * self.scale - self.offset_y
            ),
            Vector3(0, 1, 0),
            0,
            Vector3(1, 1, 1),
            pr.WHITE
        )

        pr.draw_model_ex(
            self.model,
            Vector3(
                (self.network.end_node.x) * self.scale + self.offset_x,
                1,
                self.network.end_node.y * self.scale - self.offset_y
            ),
            Vector3(0, 1, 0),
            180,
            Vector3(1, 1, 1),
            pr.WHITE
        )

    def unload(self) -> None:
        """Unload the start/end node indicator model."""
        pr.unload_model(self.model)
