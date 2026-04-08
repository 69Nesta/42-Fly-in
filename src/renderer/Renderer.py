from ..utils import Logger, Color
from .Galaxy import Galaxy
import pyray as pr


class Renderer:
    SCREEN_W: int = 1280
    SCREEN_H: int = 720

    title: str
    camera: pr.Camera3D
    galaxy: Galaxy
    logger: Logger

    def __init__(self, verbose: bool = False) -> None:
        self.title = "Fly In"
        self.logger = Logger(
            print_log=verbose,
            name='Renderer',
            color=Color.CYAN
        )
        pr.init_window(self.SCREEN_W, self.SCREEN_H, self.title)
        pr.set_target_fps(60)
        pr.disable_cursor()

        self.camera = pr.Camera3D(
            pr.Vector3(0, 4, 10),
            pr.Vector3(0, 0, 0),
            pr.Vector3(0, 1, 0),
            45.0,
            pr.CameraProjection.CAMERA_PERSPECTIVE,
        )
        pr.gui_set_style(
            pr.GuiControl.DEFAULT, pr.GuiDefaultProperty.TEXT_SIZE, 30
        )

        self.galaxy = Galaxy()

    def run(self) -> None:
        while not pr.window_should_close():
            pr.update_camera(self.camera, pr.CameraMode.CAMERA_FREE)
            time = pr.get_time()

            # Update
            self.galaxy.update(time)

            # Clear and start drawing
            pr.begin_drawing()
            pr.clear_background(pr.BLACK)

            # 3D scene
            pr.begin_mode_3d(self.camera)

            # Draw skybox in skybox
            self.galaxy.draw_3d()

            pr.draw_grid(20, 1.0)
            pr.draw_cube(
                pr.Vector3(0, 0.5, 0),
                1.0, 1.0, 1.0,
                pr.Color(80, 180, 255, 255)
            )
            pr.draw_cube_wires(
                pr.Vector3(0, 0.5, 0),
                1.0, 1.0, 1.0, pr.WHITE
            )
            pr.draw_sphere(
                pr.Vector3(3, 1, -2), 0.8, pr.Color(255, 120, 40, 255)
            )

            pr.end_mode_3d()

            # 2D overlay
            pr.draw_fps(10, 10)
            pr.draw_text(
                'WASD + souris = camera libre', 10, 40, 18, pr.RAYWHITE
            )

            pr.end_drawing()

        self.galaxy.unload()
        pr.close_window()
