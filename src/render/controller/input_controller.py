from enum import Enum
import pyray as pr
import math


class ESettings(Enum):
    """User-configurable settings.

    Attributes:
        SHOW_UI_HELP: Display help overlay.
        SHOW_UI_DEBUG: Display debug information.
    """
    SHOW_UI_HELP = True
    SHOW_UI_DEBUG = False


class InputController:
    """Manages camera and input controls for 3D navigation.

    Handles keyboard input for camera movement, mouse-based camera rotation,
    and setting toggles.

    Attributes:
        HEIGHT: Screen height in pixels.
        WIDTH: Screen width in pixels.
        camera: PyRay Camera3D for 3D view.
        base_move_speed: Base movement speed multiplier.
        move_speed: Current movement speed (affected by modifiers).
        focused_mouse: Whether mouse input focuses on camera rotation.
        _settings: User setting values.
    """
    HEIGHT: int
    WIDTH: int

    camera: pr.Camera3D
    base_move_speed: float = 0.15
    move_speed: float

    focused_mouse: bool

    _settings: dict[ESettings, bool]

    def __init__(self, camera: pr.Camera3D, WIDTH: int, HEIGHT: int) -> None:
        """Initialize the input controller.

        Args:
            camera: The PyRay Camera3D to control.
            WIDTH: Screen width in pixels.
            HEIGHT: Screen height in pixels.
        """
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.camera = camera

        self.move_speed = self.base_move_speed
        self._settings = {}
        self.focused_mouse = True

        if self.focused_mouse:
            pr.disable_cursor()

    def get_setting(self, setting: ESettings) -> bool:
        """Get the current value of a setting.

        Args:
            setting: The setting to retrieve.

        Returns:
            Current setting value, or default if not set.
        """
        if setting not in self._settings:
            return setting.value
        return self._settings[setting]

    def set_setting(self, setting: ESettings, value: bool) -> None:
        """Set the value of a setting.

        Args:
            setting: The setting to modify.
            value: New value for the setting.
        """
        self._settings[setting] = value

    def toggle_setting(self, setting: ESettings) -> None:
        """Toggle a boolean setting to its opposite value.

        Args:
            setting: The setting to toggle.
        """
        current_value = self.get_setting(setting)
        self.set_setting(setting, not current_value)

    def get_current_pointing(self) -> pr.Vector2:
        """Get the current mouse/center screen position.

        Returns:
            Vector2 pointing position (center if focused, mouse position
            otherwise).
        """
        if not self.focused_mouse:
            return pr.get_mouse_position()
        return pr.Vector2(self.WIDTH / 2.0, self.HEIGHT / 2.0)

    def update(self) -> None:
        """Update all input and camera controls.

        Processes keyboard input, mouse input, and applies camera updates.
        """
        self._update_settings()
        self._update_focused_mouse()
        self._update_movement_speed()
        self._update_camera_position()
        self._update_camera_rotation()

    def _update_settings(self) -> None:
        """Handle keyboard input for toggling settings."""
        if pr.is_key_pressed(pr.KeyboardKey.KEY_H):
            self.toggle_setting(ESettings.SHOW_UI_HELP)
        if pr.is_key_pressed(pr.KeyboardKey.KEY_O):
            self.toggle_setting(ESettings.SHOW_UI_DEBUG)

    def _update_focused_mouse(self) -> None:
        """Toggle between focused and free mouse control."""
        if pr.is_mouse_button_pressed(pr.MouseButton.MOUSE_BUTTON_RIGHT):
            self.focused_mouse = not self.focused_mouse
            if self.focused_mouse:
                pr.disable_cursor()
            else:
                pr.enable_cursor()

    def _update_camera_position(self) -> None:
        """Update camera position based on keyboard input."""
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
        """Update camera rotation based on mouse movement."""
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
        """Update movement speed based on control key state."""
        if pr.is_key_down(pr.KeyboardKey.KEY_LEFT_CONTROL):
            self.move_speed = self.base_move_speed * 2.0
        else:
            self.move_speed = self.base_move_speed

    def is_mouse_focused(self) -> bool:
        """Check if mouse is in focused camera control mode.

        Returns:
            True if mouse controls camera rotation, False otherwise.
        """
        return self.focused_mouse
