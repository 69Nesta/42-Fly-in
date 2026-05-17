from .connection import Connection


class ConnectionManager:
    """Container managing a collection of connections between nodes.

    Attributes:
        _connections: Internal list of Connection objects.
    """
    _connections: list[Connection]

    def __init__(self) -> None:
        """Initialize an empty connections container."""
        self._connections = []

    def add(self, connection: Connection) -> list[Connection]:
        """Add a connection to the collection.

        Args:
            connection: The Connection to add.

        Returns:
            The updated list of all connections.

        Raises:
            ValueError: If a connection between these hubs already exists.
        """
        if hash(connection) in [
                    hash(_connection) for _connection in self._connections
                ]:
            raise ValueError(
                f'Connection between {connection.nodes[0].name!r} and '
                f'{connection.nodes[1].name!r} already exists'
            )

        self._connections.append(connection)
        return self._connections

    @property
    def all(self) -> list[Connection]:
        """Get all connections.

        Returns:
            List of all Connection objects.
        """
        return self._connections
