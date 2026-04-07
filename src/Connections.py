from pydantic import BaseModel, Field, PrivateAttr
from .Hub import Hub, ZoneType
from typing import Match
import re


CONNECTION_PATTERN = re.compile(
    r'^connection: (\w+)-(\w+)(?:\s+\[([^\]]*)\])?$'
)


class Connection(BaseModel):
    hubs: list[Hub] = Field()
    capacity: int = Field(default=1, ge=0)
    blocked: bool = Field(default=False)

    _current_load: int = PrivateAttr(0)

    @property
    def current_load(self) -> int:
        return self._current_load

    def get_other(self, hub: Hub) -> Hub:
        if self.hubs[0] != hub:
            return self.hubs[0]
        else:
            return self.hubs[1]

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


class Connections(BaseModel):
    _connections: list[Connection] = PrivateAttr([])

    def add(self, connection: Connection) -> list[Connection]:
        if connection in self._connections:
            raise ValueError(
                f'Connection between {connection.hubs[0].name!r} and '
                f'{connection.hubs[1].name!r} already exists'
            )

        self._connections.append(connection)
        return self._connections

    def get(self) -> list[Connection]:
        return self._connections

    def get_connection(self, hub: Hub) -> list[Connection]:
        return [
            connection
            for connection in self._connections
            if hub in connection.hubs
        ]
