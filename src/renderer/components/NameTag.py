from pyray import Vector3, Camera3D, Color
import pyray as pr


class NameTag:
    # Rendering
    text: str
    offset_y: float
    camera: Camera3D

    # Style
    base_font_size: int
    min_scale: float
    max_scale: float
    padding: float

    # Colors
    text_color: Color
    shadow_color: Color
    bg_color: Color

    def __init__(
                self,
                text: str,
                camera: Camera3D,
                offset_y: float = 2.0,
                font_size: int = 20,
                min_scale: float = 0.5,
                max_scale: float = 2.0,
                padding: float = 4,
                text_color: Color = pr.WHITE,
                shadow_color: Color = pr.BLACK,
                bg_color: Color = Color(0, 0, 0, 120)
            ) -> None:
        self.text = text
        self.offset_y = offset_y
        self.camera = camera

        # Style
        self.base_font_size = font_size
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.padding = padding

        # Colors
        self.text_color = text_color
        self.shadow_color = shadow_color
        self.bg_color = bg_color

    def set_text(self, text: str) -> None:
        self.text = text

    def set_offset_y(self, offset_y: float) -> None:
        self.offset_y = offset_y

    def draw(self, position: Vector3):
        pos3d = Vector3(
            position.x,
            position.y + self.offset_y,
            position.z
        )

        screen = pr.get_world_to_screen(pos3d, self.camera)
        distance = pr.vector3_distance(self.camera.position, pos3d)

        if distance <= 0.01:
            return

        scale = 10 / distance
        scale = max(self.min_scale, min(self.max_scale, scale))

        font_size = int(self.base_font_size * scale)

        text_width = pr.measure_text(self.text, font_size)

        x = int(screen.x - text_width / 2)
        y = int(screen.y)

        pr.draw_rectangle(
            x - self.padding,
            y - self.padding // 2,
            text_width + self.padding * 2,
            font_size + self.padding,
            self.bg_color
        )
        pr.draw_text(
            self.text,
            x + 1,
            y + 1,
            font_size,
            self.shadow_color
        )
        pr.draw_text(
            self.text,
            x,
            y,
            font_size,
            self.text_color
        )
