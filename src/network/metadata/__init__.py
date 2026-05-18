"""Metadata and type information for network components.

Defines properties and styling for nodes, connections, and zones:
- NodeMetadata: Zone type, cost, and styling for nodes
- ConnectionMetadata: Capacity and properties for connections
- ColorMetadata: Color definitions for visual components
- ZoneType: Enumeration of zone types (hub, standard, etc.)
- ZoneCost: Cost multipliers for different zone types
"""

from .color_metadata import ColorMetadata
from .node_metadata import ZoneType, ZoneCost, NodeMetadata
from .connection_metadata import ConnectionMetadata

__all__: list[str] = [
    'ConnectionMetadata',
    'ColorMetadata',
    'NodeMetadata',
    'ZoneType',
    'ZoneCost'
]
