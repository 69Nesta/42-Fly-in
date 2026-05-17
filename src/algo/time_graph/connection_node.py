from ...network import Connection, Node as NetworkNode
from .node import Node


class ConnectionNode(Node):
    network_connection: Connection

    def __init__(
                self,
                time: int,
                object: NetworkNode,
                network_connection: Connection
            ) -> None:
        super().__init__(time, object)
        self.network_connection = network_connection

    def get_name(self) -> str:
        return self.network_connection.get_name()

    def get_network_connection(self) -> Connection:
        return self.network_connection
