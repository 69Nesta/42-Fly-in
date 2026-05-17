from pydantic import BaseModel, Field
from typing import cast, Any
from .Enums import EColor
from pyray import Vector2
from enum import Enum
import re


class HubType(Enum):
    """Enumeration of hub types in the network.

    Attributes:
        HUB: Regular hub node.
        START_HUB: Starting hub for drone routes.
        END_HUB: Destination hub for drone routes.
    """
    HUB = 'hub'
    START_HUB = 'start_hub'
    END_HUB = 'end_hub'


HUB_PATTERN = re.compile(
    r'^(\w+):\s+(\w+)\s+(-?\d+)\s+(-?\d+)(?:\s+\[([^\]]*)\])?$'
)


class ZoneType(Enum):
    """Enumeration of zone types that affect hub properties.

    Attributes:
        NORMAL: Standard zone with normal weight and travel time.
        BLOCKED: Impassable zone with infinite weight.
        RESTRICTED: Zone with higher weight and longer travel time.
        PRIORITY: Zone with lower weight and priority access.
    """
    NORMAL = 'normal'
    BLOCKED = 'blocked'
    RESTRICTED = 'restricted'
    PRIORITY = 'priority'


class ENodeCost(Enum):
    """Enumeration of cost values for different hub zone types.

    Attributes:
        NORMAL: Cost for normal zones.
        BLOCKED: Cost for blocked zones.
        RESTRICTED: Cost for restricted zones.
        PRIORITY: Cost for priority zones (lower than normal).
    """
    NORMAL = 1
    BLOCKED = 1
    RESTRICTED = 2
    PRIORITY = 1


class HubMetadata(BaseModel):
    """Metadata and properties associated with a hub.

    Attributes:
        zone: The zone type affecting hub behavior.
        color: Optional color identifier for the hub.
        max_drones: Maximum number of drones allowed in the hub simultaneously.
    """
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: str | None = Field(default=None, pattern=r'^[A-Za-z]+$')
    max_drones: int = Field(default=1, ge=0)

    def get_color(self) -> EColor:
        """Get the color enumeration value for this hub's metadata.

        Returns:
            The EColor enum value corresponding to the color, or EColor.NONE
            if invalid.
        """
        if EColor.has_value(self.color):
            return EColor(self.color)
        else:
            return EColor.NONE

    def get_travel_time(self) -> int:
        """Get the travel time to traverse this hub based on its zone type.

        Returns:
            Travel time in steps: 1 (normal, blocked, priority) or 2
            (restricted).

        Raises:
            ValueError: If zone type is unknown.
        """
        match self.zone:
            case ZoneType.NORMAL | ZoneType.BLOCKED | ZoneType.PRIORITY:
                return ENodeCost.NORMAL.value
            case ZoneType.RESTRICTED:
                return ENodeCost.RESTRICTED.value
            case _:
                raise ValueError(f'Unknown zone type: {self.zone!r}')

    @classmethod
    def from_attrs(cls, attrs: dict[str, str]) -> 'HubMetadata':
        """Create HubMetadata from a dictionary of attributes.

        Args:
            attrs: Dictionary with keys like 'zone', 'color', 'max_drones'.

        Returns:
            A new HubMetadata instance.

        Raises:
            ValueError: If max_drones is not a valid integer.
        """
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
    """Represents a hub (network node) in the delivery system.

    Attributes:
        type: The type of hub (regular, start, or end).
        name: Unique identifier/name for the hub.
        x: X coordinate of the hub position.
        y: Y coordinate of the hub position.
        metadata: Hub metadata including zone type, color, and capacity.
    """
    type: HubType = Field()
    name: str = Field()
    x: int = Field()
    y: int = Field()
    metadata: HubMetadata = Field(default_factory=HubMetadata)

    @classmethod
    def from_str(cls, line: str) -> 'Hub':
        """Parse a hub from a formatted string line.

        Args:
            line: String in format 'name: type x y [key=value ...]'.

        Returns:
            A new Hub instance.

        Raises:
            ValueError: If line format is invalid or attributes are malformed.
        """
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
        """Check if the hub is in a blocked zone.

        Returns:
            True if hub is blocked, False otherwise.
        """
        return self.metadata.zone == ZoneType.BLOCKED

    def is_priority(self) -> bool:
        """Check if the hub is in a priority zone.

        Returns:
            True if hub is priority, False otherwise.
        """
        return self.metadata.zone == ZoneType.PRIORITY

    def is_restricted(self) -> bool:
        """Check if the hub is in a restricted zone.

        Returns:
            True if hub is restricted, False otherwise.
        """
        return self.metadata.zone == ZoneType.RESTRICTED

    def is_start(self) -> bool:
        """Check if this is a starting hub.

        Returns:
            True if hub type is START_HUB, False otherwise.
        """
        return self.type == HubType.START_HUB

    def is_end(self) -> bool:
        """Check if this is an ending hub.

        Returns:
            True if hub type is END_HUB, False otherwise.
        """
        return self.type == HubType.END_HUB

    def get_position(self) -> Vector2:
        """Get the hub's position in 2D space.

        Returns:
            The hub's coordinates as a Vector2.
        """
        return Vector2(self.x, self.y)

    def get_name(self) -> str:
        """Get the hub's name/identifier.

        Returns:
            The hub's name.
        """
        return self.name

    def __lt__(self, other: 'Hub') -> bool:
        """Check if this hub's name is lexicographically less than another.

        Args:
            other: Another Hub instance.

        Returns:
            True if self.name < other.name, False otherwise.
        """
        return self.name < other.name

    def __eq__(self, other: object) -> bool:
        """Check equality based on hub name.

        Args:
            other: Another object.

        Returns:
            True if other is a Hub with the same name, False otherwise.
        """
        return isinstance(other, Hub) and self.name == other.name

    def __hash__(self) -> int:
        """Get hash based on hub name for use in sets and dicts.

        Returns:
            Hash value of the hub's name.
        """
        return hash(self.name)
