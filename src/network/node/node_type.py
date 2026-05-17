from enum import Enum


class NodeType(Enum):
    """Enumeration of node types in the network.

    Attributes:
        HUB: Regular hub node.
        START_NODE: Starting hub for drone routes.
        END_NODE: Destination hub for drone routes.
    """
    NODE = 'hub'
    START_NODE = 'start_hub'
    END_NODE = 'end_hub'
