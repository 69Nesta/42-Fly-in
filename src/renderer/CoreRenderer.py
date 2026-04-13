from .EnvironementRenderer import EnvironementRenderer
from .ConnectionRenderer import ConnectionRenderer
from .DronesRenderer import DronesRenderer
from .HubRenderer import HubRenderer
from .UIRenderer import UIRenderer
from ..utils import Logger, Color
from ..Level import Level
from pyray import Vector3
import pyray as pr


class CoreRenderer:
    SCREEN_W: int = 1280
    SCREEN_H: int = 720

    logger: Logger
    level: Level

    title: str
    camera: pr.Camera3D

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
        pr.set_trace_log_level(7)
        pr.init_window(self.SCREEN_W, self.SCREEN_H, self.title)
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

        self.environement_renderer = EnvironementRenderer(self.level)
        self.hub_renderer = HubRenderer(self.level)
        self.connection_renderer = ConnectionRenderer(self.level)
        self.drones_renderer = DronesRenderer(self.level)
        self.ui_renderer = UIRenderer(self.level, self.SCREEN_W, self.SCREEN_H)

    def run(self) -> None:
        while not pr.window_should_close():
            time: float = pr.get_time()
            pr.update_camera(self.camera, pr.CameraMode.CAMERA_FREE)

            # Update
            self.environement_renderer.update(time)
            self.hub_renderer.update()
            self.connection_renderer.update()
            self.drones_renderer.update()
            self.ui_renderer.update()

            # Clear and start drawing
            pr.begin_drawing()
            pr.clear_background(pr.RAYWHITE)

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
