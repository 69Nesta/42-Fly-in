from pydantic import BaseModel, Field
from typing import cast, Any
from .Enums import EColor
from pyray import Vector2
from enum import Enum
import re


class HubType(Enum):
    HUB = 'hub'
    START_HUB = 'start_hub'
    END_HUB = 'end_hub'


HUB_PATTERN = re.compile(
    r'^(\w+):\s+(\w+)\s+(-?\d+)\s+(-?\d+)(?:\s+\[([^\]]*)\])?$'
)


class ZoneType(Enum):
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class HubMetadata(BaseModel):
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: str | None = Field(default=None, pattern=r'^[A-Za-z]+$')
    max_drones: int = Field(default=1, ge=0)

    def get_color(self) -> EColor:
        if EColor.has_value(self.color):
            return EColor(self.color)
        else:
            return EColor.NONE

    def get_weight(self) -> float:
        if self.zone == ZoneType.NORMAL:
            return 1.0
        elif self.zone == ZoneType.BLOCKED:
            return float('inf')
        elif self.zone == ZoneType.RESTRICTED:
            return 2.0
        elif self.zone == ZoneType.PRIORITY:
            return 0.5
        else:
            raise ValueError(f'Unknown zone type: {self.zone!r}')

    def get_travel_time(self) -> int:
        if self.zone == ZoneType.NORMAL:
            return 1
        elif self.zone == ZoneType.BLOCKED:
            return 1
        elif self.zone == ZoneType.RESTRICTED:
            return 2
        elif self.zone == ZoneType.PRIORITY:
            return 1
        else:
            raise ValueError(f'Unknown zone type: {self.zone!r}')

    @classmethod
    def from_attrs(cls, attrs: dict[str, str]) -> 'HubMetadata':
        data: dict[str, Any] = {}

        if 'zone' in attrs:
            data['zone'] = attrs['zone']
        if 'color' in attrs:
            data['color'] = attrs['color']
        if 'max_drones' in attrs:
            try:
                data['max_drones'] = str(int(attrs['max_drones']))
            except ValueError:
                raise ValueError(
                    'max_drones must be an integer, got '
                    f'{attrs["max_drones"]!r}'
                )

        return cls(**data)


class Hub(BaseModel):
    type: HubType = Field()
    name: str = Field()
    x: int = Field()
    y: int = Field()
    metadata: HubMetadata = Field(default_factory=HubMetadata)

    @classmethod
    def from_str(cls, line: str) -> 'Hub':
        match = HUB_PATTERN.match(line.strip())
        if not match:
            raise ValueError(f'Invalid hub line format: {line!r}')

        hub_type, hub_name, x, y, attrs_str = match.groups()

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

        metadata = HubMetadata.from_attrs(attrs)

        return cls(
            type=cast(HubType, hub_type),
            name=hub_name,
            x=int(x),
            y=int(y),
            metadata=metadata,
        )

    def is_blocked(self) -> bool:
        return self.metadata.zone == ZoneType.BLOCKED

    def is_priority(self) -> bool:
        return self.metadata.zone == ZoneType.PRIORITY

    def is_restricted(self) -> bool:
        return self.metadata.zone == ZoneType.RESTRICTED

    def is_start(self) -> bool:
        return self.type == HubType.START_HUB

    def is_end(self) -> bool:
        return self.type == HubType.END_HUB

    def get_position(self) -> Vector2:
        return Vector2(self.x, self.y)

    def get_name(self) -> str:
        return self.name

    def __lt__(self, other: 'Hub') -> bool:
        return self.name < other.name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Hub) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)
