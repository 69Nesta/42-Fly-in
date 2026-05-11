from ...network import NetworkObject, Connection


class ConnectionNode:
    time: int
    object: NetworkObject
    connection: list[tuple['ConnectionNode', Connection]]

    def __init__(self, time: int, object: NetworkObject):
        self.time = time
        self.object = object
        self.connection = []

    def add_connection(
                self,
                node: 'ConnectionNode',
                connection: Connection
            ) -> None:
        self.connection.append((node, connection))
