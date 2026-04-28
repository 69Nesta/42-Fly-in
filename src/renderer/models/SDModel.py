from ..Environment import Environment
from pyray import Model, Vector3
from ...Level import Level
import pyray as pr


class SDModel:
    """Renders visual indicators for start and end hubs.

    Attributes:
        environment: The Environment instance.
        model: PyRay model for start/end hub indicators.
        level: The Level instance.
        scale: Scaling factor for positioning.
        offset_x: Horizontal offset for start hub.
        offset_y: Vertical offset for start hub.
    """
    environment: Environment
    model: Model
    level: Level

    scale: float
    offset_x: float
    offset_y: float

    def __init__(self, environment: Environment) -> None:
        """Initialize the start/end hub indicator model.

        Args:
            environment: The Environment instance.
        """
        self.environment = environment
        self.level = environment.level
        self.model = pr.load_model('src/assets/models/node_start_end.glb')

        self.scale = environment.SCALE
        self.offset_x = environment.SCALE
        self.offset_y = 0

    def draw(self) -> None:
        """Draw indicators for start and end hubs."""
        """Draw indicators for start and end hubs."""
        pr.draw_model_ex(
            self.model,
            Vector3(
                self.level.start_hub.x * self.scale - self.offset_x,
                1,
                self.level.start_hub.y * self.scale - self.offset_y
            ),
            Vector3(0, 1, 0),
            0,
            Vector3(1, 1, 1),
            pr.WHITE
        )

        pr.draw_model_ex(
            self.model,
            Vector3(
                (self.level.end_hub.x) * self.scale + self.offset_x,
                1,
                self.level.end_hub.y * self.scale - self.offset_y
            ),
            Vector3(0, 1, 0),
            180,
            Vector3(1, 1, 1),
            pr.WHITE
        )

    def unload(self) -> None:
        """Unload the start/end hub indicator model."""
        pr.unload_model(self.model)
