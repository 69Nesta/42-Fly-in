from pydantic import BaseModel, Field
from typing import Literal
from enum import Enum
import re


HubType = Literal['hub', 'start_hub', 'end_hub']


class ZoneType(Enum):
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class HubMetadata(BaseModel):
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: str | None = Field(default=None, pattern=r'^[A-Za-z]+$')
    max_drones: int = Field(default=1)


class Hub(BaseModel):
    type: HubType = Field()
    name: str = Field()
    x: int = Field()
    y: int = Field()
    metadata: HubMetadata = Field()

    @classmethod
    def from_str(cls, line: str) -> 'Hub':
        pattern = r'^(\w+):\s+(\w+)\s+(-?\d+)\s+(-?\d+)(?:\s+\[([^\]]*)\])?$'
        match = re.match(pattern, line.strip())
        if not match:
            raise ValueError(f"Invalid hub line: {line!r}")

        hub_type, hub_name, x, y, attrs_str = match.groups()

        attrs = {}
        if attrs_str:
            for pair in attrs_str.split(','):
                key, _, value = pair.strip().partition('=')
                attrs[key.strip()] = value.strip()

        metadata = HubMetadata(
            zone=ZoneType(attrs['zone']) if 'zone' in attrs else ZoneType.NORMAL,
            color=attrs.get('color'),
            max_drones=int(attrs['max_drones']) if 'max_drones' in attrs else 1,
        )

        return cls(
            type=hub_type,
            name=hub_name,
            x=int(x),
            y=int(y),
            metadata=metadata,
        )
