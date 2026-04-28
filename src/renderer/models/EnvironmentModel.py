from ..Environment import Environment, EEnvironmentObject
from pyray import Model, Vector3
import pyray as pr


class EnvironmentModel:
    """Manager for environment object models (obstacles, blocked nodes, etc.).

    Attributes:
        environment: The Environment instance.
        models: Loaded PyRay models mapped by object type.
        models_path: Paths and scales for environment object models.
    """
    environment: Environment

    models: dict[EEnvironmentObject, tuple[Model, Vector3]]
    models_path: dict[EEnvironmentObject, tuple[str, Vector3]] = {
        EEnvironmentObject.BLOCKED_NODE: (
            'src/assets/models/environment/blocked_node.glb',
            Vector3(1.2, 1, 1.2)
        )
    }

    def __init__(self, environment: Environment) -> None:
        """Initialize the environment model manager.

        Args:
            environment: The Environment instance.
        """
        self.environment = environment

        self.load()

    def load(self) -> None:
        """Load all environment object models from file paths."""
        self.models = {}
        for key, (obj_path, obj_scale) in self.models_path.items():
            self.models[key] = (pr.load_model(obj_path), obj_scale)

    def draw(self) -> None:
        """Draw all environment objects in their grid positions."""
        """Draw all environment objects in their grid positions."""
        for y, row in self.environment.environment_map.items():
            for x, obj in row.items():
                if obj in self.models:
                    model, scale = self.models[obj]
                    pr.draw_model_ex(
                        model,
                        Vector3(
                            x + self.environment.offset_x,
                            1,
                            y + self.environment.offset_y
                        ),
                        Vector3(0, 1, 0),
                        0,
                        scale,
                        pr.WHITE
                    )

    def unload(self) -> None:
        """Unload all environment models."""
        for model, _ in self.models.values():
            pr.unload_model(model)
