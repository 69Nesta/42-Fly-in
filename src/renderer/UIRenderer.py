from ..utils import Logger, Color
from .RayCast import RayCast, t_RayCastValues
from ..Level import Level
from ..Hub import Hub
from pyray import Ray
import pyray as pr


class UIRenderer:
    level: Level
    logger: Logger
    width: int
    height: int
    ray_cast: RayCast

    _current_hub: Hub | None

    def __init__(
                self,
                level: Level,
                width: int, height: int,
                ray_cast: RayCast
            ) -> None:
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='UIRenderer',
            color=Color.GREEN
        )

        self.logger.log('Initializing UI renderer...')
        self.width = width
        self.height = height
        self.ray_cast = ray_cast

        self._current_hub = None

    def update(self, ray: Ray) -> None:
        object: t_RayCastValues | None = self.ray_cast.cast(ray)
        self._current_hub = None

        if object is None:
            return

        if isinstance(object, Hub):
            self._current_hub = object

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

    def _draw_current_hub(self) -> None:
        if self._current_hub is not None:
            pr.draw_text(
                f'Current hub: {self._current_hub.name!r}',
                10,
                50,
                20,
                pr.RED
            )
        pass

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
        self._draw_current_hub()

    def unload(self) -> None:
        self.logger.log('Unloading UI renderer...')
