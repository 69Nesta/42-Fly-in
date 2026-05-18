"""Network graph representation for drone delivery routes.

Provides the core network model with nodes, connections, and metadata:
- Network: Complete graph model with drones and pathfinding
- Node: Network nodes representing delivery locations or hubs
- Connection: Bidirectional edges with capacity constraints
- Drone: Virtual delivery agents moving through the network
- Metadata: Type information and styling for network components
"""

from .network_object import NetworkObject
from .metadata import (
    ConnectionMetadata,
    ColorMetadata,
    NodeMetadata,
    ZoneType,
    ZoneCost
)
from .node import Node, NodeType
from .connection import Connection, ConnectionManager
from .network import Network


__all__: list[str] = [
    'ConnectionMetadata',
    'ConnectionManager',
    'ColorMetadata',
    'NetworkObject',
    'NodeMetadata',
    'Connection',
    'ZoneType',
    'ZoneCost',
    'NodeType',
    'Node',
    'Network',
]
