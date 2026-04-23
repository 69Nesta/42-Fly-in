from .models import DroneModel, HubModel, CollisionModel
from .InputController import InputController, ESettings
from ..utils import Logger, Color
from .RayCast import RayCast
from .components import TextBox
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
    input_controller: InputController

    _current_targeting: Hub | DroneModel | None
    text_box_drone: TextBox
    text_box_hub: TextBox
    text_box_state: TextBox

    def __init__(
                self,
                level: Level,
                width: int, height: int,
                ray_cast: RayCast,
                input_controller: InputController
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
        self.input_controller = input_controller
        self._current_targeting = None

        self.init_text_boxes()

    def init_text_boxes(self) -> None:
        self.text_box_state = TextBox(
            font_size=20,
            text_color=pr.WHITE,
            background_color=pr.fade(pr.GRAY, 0.2),
            screen_width=self.width,
            screen_height=self.height,
            top_align=True,
            left_align=True,
        )
        self.text_box_drone = TextBox(
            font_size=20,
            text_color=pr.ORANGE,
            background_color=pr.fade(pr.ORANGE, 0.2),
            screen_width=self.width,
            screen_height=self.height,
            top_align=True,
            left_align=False,
        )
        self.text_box_hub = TextBox(
            font_size=20,
            text_color=pr.BLUE,
            background_color=pr.fade(pr.SKYBLUE, 0.2),
            screen_width=self.width,
            screen_height=self.height,
            top_align=True,
            left_align=False,
        )
        self.text_box_help = TextBox(
            font_size=20,
            text_color=pr.PURPLE,
            background_color=pr.fade(pr.PURPLE, 0.2),
            screen_width=self.width,
            screen_height=self.height,
            top_align=False,
            left_align=True,
        )
        self._init_help()

    def update(self, ray: Ray) -> None:
        object: CollisionModel | None = self.ray_cast.cast(ray)
        self._current_targeting = None

        if object is None:
            return

        if isinstance(object, HubModel):
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

    def _draw_current_target(self) -> None:
        if self._current_targeting is None:
            return

        if isinstance(self._current_targeting, HubModel):
            self._current_targeting = self._current_targeting.hub
            reservation: dict[int, int] = self.level.reservations.get(
                self._current_targeting, {}
            )
            cost: int = self._current_targeting.metadata.get_travel_time()
            self.text_box_hub.set_lines([
                'Type: Hub',
                (
                    f'Node: {truncate(self._current_targeting.name, 15)} '
                    f'({self._current_targeting.get_position().x:.0f}, '
                    f'{self._current_targeting.get_position().y:.0f})'
                ),
                (
                    'Zone: ' +
                    self._current_targeting.metadata.zone.name.capitalize()
                ),
                f'Color: {self._current_targeting.metadata.color}',
                f'Cost: {cost} turn',
                (
                    f'Load: {reservation.get(self.level.current_step, 0)} /'
                    f' {self._current_targeting.metadata.max_drones}'
                )
            ])
            self.text_box_hub.draw()
        elif isinstance(self._current_targeting, DroneModel):
            self.text_box_drone.set_lines([
                'Type: Drone',
                f'ID: D{self._current_targeting.get_id() + 1}',
                f'Position: ({self._current_targeting.get_position().x:.0f}, '
                f'{self._current_targeting.get_position().z:.0f})',
            ])
            self.text_box_drone.draw()

    def _draw_state(self) -> None:
        self.text_box_state.set_lines(
            [
                f'FPS: {pr.get_fps()}',
                (
                    f'STEP: {self.level.current_step} / '
                    f'{self.level.number_of_steps}'
                )
            ],
            {
                0: pr.GREEN
            }
        )
        self.text_box_state.draw()

    def _init_help(self) -> None:
        help_text: list[str] = [
            'Controls:',
            '- Left / Right arrow to change simulation step',
            '- Right click to toggle mouse focus',
            '- WASD to move the camera',
            '- H to toggle this help',
            '- Mouse to look around',
        ]
        self.text_box_help.set_lines(help_text)

    def _draw_help(self) -> None:
        if not self.input_controller.get_setting(ESettings.SHOW_UI_HELP):
            return

        self.text_box_help.draw()

    def draw(self) -> None:
        self._draw_help()
        self._draw_state()
        self._draw_crosshair()
        self._draw_current_target()

    def unload(self) -> None:
        self.logger.log('Unloading UI renderer...')
