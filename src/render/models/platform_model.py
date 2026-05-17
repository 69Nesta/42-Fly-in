from ..environment import Environment
from pyray import Model, Vector3
import pyray as pr


class PlatformModel:
    """Renders the ground platform for the environment grid.

    Attributes:
        model: PyRay model for the platform tile.
        environment: The Environment instance.
    """
    model: Model
    environment: Environment

    def __init__(self, environment: Environment) -> None:
        """Initialize the platform model.

        Args:
            environment: The Environment instance.
        """
        self.environment = environment
        self.model = pr.load_model('src/assets/models/platform.glb')

    def draw(self) -> None:
        """Draw platform tiles for the entire environment grid."""
        for x in range(self.environment.environment_width):
            for y in range(self.environment.environment_height):
                pr.draw_model_ex(
                    self.model,
                    Vector3(
                        (x + self.environment.offset_x),
                        0.82,
                        (y + self.environment.offset_y)
                    ),
                    Vector3(0, 1, 0),
                    0,
                    Vector3(1.3, 1.5, 1.3),
                    pr.WHITE
                )

    def unload(self) -> None:
        """Unload the platform model."""
        pr.unload_model(self.model)
