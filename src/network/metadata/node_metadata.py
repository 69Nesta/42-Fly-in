from ..metadata.color_metadata import ColorMetadata
from ...utils import Logger

from pydantic import BaseModel, Field
from typing import Any
from enum import Enum


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


class ZoneCost(Enum):
    """Enumeration of cost values for different node zone types.

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


class NodeMetadata(BaseModel):
    """Metadata and properties associated with a hub.

    Attributes:
        zone: The zone type affecting hub behavior.
        color: Optional color identifier for the hub.
        max_drones: Maximum number of drones allowed in the hub simultaneously.
    """
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: str | None = Field(default=None, pattern=r'^[A-Za-z]+$')
    max_drones: int = Field(default=1, ge=0)

    def get_color(self) -> ColorMetadata:
        """Get the color enumeration value for this hub's metadata.

        Returns:
            The EColor enum value corresponding to the color, or EColor.NONE
            if invalid.
        """
        if ColorMetadata.has_value(self.color):
            return ColorMetadata(self.color)
        else:
            return ColorMetadata.NONE

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
                return ZoneCost.NORMAL.value
            case ZoneType.RESTRICTED:
                return ZoneCost.RESTRICTED.value
            case _:
                raise ValueError(f'Unknown zone type: {self.zone!r}')

    @classmethod
    def from_attrs(
                cls,
                attrs: dict[str, str],
                logger: Logger
            ) -> 'NodeMetadata':
        """Create NodeMetadata from a dictionary of attributes.

        Args:
            attrs: Dictionary with keys like 'zone', 'color', 'max_drones'.

        Returns:
            A new NodeMetadata instance.

        Raises:
            ValueError: If max_drones is not a valid integer.
        """
        data: dict[str, Any] = {}
        allowed_attrs = {'zone', 'color', 'max_drones'}
        for key in attrs:
            if key not in allowed_attrs:
                logger.warning(
                    f'Unknown attribute {key!r} in node metadata, ignoring'
                )

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
