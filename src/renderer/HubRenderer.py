from pyray import Model, Vector3
from .models import HubModel
from ..utils import Logger, Color
from .RayCast import RayCast
from ..Level import Level
from ..Hub import Hub
import pyray as pr


class HubRenderer:
    level: Level
    logger: Logger
    ray_cast: RayCast

    node_model: Model
    node_es_model: Model
    nodes: list[HubModel]

    def __init__(self, level: Level, ray_cast: RayCast) -> None:
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='HubRenderer',
            color=Color.GREEN
        )
        self.logger.log('Initializing hub renderer...')
        self.ray_cast = ray_cast

        # Create hub
        self.node_model = pr.load_model('src/assets/models/node.glb')
        # self.node_es_model = pr.load_model('src/assets/models/platform.glb')
        self.nodes = []
        for hub in self.level.hubs.values():
            model = HubModel(hub, self.node_model)
            self.nodes.append(model)
            # self.ray_cast.register_static(
            #     self.hub_model,
            #     self._calculate_position(hub),
            #     hub
            # )
            pass

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
                self.node_model,
                self._calculate_position(hub),
                1,
                pr.WHITE
            )
            pass

    def _calculate_position(self, hub: Hub) -> Vector3:
        return Vector3(hub.x * 3, 0.8, hub.y * 3)

    def unload(self) -> None:
        self.logger.log('Unloading hub renderer...')
        pr.unload_model(self.node_model)
