from pyray import Mesh, Model, Vector3
from ..utils import Logger, Color
from ..Level import Level
import pyray as pr


class HubRenderer:
    level: Level
    logger: Logger

    hub_mesh: Mesh
    hub_model: Model

    def __init__(self, level: Level) -> None:
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='HubRenderer',
            color=Color.GREEN
        )
        self.logger.log('Initializing hub renderer...')

        # Create hub mesh
        self.hub_mesh = pr.gen_mesh_sphere(0.5, 16, 16)
        self.hub_model = pr.load_model_from_mesh(self.hub_mesh)

    def update(self) -> None:
        pass

    def draw(self) -> None:
        for hub in self.level.hubs.values():
            color: pr.Color
            if hub.is_start():
                color = pr.BLUE
            elif hub.is_end():
                color = pr.GREEN
            elif hub.is_restricted():
                color = pr.RED
            elif hub.is_priority():
                color = pr.YELLOW
            else:
                color = pr.GRAY
            pr.draw_model(
                self.hub_model,
                Vector3(hub.x, 3.0, hub.y),
                0.4,
                color
            )

    def unload(self) -> None:
        self.logger.log('Unloading hub renderer...')
        pr.unload_model(self.hub_model)
