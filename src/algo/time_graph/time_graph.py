from ...network import Node as NetworkNode, Connection
from .connection_node import ConnectionNode
from ...utils import Logger, Color
from .graph_node import GraphNode
from .node import Node

from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...network import Network


class TimeGraph:
    """A time-expanded graph representation of the network.

    Creates a layered graph where each layer represents a time step. Each
    network node appears at each time step, and transitions model both
    staying at a node and moving along connections over one time unit.

    Attributes:
        logger: Logger instance for debug output.
        network: The Network instance being expanded.
        step: Current maximum time step in the graph.
        step_dict: Dictionary mapping time steps to sets of reachable nodes.
    """
    logger: Logger

    network: 'Network'

    step: int
    step_dict: dict[int, set[Node]]

    def __init__(self, verbose: bool, network: 'Network') -> None:
        """Initialize the time-expanded graph.

        Args:
            verbose: Whether to enable verbose logging.
            network: The Network instance to expand.
        """
        self.logger = Logger(
            name='TimeGraph',
            print_log=verbose,
            color=Color.GREEN
        )
        self.logger.log('Initializing TimeGraph...')
        self.network = network

        self.step = 0
        self.step_dict = {
            0: set({self.create_node(0, self.network.start_node)})
        }

    @lru_cache(maxsize=None)
    def create_node(
                self,
                time: int,
                object: NetworkNode,
            ) -> Node:
        """Create or retrieve a cached time-graph node.

        Args:
            time: The time step.
            object: The network node at this time step.

        Returns:
            A GraphNode wrapping the network node at the time step.
        """
        return GraphNode(time, object)

    @lru_cache(maxsize=None)
    def create_connection_node(
                self,
                time: int,
                object: NetworkNode,
                connection: Connection
            ) -> ConnectionNode:
        """Create or retrieve a cached connection node.

        Connection nodes represent drones being on a connection (restricted
        zone transition) at a specific time.

        Args:
            time: The time step.
            object: The source network node.
            connection: The network connection being traversed.

        Returns:
            A ConnectionNode wrapping the connection at the time step.
        """
        return ConnectionNode(time, object, connection)

    def add_connection(
                self,
                from_node: Node,
                next_time: int,
                next_object: NetworkNode
            ) -> None:
        """Add a connection between nodes at different time steps.

        Args:
            from_node: The source node.
            next_time: The time of the destination node.
            next_object: The network object at the destination.
        """

        new_node: Node = self.create_node(next_time, next_object)
        new_node.add_connection(from_node)

    def get_step(self, step: int) -> set[Node]:
        """Get all nodes (network objects) reachable at a time step.

        Args:
            step: The time step to retrieve.

        Returns:
            Set of Node objects present at the specified step.
        """
        for _ in range(step - self.step):
            self.next_step()
        return self.step_dict.get(step, set())

    def next_step(self) -> None:
        """Expand the graph to the next time step.

        For each node at the current step, creates transitions to:
        1. The same node at the next time step (waiting)
        2. Connected neighbors at the next time step (moving)

        Takes into account zone restrictions and capacity constraints.
        """
        new_step: int = self.step + 1

        for node in self.step_dict.get(self.step, set()):
            new_current_node: Node = self.create_node(
                new_step,
                node.object
            )
            node.add_connection(new_current_node)
            self.step_dict.setdefault(new_step, set()).add(new_current_node)

            if isinstance(node, ConnectionNode):
                continue

            for zone, connection in node.object.get_connections():
                if zone.get_capacity() <= 0 or zone.is_blocked():
                    continue
                if connection.get_capacity() <= 0:
                    continue

                new_neighbor: Node
                if zone.is_restricted():
                    new_neighbor = self.create_connection_node(
                        new_step,
                        zone,
                        connection
                    )
                else:
                    new_neighbor = self.create_node(
                        new_step,
                        zone
                    )

                node.add_connection(new_neighbor, connection)
                self.step_dict.setdefault(new_step, set()).add(new_neighbor)

        self.step += 1

    def unload(self) -> None:
        """Clear cached nodes to free memory."""
        self.create_node.cache_clear()
        self.create_connection_node.cache_clear()
