from ...network import NetworkObject, Connection


class Node:
    time: int
    object: NetworkObject
    connections: list[tuple['Node', Connection]]

    def __init__(self, time: int, object: NetworkObject):
        self.time = time
        self.object = object
        self.connections = []

    def add_connection(self, node: 'Node', connection: Connection) -> None:
        self.connections.append((node, connection))
