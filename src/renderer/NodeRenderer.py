from .models import NodeModel
from ..utils import Logger, Color
from .RayCast import RayCast
from ..network import Network
from pyray import Model
import pyray as pr


class NodeRenderer:
    """Renderer for node visualization in the 3D environment.

    Manages rendering of all node nodes and their color indicators,
    with support for selection via raycasting.

    Attributes:
        network: The network containing node data.
        logger: Logger instance for debug output.
        ray_cast: Ray casting system for intersection detection.
        node_model: 3D model for node geometry.
        node_color_model: 3D model for node color indicator.
        nodes: List of node models to render.
    """
    network: Network
    logger: Logger
    ray_cast: RayCast

    node_model: Model
    node_es_model: Model
    nodes: list[NodeModel]

    def __init__(self, network: Network, ray_cast: RayCast) -> None:
        """Initialize the node renderer.

        Args:
            network: The network instance containing node data.
            ray_cast: The ray casting system for intersection detection.
        """
        self.network = network
        self.logger = Logger(
            print_log=network.logger.print_log,
            name='NodeRenderer',
            color=Color.GREEN
        )
        self.logger.log('Initializing node renderer...')
        self.ray_cast = ray_cast

        self.node_model = pr.load_model('src/assets/models/node.glb')
        self.node_color_model = pr.load_model_from_mesh(
            pr.gen_mesh_cylinder(0.15, 0.2, 16)
        )

        self.nodes = []
        for node in self.network.nodes:
            model = NodeModel(node, self.node_model, self.node_color_model)
            self.nodes.append(model)
            self.ray_cast.register(model)
            pass

    def update(self) -> None:
        """Update node models (placeholder for future logic)."""
        pass

    def draw(self) -> None:
        """Draw all node models to the screen."""
        for node in self.nodes:
            node.draw()

    def unload(self) -> None:
        """Unload and clean up node models."""
        self.logger.log('Unloading node renderer...')
        pr.unload_model(self.node_model)
        pr.unload_model(self.node_color_model)
