from pydantic import BaseModel, Field, PrivateAttr
from typing import Any, Match, Optional
from .Hub import Hub, ZoneType
from pyray import Vector2
import re


CONNECTION_PATTERN = re.compile(
    r'^connection: (\w+)-(\w+)(?:\s+\[([^\]]*)\])?$'
)


class Connection(BaseModel):
    """Represents a bidirectional connection between two hubs.

    Attributes:
        hubs: List of two Hub objects that this connection links.
        capacity: Maximum number of drones allowed on this connection.
        blocked: Whether the connection is blocked for traversal.
    """
    hubs: list[Hub] = Field()
    capacity: int = Field(default=1, ge=0)
    blocked: bool = Field(default=False)

    _hash: int = PrivateAttr()

    def model_post_init(self, context: Any) -> None:
        """Initialize connection after model creation.

        Args:
            context: Pydantic context parameter.
        """
        self._hash = hash(self.hubs[0].name) ^ hash(self.hubs[1].name)
        return super().model_post_init(context)

    def get_id(self) -> str:
        """Get a unique identifier for this connection.

        Returns:
            String identifier in format 'hub1<->hub2'.
        """
        return f'{self.hubs[0].name}<->{self.hubs[1].name}'

    def get_name(self) -> str:
        """Get a human-readable name for this connection.

        Returns:
            String name in format 'hub1 <-> hub2'.
        """
        return f'{self.hubs[0].name} <-> {self.hubs[1].name}'

    def get_travel_time(self, from_hub: Hub) -> int:
        """Get the travel time through this connection from a hub.

        Args:
            from_hub: The hub where the drone is coming from.

        Returns:
            Travel time in steps to the other hub.
        """
        return self.get_other(from_hub).metadata.get_travel_time()

    def get_weight(self, from_hub: Hub) -> float:
        """Get the traversal weight of this connection from a hub.

        Args:
            from_hub: The hub where the drone is coming from.

        Returns:
            Weight value for pathfinding algorithms.
        """
        return self.get_other(from_hub).metadata.get_weight()

    def get_capacity(self) -> int:
        """Get the connection's capacity.

        Returns:
            Maximum number of drones allowed simultaneously.
        """
        return self.capacity

    def get_other(self, hub: Hub) -> Hub:
        """Get the other hub this connection links to.

        Args:
            hub: One of the hubs in this connection.

        Returns:
            The other hub in the connection.
        """
        if self.hubs[0] != hub:
            return self.hubs[0]
        else:
            return self.hubs[1]

    def get_from_str(self, id: str) -> Hub:
        """Get a hub from this connection by its ID.

        Args:
            id: The hub name/ID to find.

        Returns:
            The Hub object with matching ID.

        Raises:
            ValueError: If no hub with the given ID exists in this connection.
        """
        if self.hubs[0].name == id:
            return self.hubs[0]
        elif self.hubs[1].name == id:
            return self.hubs[1]
        else:
            raise ValueError(
                f'Connection does not link hub with id {id!r}: '
                f'{self.hubs[0].name!r} <-> {self.hubs[1].name!r}'
            )

    def calculate_middle_point(self) -> Vector2:
        """Calculate the midpoint between the two hubs.

        Returns:
            Vector2 at the center point between both hubs.
        """
        x = (self.hubs[0].x + self.hubs[1].x) / 2
        y = (self.hubs[0].y + self.hubs[1].y) / 2
        return Vector2(x, y)

    def get_position(self) -> Vector2:
        """Get the connection's position (midpoint).

        Returns:
            Vector2 at the center of the connection.
        """
        return self.calculate_middle_point()

    def intersects_with(self, other: 'Connection') -> Optional[Vector2]:
        """Check if this connection intersects with another.

        Uses line intersection algorithm to detect if two connections cross.

        Args:
            other: Another Connection to check intersection with.

        Returns:
            Vector2 at intersection point if they intersect, None otherwise.
        """
        A: Vector2 = self.hubs[0].get_position()
        B: Vector2 = self.hubs[1].get_position()
        C: Vector2 = other.hubs[0].get_position()
        D: Vector2 = other.hubs[1].get_position()

        denom: float = (A.x - B.x) * (C.y - D.y) - (A.y - B.y) * (C.x - D.x)

        if abs(denom) < 1e-6:
            return None

        t: float = \
            ((A.x - C.x) * (C.y - D.y) - (A.y - C.y) * (C.x - D.x)) / denom
        u: float = \
            ((A.x - C.x) * (A.y - B.y) - (A.y - C.y) * (A.x - B.x)) / denom

        if 0 <= t <= 1 and 0 <= u <= 1:
            x: float = A.x + t * (B.x - A.x)
            y: float = A.y + t * (B.y - A.y)
            return Vector2(x, y)

        return None

    @classmethod
    def from_str(cls, line: str, hubs: dict[str, Hub]) -> 'Connection':
        """Parse a connection from a formatted string line.

        Args:
            line: String in format 'connection: hub1-hub2 [key=value ...]'.
            hubs: Dictionary mapping hub IDs to Hub objects.

        Returns:
            A new Connection instance.

        Raises:
            ValueError: If line format is invalid or references unknown hubs.
        """
        match: Match[str] | None = CONNECTION_PATTERN.match(line.strip())
        if not match:
            raise ValueError(f'Invalid connection line format: {line!r}')

        raw_hub_a, raw_hub_b, attrs_str = match.groups()

        hub_a: Hub | None = hubs.get(raw_hub_a)
        hub_b: Hub | None = hubs.get(raw_hub_b)

        if not hub_a or not hub_b:
            raise ValueError(
                'Connection references unknown hub(s): '
                f'{raw_hub_a!r}, {raw_hub_b!r}'
            )

        if hub_a == hub_b:
            raise ValueError(
                f'Connection cannot link a hub to itself: {hub_a.name!r}'
            )

        _hubs: list[Hub] = [hub_a, hub_b]
        _hubs.sort(key=lambda h: h.name)

        attrs: dict[str, str] = {}
        if attrs_str:
            for pair in attrs_str.split(' '):
                key, sep, value = pair.strip().partition('=')
                if not sep:
                    raise ValueError(
                        f'Malformed attribute {pair.strip()!r} '
                        f'(expected key=value) in line: {line!r}'
                    )
                attrs[key.strip()] = value.strip()

        return cls(
            hubs=_hubs,
            capacity=int(attrs.get('max_link_capacity', 1)),
            blocked=(hub_a or hub_b).metadata.zone == ZoneType.BLOCKED
        )

    def __hash__(self) -> int:
        """Get hash for use in sets and dictionaries.

        Returns:
            Hash value based on connected hub names.
        """
        return self._hash


class Connections:
    """Container managing a collection of connections between hubs.

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
        if connection.hubs in [
                    _connection.hubs for _connection in self._connections
                ]:
            raise ValueError(
                f'Connection between {connection.hubs[0].name!r} and '
                f'{connection.hubs[1].name!r} already exists'
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

    def get_between(self, hub_a: Hub, hub_b: Hub) -> Connection:
        """Get the connection between two specific hubs.

        Args:
            hub_a: First hub.
            hub_b: Second hub.

        Returns:
            The Connection linking both hubs.

        Raises:
            ValueError: If no connection exists between the hubs.
        """
        for connection in self._connections:
            if hub_a in connection.hubs and hub_b in connection.hubs:
                return connection
        raise ValueError(
            f'No connection found between {hub_a.name!r} and {hub_b.name!r}'
        )

    def get_from_hub(self, hub: Hub) -> list[Connection]:
        """Get all connections linked to a specific hub.

        Args:
            hub: The hub to find connections for.

        Returns:
            List of Connection objects that include this hub.
        """
        return [
            connection
            for connection in self._connections
            if hub in connection.hubs
        ]

    def calculate_intersections(self) \
            -> list[tuple[Connection, Connection, Vector2]]:
        """Find all intersection points between connections.

        Returns:
            List of tuples (connection1, connection2, intersection_point)
            for all intersecting connection pairs.
        """
        intersections: list[tuple[Connection, Connection, Vector2]] = []
        for i in range(len(self._connections)):
            for j in range(i + 1, len(self._connections)):
                conn_a = self._connections[i]
                conn_b = self._connections[j]
                intersection = conn_a.intersects_with(conn_b)
                if intersection:
                    intersections.append((conn_a, conn_b, intersection))
        return intersections
