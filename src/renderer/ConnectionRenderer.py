from .models import ConnectionModel
from ..utils import Logger, Color
from ..network import Network


class ConnectionRenderer:
    """Renderer for connection visualization in the 3D environment.

    Manages rendering of all connections between nodes using connection models.

    Attributes:
        level: The level containing connection data.
        logger: Logger instance for debug output.
        connections_models: List of connection models to render.
    """
    network: Network
    logger: Logger

    connections_models: list[ConnectionModel]

    def __init__(self, network: Network) -> None:
        """Initialize the connection renderer.

        Args:
            level: The level instance containing connection data.
        """
        self.network = network
        self.logger = Logger(
            print_log=network.logger.print_log,
            name='ConnectionRenderer',
            color=Color.BLUE
        )
        self.logger.log('Initializing connections renderer...')
        self.connections_models = []
        self._generate_models()

    def _generate_models(self) -> None:
        """Generate visual models for all connections in the level."""
        for connection in self.network.connections:
            model = ConnectionModel(connection)
            self.connections_models.append(model)

    def update(self) -> None:
        """Update connection models (placeholder for future logic)."""
        pass

    def draw(self) -> None:
        """Draw all connection models to the screen."""
        for model in self.connections_models:
            model.draw()

    def unload(self) -> None:
        """Unload and clean up connection models."""
        self.logger.log('Unloading connection renderer...')
        for model in self.connections_models:
            model.unload()
        self.connections_models.clear()
