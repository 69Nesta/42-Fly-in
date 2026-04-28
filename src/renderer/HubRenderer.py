from .models import HubModel
from ..utils import Logger, Color
from .RayCast import RayCast
from ..Level import Level
from pyray import Model
import pyray as pr


class HubRenderer:
    """Renderer for hub visualization in the 3D environment.

    Manages rendering of all hub nodes and their color indicators,
    with support for selection via raycasting.

    Attributes:
        level: The level containing hub data.
        logger: Logger instance for debug output.
        ray_cast: Ray casting system for intersection detection.
        node_model: 3D model for hub geometry.
        node_color_model: 3D model for hub color indicator.
        nodes: List of hub models to render.
    """
    level: Level
    logger: Logger
    ray_cast: RayCast

    node_model: Model
    node_es_model: Model
    nodes: list[HubModel]

    def __init__(self, level: Level, ray_cast: RayCast) -> None:
        """Initialize the hub renderer.

        Args:
            level: The level instance containing hub data.
            ray_cast: The ray casting system for intersection detection.
        """
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='HubRenderer',
            color=Color.GREEN
        )
        self.logger.log('Initializing hub renderer...')
        self.ray_cast = ray_cast

        self.node_model = pr.load_model('src/assets/models/node.glb')
        self.node_color_model = pr.load_model_from_mesh(
            pr.gen_mesh_cylinder(0.15, 0.2, 16)
        )

        self.nodes = []
        for hub in self.level.hubs.values():
            model = HubModel(hub, self.node_model, self.node_color_model)
            self.nodes.append(model)
            self.ray_cast.register(model)
            pass

    def update(self) -> None:
        """Update hub models (placeholder for future logic)."""
        pass

    def draw(self) -> None:
        """Draw all hub models to the screen."""
        for node in self.nodes:
            node.draw()

    def unload(self) -> None:
        """Unload and clean up hub models."""
        self.logger.log('Unloading hub renderer...')
        pr.unload_model(self.node_model)
        pr.unload_model(self.node_color_model)
