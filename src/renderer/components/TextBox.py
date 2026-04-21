from pyray import Vector2, Color
import pyray as pr


class TextBox():
    lines: list[str]
    position: Vector2
    font_size: int
    text_color: Color
    background_color: Color

    screen_width: int
    screen_height: int

    text_space: int

    top_align: bool
    left_align: bool

    in_x_space: int
    in_y_space: int
    out_x_space: int
    out_y_space: int

    def __init__(
                self,
                font_size: int,
                text_color: Color,
                background_color: Color,
                screen_width: int,
                screen_height: int,
                top_align: bool = True,
                left_align: bool = True,
                text_space: int = 25,
                in_x_space: int = 10,
                in_y_space: int = 10,
                out_x_space: int = 10,
                out_y_space: int = 10,
            ) -> None:
        self.lines = []
        self.font_size = font_size
        self.text_color = text_color
        self.background_color = background_color

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.text_space = text_space

        self.top_align = top_align
        self.left_align = left_align

        self.in_x_space = in_x_space
        self.in_y_space = in_y_space
        self.out_x_space = out_x_space
        self.out_y_space = out_y_space

    def draw(
                self,
                lines: list[str],
                color_option: dict[int, Color] = {}
            ) -> None:
        max_line_length: int = max(
            [pr.measure_text(line, self.font_size) for line in lines]
        ) if len(lines) > 0 else 0
        width: int = max_line_length + self.in_x_space * 2
        height: int = self.text_space * len(lines) + self.in_y_space * 2
        left_align: int = (
            self.out_x_space
            if self.left_align
            else self.screen_width - width - self.out_x_space
        )
        top_align: int = (
            self.out_y_space
            if self.top_align
            else self.screen_height - height - self.out_y_space
        )

        pr.draw_rectangle(
            left_align, top_align,
            width, height,
            self.background_color
        )
        pr.draw_rectangle_lines(
            left_align, top_align,
            width, height,
            self.text_color
        )

        for i, line in enumerate(lines):
            pr.draw_text(
                line,
                left_align + self.in_x_space,
                top_align + self.in_y_space + self.text_space * i,
                self.font_size,
                color_option.get(i, self.text_color)
            )
