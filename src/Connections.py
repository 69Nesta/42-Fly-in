from pydantic import BaseModel, Field, PrivateAttr
from typing import Any, Match, Optional
from .Hub import Hub, ZoneType
from pyray import Vector2
import re


CONNECTION_PATTERN = re.compile(
    r'^connection: (\w+)-(\w+)(?:\s+\[([^\]]*)\])?$'
)


class Connection(BaseModel):
    hubs: list[Hub] = Field()
    capacity: int = Field(default=1, ge=0)
    blocked: bool = Field(default=False)

    _hash: int = PrivateAttr()

    def get_id(self) -> str:
        return f'{self.hubs[0].name}<->{self.hubs[1].name}'

    def get_name(self) -> str:
        return f'{self.hubs[0].name} <-> {self.hubs[1].name}'

    def model_post_init(self, context: Any) -> None:
        self._hash = hash(self.hubs[0].name) ^ hash(self.hubs[1].name)
        return super().model_post_init(context)

    def get_travel_time(self, from_hub: Hub) -> int:
        return self.get_other(from_hub).metadata.get_travel_time()

    def get_weight(self, from_hub: Hub) -> float:
        return self.get_other(from_hub).metadata.get_weight()

    def get_capacity(self) -> int:
        return self.capacity

    def get_other(self, hub: Hub) -> Hub:
        if self.hubs[0] != hub:
            return self.hubs[0]
        else:
            return self.hubs[1]

    def get_from_str(self, id: str) -> Hub:
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
        x = (self.hubs[0].x + self.hubs[1].x) / 2
        y = (self.hubs[0].y + self.hubs[1].y) / 2
        return Vector2(x, y)

    def get_position(self) -> Vector2:
        return self.calculate_middle_point()

    def intersects_with(self, other: 'Connection') -> Optional[Vector2]:
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
        return self._hash


class Connections:
    _connections: list[Connection]

    def __init__(self) -> None:
        self._connections = []

    def add(self, connection: Connection) -> list[Connection]:
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
        return self._connections

    def get_between(self, hub_a: Hub, hub_b: Hub) -> Connection:
        for connection in self._connections:
            if hub_a in connection.hubs and hub_b in connection.hubs:
                return connection
        raise ValueError(
            f'No connection found between {hub_a.name!r} and {hub_b.name!r}'
        )

    def get_from_hub(self, hub: Hub) -> list[Connection]:
        return [
            connection
            for connection in self._connections
            if hub in connection.hubs
        ]

    def calculate_intersections(self) \
            -> list[tuple[Connection, Connection, Vector2]]:
        intersections: list[tuple[Connection, Connection, Vector2]] = []
        for i in range(len(self._connections)):
            for j in range(i + 1, len(self._connections)):
                conn_a = self._connections[i]
                conn_b = self._connections[j]
                intersection = conn_a.intersects_with(conn_b)
                if intersection:
                    intersections.append((conn_a, conn_b, intersection))
        return intersections
