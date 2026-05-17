from pyray import Vector2, Color
from typing import Optional
import pyray as pr


class TextBox():
    """Renders a styled text box on the screen.

    Displays multi-line text with configurable alignment, colors, and styling.
    Supports per-line color customization.

    Attributes:
        lines: List of text lines to display.
        position: Screen position for the text box.
        font_size: Font size for rendering.
        text_color: Default text color.
        background_color: Background color.
        screen_width: Screen width in pixels.
        screen_height: Screen height in pixels.
        text_space: Vertical spacing between lines.
        is_top_align: Whether to align to top.
        is_left_align: Whether to align to left.
        in_x_space: Inner horizontal padding.
        in_y_space: Inner vertical padding.
        out_x_space: Outer horizontal padding.
        out_y_space: Outer vertical padding.
        width: Calculated text box width.
        height: Calculated text box height.
        left_align: Calculated left position.
        top_align: Calculated top position.
        color_option: Per-line color overrides.
    """
    lines: list[str]
    position: Vector2
    font_size: int
    text_color: Color
    background_color: Color

    screen_width: int
    screen_height: int

    text_space: int

    is_top_align: bool
    is_left_align: bool

    in_x_space: int
    in_y_space: int
    out_x_space: int
    out_y_space: int

    width: int
    height: int
    left_align: int
    top_align: int
    color_option: dict[int, Color]

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
                out_y_space: int = 10
            ) -> None:
        """Initialize a text box.

        Args:
            font_size: Font size for text.
            text_color: Default text color.
            background_color: Background color.
            screen_width: Screen width in pixels.
            screen_height: Screen height in pixels.
            top_align: Align to top of screen. Defaults to True.
            left_align: Align to left of screen. Defaults to True.
            text_space: Vertical spacing between lines. Defaults to 25.
            in_x_space: Inner horizontal padding. Defaults to 10.
            in_y_space: Inner vertical padding. Defaults to 10.
            out_x_space: Outer horizontal padding. Defaults to 10.
            out_y_space: Outer vertical padding. Defaults to 10.
        """
        self.font_size = font_size
        self.text_color = text_color
        self.background_color = background_color

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.text_space = text_space

        self.is_top_align = top_align
        self.is_left_align = left_align

        self.in_x_space = in_x_space
        self.in_y_space = in_y_space
        self.out_x_space = out_x_space
        self.out_y_space = out_y_space

    def _calculate_lines(self) -> None:
        """Calculate text box dimensions based on content and alignment."""
        max_line_length: int = max(
            [pr.measure_text(line, self.font_size) for line in self.lines]
        ) if len(self.lines) > 0 else 0
        self.width = max_line_length + self.in_x_space * 2
        self.height = self.text_space * len(self.lines) + self.in_y_space * 2
        self.left_align = (
            self.out_x_space
            if self.is_left_align
            else self.screen_width - self.width - self.out_x_space
        )
        self.top_align = (
            self.out_y_space
            if self.is_top_align
            else self.screen_height - self.height - self.out_y_space
        )

    def set_lines(
                self,
                lines: list[str],
                color_option: dict[int, Color] = {}
            ) -> None:
        """Set the text lines and optional per-line colors.

        Args:
            lines: List of text lines to display.
            color_option: Dictionary mapping line index to color. Defaults to
            empty.
        """
        self.lines = lines
        self.color_option = color_option

        self._calculate_lines()

    def update_lines(
                self,
                lines: list[str],
                color_option: dict[int, Color] = {}
            ) -> None:
        """Update all lines and colors (alias for set_lines).

        Args:
            lines: List of text lines to display.
            color_option: Dictionary mapping line index to color. Defaults to
            empty.
        """
        self.set_lines(lines, color_option)

    def update_line(
                self,
                index: int,
                line: str,
                color_option: Optional[Color] = None
            ) -> None:
        """Update a single line's text and optional color.

        Args:
            index: Line index to update.
            line: New text for the line.
            color_option: Optional color override for the line. Defaults to
            None.
        """
        if index < 0 or index >= len(self.lines):
            return
        self.lines[index] = line
        if color_option is not None:
            self.color_option[index] = color_option

        self._calculate_lines()

    def draw(self) -> None:
        """Draw the text box with background, border, and styled text."""
        if self.lines is None or len(self.lines) == 0:
            return

        pr.draw_rectangle(
            self.left_align, self.top_align,
            self.width, self.height,
            self.background_color
        )
        pr.draw_rectangle_lines(
            self.left_align, self.top_align,
            self.width, self.height,
            self.text_color
        )

        for i, line in enumerate(self.lines):
            pr.draw_text(
                line,
                self.left_align + self.in_x_space,
                self.top_align + self.in_y_space + self.text_space * i,
                self.font_size,
                self.color_option.get(i, self.text_color)
            )
