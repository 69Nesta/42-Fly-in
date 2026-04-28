"""Utility modules for math, strings, animation, and logging.

Provides helper utilities:
- MathUtils: Geometric calculations (distance, angles)
- StrUtils: String manipulation (truncation)
- Bezier: Cubic Bézier curve interpolation for smooth animations
- Logger: Colored debug logging system
- Color: Color definition and management
"""

from .MathUtils import MathUtils
from .StrUtils import StrUtils
from .Bezier import Bezier
from .Logger import Logger
from .Color import Color


__all__: list[str] = [
    'MathUtils',
    'StrUtils',
    'Bezier',
    'Logger',
    'Color'
]
