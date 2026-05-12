from .connection_node import ConnectionNode
from ...network.network import Network
from ...network import NetworkObject, Node as NetworkNode
from ...utils import Logger, Color
from .node import Node

from functools import lru_cache


class TimeGraph:
    logger: Logger

    network: Network
    nodes: list[Node]

    step: int
    step_dict: dict[int, set[Node]]

    def __init__(self, verbose: bool, network: Network) -> None:
        self.logger = Logger(
            name='TimeGraph',
            print_log=verbose,
            color=Color.GREEN
        )
        self.logger.log('Initializing TimeGraph...')
        self.network = network

        self.nodes = []
        self.step = 0
        self.step_dict = {
            0: set({self.create_node(0, self.network.start_node)})
        }

    @lru_cache(maxsize=None)
    def create_node(
                self,
                time: int,
                object: NetworkObject,
                node_type: type[Node] = Node
            ) -> Node:
        node: Node = node_type(time, object)
        self.nodes.append(node)

        return node

    def add_connection(
                self,
                from_node: Node,
                next_time: int,
                next_object: NetworkObject
            ) -> None:

        new_node: Node = self.create_node(next_time, next_object)
        new_node.add_connection(from_node)

    def next_step(self) -> None:
        self.logger.log('Creating TimeGraph...')
        for node in self.step_dict.get(self.step, set()):
            new_step: int = self.step + 1
            new_node: Node = self.create_node(
                new_step,
                node.object
            )
            new_node.add_connection(node)
            self.step_dict.setdefault(new_step, set()).add(new_node)

            if isinstance(node, ConnectionNode):
                continue
            if not isinstance(node.object, NetworkNode):
                continue
            for zone, connection in node.object.get_connections():
                if zone.get_capacity() <= 0 or zone.is_blocked():
                    continue
                if connection.get_capacity() <= 0:
                    continue

                new_neighbor: Node
                if zone.is_restricted():
                    new_neighbor = self.create_node(
                        new_step,
                        zone,
                        node_type=ConnectionNode
                    )
                else:
                    new_neighbor = self.create_node(
                        new_step,
                        zone
                    )

                new_neighbor.add_connection(node, connection)
                self.step_dict.setdefault(new_step, set()).add(new_neighbor)

        self.step += 1
