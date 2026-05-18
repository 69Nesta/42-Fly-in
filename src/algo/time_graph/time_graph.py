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
    logger: Logger

    network: 'Network'

    step: int
    step_dict: dict[int, set[Node]]

    def __init__(self, verbose: bool, network: 'Network') -> None:
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
        return GraphNode(time, object)

    @lru_cache(maxsize=None)
    def create_connection_node(
                self,
                time: int,
                object: NetworkNode,
                connection: Connection
            ) -> ConnectionNode:
        return ConnectionNode(time, object, connection)

    def add_connection(
                self,
                from_node: Node,
                next_time: int,
                next_object: NetworkNode
            ) -> None:

        new_node: Node = self.create_node(next_time, next_object)
        new_node.add_connection(from_node)

    def get_step(self, step: int) -> set[Node]:
        for _ in range(step - self.step):
            self.next_step()
        return self.step_dict.get(step, set())

    def next_step(self) -> None:
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
