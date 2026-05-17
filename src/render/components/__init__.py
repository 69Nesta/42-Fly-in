"""UI components for rendering text and labels.

Provides reusable UI elements for displaying information on screen:
- TextBox: Multi-line styled text display with per-line colors
- NameTag: 3D world-space name tags that scale with distance
"""

from .text_box import TextBox
from .name_tag import NameTag


__all__: list[str] = [
    'text_box',
    'name_tag',
]
