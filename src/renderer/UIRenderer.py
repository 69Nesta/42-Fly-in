from .models import DroneModel, HubModel, CollisionModel
from .InputController import InputController, ESettings
from pyray import Ray, RayCollision, Camera3D
from .components import TextBox, NameTag
from ..utils import Logger, Color
from .RayCast import RayCast
from ..Level import Level
from ..Hub import Hub
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
    camera: Camera3D
    input_controller: InputController

    _current_targeting: Hub | list[DroneModel] | None
    text_box_drone: TextBox
    text_box_hub: TextBox
    text_box_state: TextBox
    text_box_debug: TextBox

    stack_count_name_tag: NameTag

    def __init__(
                self,
                level: Level,
                width: int, height: int,
                ray_cast: RayCast,
                camera: Camera3D,
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
        self.camera = camera
        self.input_controller = input_controller
        self._current_targeting = None

        self.init_text_boxes()
        self.stack_count_name_tag = NameTag('', self.camera, font_size=16)

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
        self.text_box_debug = TextBox(
            font_size=20,
            text_color=pr.YELLOW,
            background_color=pr.fade(pr.YELLOW, 0.2),
            screen_width=self.width,
            screen_height=self.height,
            top_align=False,
            left_align=False,
        )
        self._init_help()
        self._init_debug()

    def update(self, ray: Ray) -> None:
        objects: list[tuple[CollisionModel, RayCollision]] = \
            self.ray_cast.cast(ray)
        self._current_targeting = None

        if not objects:
            return

        first_object, _ = objects[0]
        first_object.set_selected(True)
        if isinstance(first_object, HubModel):
            self._current_targeting = first_object.hub
        elif isinstance(first_object, DroneModel):
            self._current_targeting = [first_object]
            for obj, _ in objects[1:]:
                if (isinstance(obj, DroneModel)
                   and obj.get_pos() == first_object.get_pos()):
                    self._current_targeting.append(obj)
                else:
                    break

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

    def _draw_current_target_hub(self) -> None:
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

    def _draw_current_target_drone(self) -> None:
        if len(self._current_targeting) == 1:
            self.text_box_drone.set_lines([
                'Type: Drone',
                f'ID: D{self._current_targeting[0].get_id() + 1}',
                'Position: ('
                f'{self._current_targeting[0].get_position().x:.0f}, '
                f'{self._current_targeting[0].get_position().z:.0f})',
            ])
        else:
            self.text_box_drone.set_lines([
                f'Type: Drone (multiple, {len(self._current_targeting)})',
                'IDs: ' + ', '.join([
                    f'D{drone.get_id() + 1}'
                    for drone in self._current_targeting
                ]),
                'Position: ('
                f'{self._current_targeting[0].get_position().x:.0f}, '
                f'{self._current_targeting[0].get_position().z:.0f})',
            ])
            self.stack_count_name_tag.set_text(
                f'x{len(self._current_targeting)}'
            )
            self.stack_count_name_tag.draw(
                self._current_targeting[0].get_position()
            )
        self.text_box_drone.draw()

    def _draw_current_target(self) -> None:
        if self._current_targeting is None:
            return

        if isinstance(self._current_targeting, Hub):
            self._draw_current_target_hub()
        elif isinstance(self._current_targeting, list):
            self._draw_current_target_drone()

    def _draw_state(self) -> None:
        self.text_box_state.set_lines(
            [
                f'FPS: {pr.get_fps()}',
                (
                    f'STEP: {self.level.current_step} / '
                    f'{self.level.number_of_steps - 1}'
                ),
                f'Number of drones: {len(self.level.drones)}'
            ],
            {
                0: pr.GREEN,
                2: pr.GRAY
            }
        )
        self.text_box_state.draw()

    def _init_help(self) -> None:
        help_text: list[str] = [
            'Controls:',
            '- Left / Right arrow to change simulation step',
            '- Right click to toggle mouse focus',
            '- WASD to move the camera',
            '- \'O\' to toggle debug info',
            '- \'H\' to toggle this help',
            '- Mouse to look around',
        ]
        self.text_box_help.set_lines(help_text)

    def _draw_help(self) -> None:
        if not self.input_controller.get_setting(ESettings.SHOW_UI_HELP):
            return

        self.text_box_help.draw()

    def _init_debug(self) -> None:
        pass

    def _draw_debug(self) -> None:
        if not self.input_controller.get_setting(ESettings.SHOW_UI_DEBUG):
            return

        self.text_box_debug.set_lines([
            'Debug info:',
            'Connections Reservations: ',
            *[
                (
                    f'- {conn.hubs[0].name} <-> {conn.hubs[1].name}: ' +
                    str(self.level.reservations_connection.get(conn, {}).get(
                        self.level.current_step, 0
                    )) + f' / {conn.get_capacity()}'
                )
                for conn in self.level.connections.all
            ],
            'Hubs Reservations: ',
            *[
                (
                    f'- {hub.get_name()}: ' +
                    str(self.level.reservations.get(hub, {}).get(
                        self.level.current_step, 0
                    )) + f' / {hub.metadata.max_drones}'
                )
                for hub in self.level.hubs.values()
            ]
        ])

        self.text_box_debug.draw()

    def draw(self) -> None:
        self._draw_help()
        self._draw_state()
        self._draw_crosshair()
        self._draw_current_target()
        self._draw_debug()

    def unload(self) -> None:
        self.logger.log('Unloading UI renderer...')
