"""Connection management and graph edges.

Provides bidirectional connection representation with capacity constraints:
- Connection: Edges between network nodes with capacity limits
- ConnectionManager: Manages all connections in the network
"""

from .connection_manager import ConnectionManager
from .connection import Connection


__all__: list[str] = [
    'ConnectionManager',
    'Connection',
]
