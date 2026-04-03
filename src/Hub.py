from pydantic import BaseModel, Field
from typing import Literal
from enum import Enum
import re

HubType = Literal['hub', 'start_hub', 'end_hub']

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

    @classmethod
    def from_attrs(cls, attrs: dict[str, str]) -> 'HubMetadata':
        data: dict = {}

        if 'zone' in attrs:
            data['zone'] = attrs['zone']
        if 'color' in attrs:
            data['color'] = attrs['color']
        if 'max_drones' in attrs:
            try:
                data['max_drones'] = int(attrs['max_drones'])
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
            type=hub_type,
            name=hub_name,
            x=int(x),
            y=int(y),
            metadata=metadata,
        )
