from .models import PlatformModel, SDModel, EnvironmentModel
from .Environment import Environment
from ..utils import Logger, Color
from ..Level import Level
from .SkyBox import SkyBox


class EnvironmentRenderer:
    level: Level
    logger: Logger

    skybox: SkyBox
    environment: Environment

    platform: PlatformModel
    sd_model: SDModel
    environment_model: EnvironmentModel

    def __init__(self, level: Level) -> None:
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='EnvironmentRenderer',
            color=Color.BRIGHT_YELLOW
        )
        self.logger.log('Initializing environment renderer...')

        self.skybox = SkyBox()
        self.environment = Environment(self.level)
        self.environment_model = EnvironmentModel(self.environment)
        self.platform = PlatformModel(self.environment)
        self.sd_model = SDModel(self.environment)

    def update(self, _: float) -> None:
        pass

    def draw(self) -> None:
        self.skybox.draw_3d()
        self.sd_model.draw()
        self.platform.draw()
        self.environment_model.draw()

    def unload(self) -> None:
        self.logger.log('Unloading environment renderer...')
        self.skybox.unload()
        self.platform.unload()
        self.sd_model.unload()
        self.environment_model.unload()
