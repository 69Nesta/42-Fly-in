from ...network import NetworkObject


class Node:
    time: int
    object: NetworkObject
    connections: list[tuple['Node', NetworkObject | None]]

    capacity: int
    flow: int

    def __init__(
                self,
                time: int,
                object: NetworkObject,
            ) -> None:
        self.time = time
        self.object = object
        self.connections = []
        self.capacity = object.get_capacity()
        self.flow = 0

    def add_flow(self, amount: int) -> None:
        if self.flow + amount > self.capacity:
            raise ValueError(
                f'Cannot add flow of {amount} to node at time {self.time} '
                f'with capacity {self.capacity} and current flow {self.flow}.'
            )
        self.flow += amount

    def remove_flow(self, amount: int) -> None:
        self.flow = min(self.flow - amount, 0)

    def get_remaining_capacity(self) -> int:
        return self.capacity - self.flow

    def add_connection(
                self,
                node: 'Node',
                connection: NetworkObject | None = None
            ) -> None:
        self.connections.append((node, connection))
