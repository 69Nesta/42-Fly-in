from ..Environment import Environment, EEnvironmentObject
from pyray import Model, Vector3
import pyray as pr


class EnvironmentModel:
    environment: Environment

    models: dict[EEnvironmentObject, tuple[Model, Vector3]]
    models_path: dict[EEnvironmentObject, tuple[str, Vector3]] = {
        EEnvironmentObject.BLOCKED_NODE: (
            'src/assets/models/environment/blocked_node.glb',
            Vector3(1.2, 1, 1.2)
        )
    }

    def __init__(self, environment: Environment) -> None:
        self.environment = environment

        self.load()

    def load(self) -> None:
        self.models = {}
        for key, (obj_path, obj_scale) in self.models_path.items():
            self.models[key] = (pr.load_model(obj_path), obj_scale)

    def draw(self) -> None:
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
        pass

    def unload(self) -> None:
        for model, _ in self.models.values():
            pr.unload_model(model)
        pass
