from .models import DroneModel
from ..utils import Logger, Color
from .RayCast import RayCast, t_RayCastValues
from ..Level import Level
from ..Hub import Hub
from pyray import Ray
import pyray as pr


def truncate(text, max_length):
    if len(text) > max_length:
        return text[:max_length - 1] + "..."
    return text


class UIRenderer:
    level: Level
    logger: Logger
    width: int
    height: int
    ray_cast: RayCast

    _current_targeting: Hub | DroneModel | None

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

        self._current_targeting = None

    def update(self, ray: Ray) -> None:
        object: t_RayCastValues | None = self.ray_cast.cast(ray)
        self._current_targeting = None

        if object is None:
            return

        if isinstance(object, Hub):
            self._current_targeting = object
        elif isinstance(object, DroneModel):
            self._current_targeting = object

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
        text_space: int
        width: int
        height: int
        left_align: int
        top_align: int

        if self._current_targeting is None:
            return

        if isinstance(self._current_targeting, Hub):
            text_space = 25
            width = 300
            height = text_space * 6 + 15
            left_align = self.width - width - 20
            top_align = 20

            pr.draw_rectangle(
                left_align - 10, top_align - 10,
                width, height,
                pr.fade(pr.SKYBLUE, 0.5)
            )
            pr.draw_rectangle_lines(
                left_align - 10, top_align - 10,
                width, height,
                pr.BLUE
            )

            pr.draw_text(
                'Type: Hub',
                left_align,
                top_align + text_space * 0,
                20,
                pr.BLUE
            )
            pos = self._current_targeting.get_position()
            pr.draw_text(
                f'node: {truncate(self._current_targeting.name, 15)} '
                f'({pos.x:.0f}, {pos.y:.0f})',
                left_align,
                top_align + text_space * 1,
                20,
                pr.BLUE
            )
            pr.draw_text(
                'zone: '
                f'{self._current_targeting.metadata.zone.name.capitalize()}',
                left_align,
                top_align + text_space * 2,
                20,
                pr.BLUE
            )
            pr.draw_text(
                f'color: {self._current_targeting.metadata.color}',
                left_align,
                top_align + text_space * 3,
                20,
                pr.BLUE
            )
            pr.draw_text(
                f'cost: {self._current_targeting.metadata.get_travel_time()} '
                'turn',
                left_align,
                top_align + text_space * 4,
                20,
                pr.BLUE
            )
            reservation = self.level.reservations.get(
                self._current_targeting, {}
            )
            pr.draw_text(
                f'load: {reservation.get(self.level.current_step, 0)} /'
                f' {self._current_targeting.metadata.max_drones}',
                left_align,
                top_align + text_space * 5,
                20,
                pr.BLUE
            )
        elif isinstance(self._current_targeting, DroneModel):
            text_space = 25
            width = 300
            height = text_space * 2 + 15
            left_align = self.width - width - 20
            top_align = 20

            pr.draw_rectangle(
                left_align - 10, top_align - 10,
                width, height,
                pr.fade(pr.LIME, 0.5)
            )
            pr.draw_rectangle_lines(
                left_align - 10, top_align - 10,
                width, height,
                pr.GREEN
            )

            pr.draw_text(
                'Type: Drone',
                left_align,
                top_align + text_space * 0,
                20,
                pr.GREEN
            )
            position = self._current_targeting.get_position()
            pr.draw_text(
                f'position: ({position.x:.0f}, {position.z:.0f})',
                left_align,
                top_align + text_space * 1,
                20,
                pr.GREEN
            )
        pass

    def _draw_state(self) -> None:
        left_align: int = 20
        top_align: int = 20
        pr.draw_rectangle(
            left_align - 10, top_align - 10,
            200, 70,
            pr.fade(pr.BLACK, 0.5)
        )
        pr.draw_rectangle_lines(
            left_align - 10, top_align - 10,
            200, 70,
            pr.WHITE
        )

        pr.draw_fps(left_align, top_align)
        pr.draw_text(
            f'STEP: {self.level.current_step} / {self.level.number_of_steps}',
            left_align,
            top_align + 30,
            20,
            pr.WHITE
        )

    def draw(self) -> None:
        self._draw_state()
        self._draw_crosshair()
        self._draw_current_hub()

    def unload(self) -> None:
        self.logger.log('Unloading UI renderer...')
