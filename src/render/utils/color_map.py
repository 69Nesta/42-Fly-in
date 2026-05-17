"""Color mapping from application enums to PyRay colors.

Provides a dictionary mapping EColor enum values to PyRay color constants
for consistent color rendering throughout the application.
"""

import pyray as pr
from ...network.metadata import ColorMetadata as Color


color_map: dict[Color, pr.Color] = {
    Color.NONE: pr.RAYWHITE,
    Color.BLUE: pr.BLUE,
    Color.RED: pr.RED,
    Color.GREEN: pr.GREEN,
    Color.YELLOW: pr.YELLOW,
    Color.GRAY: pr.GRAY,
    Color.PURPLE: pr.PURPLE,
    Color.BLACK: pr.BLACK,
    Color.BROWN: pr.BROWN,
    Color.ORANGE: pr.ORANGE,
    Color.MAROON: pr.MAROON,
    Color.GOLD: pr.GOLD,
    Color.DARKRED: pr.MAROON,
    Color.VIOLET: pr.VIOLET,
    Color.CRIMSON: pr.MAGENTA,
    Color.RAINBOW: pr.RAYWHITE,
}
