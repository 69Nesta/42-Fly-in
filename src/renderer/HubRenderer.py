from pyray import Mesh, Model, Vector3
from ..utils import Logger, Color
from .RayCast import RayCast
from ..Level import Level
from ..Hub import Hub
import pyray as pr


class HubRenderer:
    level: Level
    logger: Logger
    ray_cast: RayCast

    # hub_mesh: Mesh
    hub_model: Model

    def __init__(self, level: Level, ray_cast: RayCast) -> None:
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='HubRenderer',
            color=Color.GREEN
        )
        self.logger.log('Initializing hub renderer...')
        self.ray_cast = ray_cast

        # Create hub mesh
        # self.hub_mesh = pr.gen_mesh_sphere(0.2, 16, 16)
        self.hub_model = pr.load_model('src/assets/models/island.glb')

        for hub in self.level.hubs.values():
            self.ray_cast.register_static(
                self.hub_model,
                self._calculate_position(hub),
                hub
            )

    def update(self) -> None:
        pass

    def draw(self) -> None:
        for hub in self.level.hubs.values():
            # color: pr.Color
            # if hub.is_start():
            #     color = pr.BLUE
            # elif hub.is_end():
            #     color = pr.GREEN
            # elif hub.is_restricted():
            #     color = pr.RED
            # elif hub.is_priority():
            #     color = pr.YELLOW
            # else:
            #     color = pr.GRAY
            pr.draw_model(
                self.hub_model,
                self._calculate_position(hub),
                0.01,
                pr.WHITE
            )

    def _calculate_position(self, hub: Hub) -> Vector3:
        return Vector3(hub.x * 3, 0.82, hub.y * 3)

    def unload(self) -> None:
        self.logger.log('Unloading hub renderer...')
        pr.unload_model(self.hub_model)
