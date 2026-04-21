from enum import Enum


class EColor(Enum):
    NONE = None
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
        return value in (item.value for item in EColor)
