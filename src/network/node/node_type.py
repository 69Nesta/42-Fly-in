from enum import Enum


class NodeType(Enum):
    """Enumeration of node types in the network.

    Attributes:
        HUB: Regular node node.
        START_NODE: Starting node for drone routes.
        END_NODE: Destination node for drone routes.
    """
    NODE = 'hub'
    START_NODE = 'start_hub'
    END_NODE = 'end_hub'
