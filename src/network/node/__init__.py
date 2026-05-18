"""Network node representation and node types.

Defines graph vertices and their classification:
- Node: Individual network node with position and metadata
- NodeType: Enumeration of node types (start, end, hub, delivery point)
"""

from .node_type import NodeType
from .node import Node


__all__: list[str] = [
    'NodeType',
    'Node'
]
