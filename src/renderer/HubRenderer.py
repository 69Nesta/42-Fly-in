from .models import HubModel
from ..utils import Logger, Color
from .RayCast import RayCast
from ..Level import Level
from pyray import Model
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

        self.nodes = []
        for hub in self.level.hubs.values():
            model = HubModel(hub, self.node_model)
            self.nodes.append(model)
            self.ray_cast.register(model)
            pass

    def update(self) -> None:
        pass

    def draw(self) -> None:
        for node in self.nodes:
            node.draw()

    def unload(self) -> None:
        self.logger.log('Unloading hub renderer...')
        pr.unload_model(self.node_model)
