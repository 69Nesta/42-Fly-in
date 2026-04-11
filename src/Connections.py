from pydantic import BaseModel, Field, PrivateAttr
from .Hub import Hub, ZoneType
from typing import Any, Match
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


class Connections(BaseModel):
    _connections: list[Connection] = PrivateAttr([])

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
