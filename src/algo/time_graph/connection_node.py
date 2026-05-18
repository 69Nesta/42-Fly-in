from ...network import Connection, Node as NetworkNode
from .node import Node


class ConnectionNode(Node):
    """A node representing a restricted-zone connection at a time step.

    Models drones being on a restricted-zone connection at a specific time.
    These nodes are used to enforce time constraints on restricted zones.

    Attributes:
        network_connection: The Connection object being traversed.
    """
    network_connection: Connection

    def __init__(
                self,
                time: int,
                object: NetworkNode,
                network_connection: Connection
            ) -> None:
        """Initialize a connection node.

        Args:
            time: The time step.
            object: The source network node.
            network_connection: The Connection being traversed.
        """
        super().__init__(time, object)
        self.network_connection = network_connection

    def get_name(self) -> str:
        """Get the display name of this connection.

        Returns:
            The name of the underlying network connection.
        """
        return self.network_connection.get_name()

    def get_network_connection(self) -> Connection:
        """Get the network connection object.

        Returns:
            The Connection object being traversed.
        """
        return self.network_connection
