"""Utility modules for math, strings, animation, and logging.

Provides helper utilities:
- MathUtils: Geometric calculations (distance, angles)
- StrUtils: String manipulation (truncation)
- Bezier: Cubic Bézier curve interpolation for smooth animations
- Logger: Colored debug logging system
- Color: Color definition and management
"""

from .math_utils import MathUtils
from .str_utils import StrUtils
from .bezier import Bezier
from .logger import Logger
from .color import Color


__all__: list[str] = [
    'MathUtils',
    'StrUtils',
    'Bezier',
    'Logger',
    'Color'
]
