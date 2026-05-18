from enum import Enum


class ColorMetadata(Enum):
    """Enumeration of available colors for nodes and UI elements.

    Attributes:
        NONE: No color specified.
        LIME: Lime color.
        MAGENTA: Magenta color.
        CYAN: Cyan color.
        BLUE: Blue color.
        RED: Red color.
        GREEN: Green color.
        YELLOW: Yellow color.
        GRAY: Gray color.
        PURPLE: Purple color.
        BLACK: Black color.
        BROWN: Brown color.
        ORANGE: Orange color.
        MAROON: Maroon color.
        GOLD: Gold color.
        DARKRED: Dark red color.
        VIOLET: Violet color.
        CRIMSON: Crimson color.
        RAINBOW: Rainbow color.
    """
    NONE = None
    LIME = 'lime'
    MAGENTA = 'magenta'
    CYAN = 'cyan'
    BLUE = 'blue'
    RED = 'red'
    GREEN = 'green'
    YELLOW = 'yellow'
    GRAY = 'gray'
    PURPLE = 'purple'
    BLACK = 'black'
    BROWN = 'brown'
    ORANGE = 'orange'
    MAROON = 'maroon'
    GOLD = 'gold'
    DARKRED = 'darkred'
    VIOLET = 'violet'
    CRIMSON = 'crimson'
    RAINBOW = 'rainbow'

    @staticmethod
    def has_value(value: str | None) -> bool:
        """Check if a value exists in the EColor enumeration.

        Args:
            value: The color value to check.

        Returns:
            True if the value exists in EColor, False otherwise.
        """
        return value in (item.value for item in ColorMetadata)
