from ..utils import Logger, Color
from ..Level import Level
import pyray as pr


class UIRenderer:
    level: Level
    logger: Logger
    width: int
    height: int

    def __init__(self, level: Level, width: int, height: int) -> None:
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='UIRenderer',
            color=Color.GREEN
        )
        self.logger.log('Initializing UI renderer...')
        self.width = width
        self.height = height

    def update(self) -> None:
        pass

    def _draw_crosshair(self) -> None:
        pr.draw_rectangle(
            int(self.width / 2) - 1,
            int(self.height / 2) - 10,
            2, 20,
            pr.fade(pr.GRAY, 0.8)
        )
        pr.draw_rectangle(
            int(self.width / 2) - 10,
            int(self.height / 2) - 1,
            20, 2,
            pr.fade(pr.GRAY, 0.8)
        )

    def _draw_step(self) -> None:
        pr.draw_text(
            f'STEP: {self.level.current_step} / {self.level.number_of_steps}',
            10,
            30,
            20,
            pr.GRAY
        )

    def draw(self) -> None:
        pr.draw_fps(10, 10)

        self._draw_step()
        self._draw_crosshair()

    def unload(self) -> None:
        self.logger.log('Unloading UI renderer...')
