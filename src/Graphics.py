from .utils import Logger, Color
import pyray as pr


class Graphics:
    def __init__(self, verbose: bool = False) -> None:
        self.window_width: int = 1200
        self.window_height: int = 700
        self.title: str = "Fly In"
        self.mouse_status: bool = True
        self.move_speed: float = 0.1
        self.camera: pr.Camera3D = pr.Camera3D()
        self.logger: Logger = Logger(
            ACTIVE=verbose,
            name='Graphics',
            color=Color.CYAN
        )

        self.camera.up = pr.Vector3(0.0, 1.0, 0.0)
        self.camera.fovy = 75.0
        self.camera.projection = pr.CameraProjection.CAMERA_PERSPECTIVE
        self.camera.target = pr.Vector3(-1.75, 0.9, 0.55)
        self.camera.position = pr.Vector3(-2.3, 1.2, 0.55)

        pr.set_trace_log_level(7)
        pr.set_config_flags(pr.ConfigFlags.FLAG_MSAA_4X_HINT)
        pr.init_window(self.window_width, self.window_height, self.title)
        pr.set_exit_key(pr.KeyboardKey.KEY_ESCAPE)
        pr.set_target_fps(60)
        pr.gui_set_style(pr.GuiControl.DEFAULT,
                         pr.GuiDefaultProperty.TEXT_SIZE, 30)

    def get_virtual_mouse_position(self) -> pr.Vector3:
        mouse_pos = pr.get_mouse_position()

        self.logger.log(f"Mouse Position: {mouse_pos.x}, {mouse_pos.y}")

        return mouse_pos

    def _refresh_camera(self) -> None:
        mouse_delta = pr.get_mouse_delta()
        rotation = pr.Vector3(mouse_delta.x * 0.1, mouse_delta.y * 0.1, 0.0)
        movement = pr.Vector3(0.0, 0.0, 0.0)
        zoom = 0.0
        pr.update_camera_pro(self.camera, movement, rotation, zoom)

    def run(self) -> None:
        while not pr.window_should_close():
            if pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_RIGHT):
                if self.mouse_status:
                    pr.disable_cursor()
                    self.mouse_status = False
                self._refresh_camera()
            else:
                if not self.mouse_status:
                    pr.enable_cursor()
                    self.mouse_status = True

            if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_LEFT):
                self.get_virtual_mouse_position()

            pr.begin_drawing()
            pr.clear_background(pr.BLACK)
            pr.begin_mode_3d(self.camera)

            # pr.draw_circle_3d(pr.Vector3(0, 0, 0), 1.0, pr.Vector3(0, 0, 0), 0.0, pr.RED)

            pr.end_mode_3d()

            self.draw_hud()

            pr.end_drawing()

        pr.close_window()

    def draw_hud(self) -> None:
        tmp = "[Home]/[End] to add/remove 3D text layers"
        width = pr.measure_text(tmp, 10)
        pr.draw_text(tmp, self.window_width - 20 - width, 25, 10, pr.DARKGRAY)
        pr.draw_fps(10, 10
