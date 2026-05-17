from ...network import Node as NetworkNode, Connection


class Node:
    time: int
    object: NetworkNode
    connections: list[tuple['Node', Connection | None]]

    def __init__(
                self,
                time: int,
                object: NetworkNode,
            ) -> None:
        self.time = time
        self.object = object
        self.connections = []

    def add_connection(
                self,
                node: 'Node',
                connection: Connection | None = None
            ) -> None:
        if (node, connection) in self.connections:
            return
        self.connections.append((node, connection))

    def get_name(self) -> str:
        return self.object.get_name()

    def get_connections(self) -> list[tuple['Node', Connection | None]]:
        return self.connections
