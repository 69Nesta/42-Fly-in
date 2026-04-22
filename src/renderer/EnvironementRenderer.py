from ..utils import Logger, Color
from ..Level import Level
from .SkyBox import SkyBox

from pyray import Model, Mesh
import pyray as pr


class EnvironementRenderer:
    level: Level
    logger: Logger

    # sea: SeaModel

    mesh: Mesh
    model: Model
    skybox: SkyBox
    # buoys: BuoysModel

    def __init__(self, level: Level) -> None:
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='EnvironementRenderer',
            color=Color.BRIGHT_YELLOW
        )
        self.logger.log('Initializing drones renderer...')

        # self.sea = SeaModel()
        self.mesh = pr.gen_mesh_cube(0.2, 0.2, 0.5)
        self.model = pr.load_model_from_mesh(self.mesh)
        self.skybox = SkyBox()
        # self.buoys = BuoysModel(self.level)

    def update(self, time: float) -> None:
        # self.sea.update(time)
        # self.buoys.update(time)
        pass

    def draw(self) -> None:
        # self.sea.draw()
        # self.buoys.draw()
        self.skybox.draw_3d()

    def unload(self) -> None:
        self.logger.log('Unloading drones renderer...')
        # self.sea.unload()
        self.skybox.unload()
