from .EnvironmentRenderer import EnvironmentRenderer
from .ConnectionRenderer import ConnectionRenderer
from .InputController import InputController
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
    input_controller: InputController
    ray_cast: RayCast

    hub_renderer: HubRenderer
    connection_renderer: ConnectionRenderer
    drones_renderer: DronesRenderer
    ui_renderer: UIRenderer

    def __init__(self, level: Level, verbose: bool = False) -> None:
        self.title = "Fly In - Renderer"
        self.logger = Logger(
            print_log=verbose,
            name='Renderer',
            color=Color.CYAN
        )
        self.logger.log('Initializing renderer...')

        self.level = level
        pr.set_trace_log_level(7)
        pr.init_window(self.WIDTH, self.HEIGHT, self.title)
        pr.set_target_fps(60)

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

        self.input_controller = InputController(
            self.camera,
            self.WIDTH,
            self.HEIGHT
        )
        self.ray_cast = RayCast(self.level)

        self.environment_renderer = EnvironmentRenderer(self.level)
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
            time: float = pr.get_time()
            # pr.update_camera(self.camera, pr.CameraMode.CAMERA_FREE)

            # Update
            self.input_controller.update()
            self.environment_renderer.update(time)
            self.hub_renderer.update()
            self.connection_renderer.update()
            self.drones_renderer.update()

            ray = pr.get_screen_to_world_ray(
                self.input_controller.get_current_pointing(),
                self.camera
            )
            self.ui_renderer.update(ray)

            # Clear and start drawing
            # pr.rl_set_clip_planes(0.1, 100000.0)
            pr.begin_drawing()
            pr.clear_background(pr.BLACK)

            # 3D scene
            pr.begin_mode_3d(self.camera)
            self.environment_renderer.draw()
            self.connection_renderer.draw()
            self.hub_renderer.draw()
            self.drones_renderer.draw()
            pr.end_mode_3d()

            # 2D overlay
            self.ui_renderer.draw()

            pr.end_drawing()

        self.logger.log('Closing renderer...')
        self.environment_renderer.unload()
        self.hub_renderer.unload()
        self.connection_renderer.unload()
        self.drones_renderer.unload()
        pr.close_window()
