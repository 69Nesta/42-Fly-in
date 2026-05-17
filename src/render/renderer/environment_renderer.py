from ..models import PlatformModel, SDModel, EnvironmentModel
from ..environment import Environment
from ...utils import Logger, Color
from ...network import Network
from ..models import SkyModel


class EnvironmentRenderer:
    """Coordinates rendering of all environment elements.

    Manages skybox, platform, environment objects, and start/end node
    indicators.

    Attributes:
        level: The Level instance.
        logger: Logger for debug output.
        sky_model: The SkyBox renderer.
        environment: The Environment grid.
        platform: The PlatformModel.
        sd_model: Start/end hub indicator model.
        environment_model: Environment object models.
    """
    network: Network
    logger: Logger

    environment: Environment

    sky_model: SkyModel
    platform: PlatformModel
    sd_model: SDModel
    environment_model: EnvironmentModel

    def __init__(self, network: Network) -> None:
        """Initialize the environment renderer.

        Args:
            level: The Level instance.
        """
        self.network = network
        self.logger = Logger(
            print_log=network.logger.print_log,
            name='EnvironmentRenderer',
            color=Color.BRIGHT_YELLOW
        )
        self.logger.log('Initializing environment renderer...')

        self.sky_model = SkyModel()
        self.environment = Environment(self.network)
        self.environment_model = EnvironmentModel(self.environment)
        self.platform = PlatformModel(self.environment)
        self.sd_model = SDModel(self.environment)

    def update(self, _: float) -> None:
        """Update environment (placeholder for future logic).

        Args:
            _: Unused parameter for timing information.
        """
        pass

    def draw(self) -> None:
        """Draw all environment elements in proper order."""
        self.sky_model.draw_3d()
        self.sd_model.draw()
        self.platform.draw()
        self.environment_model.draw()

    def unload(self) -> None:
        """Unload and clean up all environment resources."""
        self.logger.log('Unloading environment renderer...')
        self.sky_model.unload()
        self.platform.unload()
        self.sd_model.unload()
        self.environment_model.unload()
