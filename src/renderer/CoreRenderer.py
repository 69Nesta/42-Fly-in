from .EnvironementRenderer import EnvironementRenderer
from .ConnectionRenderer import ConnectionRenderer
from .DronesRenderer import DronesRenderer
from .HubRenderer import HubRenderer
from .UIRenderer import UIRenderer
from pyray import Vector3
from ..utils import Logger, Color
from .RayCast import RayCast
from ..Level import Level
import pyray as pr


class CoreRenderer:
    WIDTH: int = 1280
    HEIGHT: int = 720

    logger: Logger
    level: Level

    title: str
    camera: pr.Camera3D
    ray_cast: RayCast

    hub_renderer: HubRenderer
    connection_renderer: ConnectionRenderer
    drones_renderer: DronesRenderer
    ui_renderer: UIRenderer

    def __init__(self, level: Level, verbose: bool = False) -> None:
        self.title = "Fly In"
        self.logger = Logger(
            print_log=verbose,
            name='Renderer',
            color=Color.CYAN
        )
        self.logger.log('Initializing renderer...')

        self.level = level
        # pr.set_trace_log_level(7)
        pr.init_window(self.WIDTH, self.HEIGHT, self.title)
        pr.set_target_fps(60)
        pr.disable_cursor()

        self.camera = pr.Camera3D(
            Vector3(10.0, 4.0, 10.0),
            Vector3(0.0, 0.0, 0.0),
            Vector3(0.0, 1.0, 0.0),
            60.0,
            pr.CameraProjection.CAMERA_PERSPECTIVE,
        )

        pr.gui_set_style(
            pr.GuiControl.DEFAULT, pr.GuiDefaultProperty.TEXT_SIZE, 30
        )

        self.ray_cast = RayCast(self.level)

        self.environement_renderer = EnvironementRenderer(self.level)
        self.hub_renderer = HubRenderer(self.level, self.ray_cast)
        self.connection_renderer = ConnectionRenderer(self.level)
        self.drones_renderer = DronesRenderer(self.level, self.ray_cast)
        self.ui_renderer = UIRenderer(
            self.level,
            self.WIDTH, self.HEIGHT,
            self.ray_cast
        )

    def run(self) -> None:
        while not pr.window_should_close():
            # mouse_pos: Vector2 = pr.get_mouse_position()
            time: float = pr.get_time()
            pr.update_camera(self.camera, pr.CameraMode.CAMERA_FREE)

            # Update
            self.environement_renderer.update(time)
            self.hub_renderer.update()
            self.connection_renderer.update()
            self.drones_renderer.update()

            center_screen = pr.Vector2(self.WIDTH / 2.0, self.HEIGHT / 2.0)
            ray = pr.get_screen_to_world_ray(center_screen, self.camera)
            self.ui_renderer.update(ray)

            # Clear and start drawing
            pr.begin_drawing()
            pr.clear_background(pr.fade(pr.SKYBLUE, 0.1))

            # 3D scene
            pr.begin_mode_3d(self.camera)
            self.environement_renderer.draw()
            self.connection_renderer.draw()
            self.hub_renderer.draw()
            self.drones_renderer.draw()
            pr.end_mode_3d()

            # 2D overlay
            self.ui_renderer.draw()

            pr.end_drawing()

        self.logger.log('Closing renderer...')
        self.environement_renderer.unload()
        self.hub_renderer.unload()
        self.connection_renderer.unload()
        self.drones_renderer.unload()
        pr.close_window()
