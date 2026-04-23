import pyray as pr
import math


class InputController:
    HEIGHT: int
    WIDTH: int

    camera: pr.Camera3D
    base_move_speed: float = 0.15
    move_speed: float

    focused_mouse: bool

    def __init__(self, camera: pr.Camera3D, WIDTH: int, HEIGHT: int) -> None:
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.camera = camera

        self.move_speed = self.base_move_speed
        self.focused_mouse = True

        if self.focused_mouse:
            pr.disable_cursor()

    def get_current_pointing(self) -> pr.Vector2:
        if not self.focused_mouse:
            return pr.get_mouse_position()
        return pr.Vector2(self.WIDTH / 2.0, self.HEIGHT / 2.0)

    def update(self) -> None:
        if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_RIGHT):
            self.focused_mouse = not self.focused_mouse
            if self.focused_mouse:
                pr.disable_cursor()
            else:
                pr.enable_cursor()
        self._update_movement_speed()
        self._update_camera_position()
        self._update_camera_rotation()

    def _update_camera_position(self) -> None:
        dx = self.camera.target.x - self.camera.position.x
        dz = self.camera.target.z - self.camera.position.z
        dy = self.camera.target.y - self.camera.position.y
        length = math.sqrt(dx*dx + dz*dz + dy*dy)
        if length > 0:
            dx /= length
            dz /= length
            dy /= length

            if pr.is_key_down(pr.KeyboardKey.KEY_W):
                self.camera.position.x += dx * self.move_speed
                self.camera.position.z += dz * self.move_speed
                self.camera.position.y += dy * self.move_speed
                self.camera.target.x += dx * self.move_speed
                self.camera.target.z += dz * self.move_speed
                self.camera.target.y += dy * self.move_speed

            if pr.is_key_down(pr.KeyboardKey.KEY_S):
                self.camera.position.x -= dx * self.move_speed
                self.camera.position.z -= dz * self.move_speed
                self.camera.position.y -= dy * self.move_speed
                self.camera.target.x -= dx * self.move_speed
                self.camera.target.z -= dz * self.move_speed
                self.camera.target.y -= dy * self.move_speed

            if pr.is_key_down(pr.KeyboardKey.KEY_D):
                self.camera.position.x += -dz * self.move_speed
                self.camera.position.z += dx * self.move_speed
                self.camera.target.x += -dz * self.move_speed
                self.camera.target.z += dx * self.move_speed

            if pr.is_key_down(pr.KeyboardKey.KEY_A):
                self.camera.position.x -= -dz * self.move_speed
                self.camera.position.z -= dx * self.move_speed
                self.camera.target.x -= -dz * self.move_speed
                self.camera.target.z -= dx * self.move_speed

            if pr.is_key_down(pr.KeyboardKey.KEY_SPACE):
                self.camera.position.y += self.move_speed
                self.camera.target.y += self.move_speed

            if pr.is_key_down(pr.KeyboardKey.KEY_LEFT_SHIFT):
                self.camera.position.y -= self.move_speed
                self.camera.target.y -= self.move_speed

    def _update_camera_rotation(self) -> None:
        if self.focused_mouse:
            mouse_delta = pr.get_mouse_delta()
            rotation = pr.Vector3(
                mouse_delta.x * 0.1,
                mouse_delta.y * 0.1,
                0.0
            )
            movement = pr.Vector3(0.0, 0.0, 0.0)
            zoom = 0.0
            pr.update_camera_pro(self.camera, movement, rotation, zoom)

    def _update_movement_speed(self) -> None:
        if pr.is_key_down(pr.KeyboardKey.KEY_LEFT_CONTROL):
            self.move_speed = self.base_move_speed * 2.0
        else:
            self.move_speed = self.base_move_speed

    def is_mouse_focused(self) -> bool:
        return self.focused_mouse
