from ...utils import Logger
from pydantic import BaseModel, Field


class ConnectionMetadata(BaseModel):
    """Metadata for a connection between two nodes.

    Attributes:
        capacity: Maximum number of drones allowed on the connection.
        blocked: Whether the connection is impassable.
    """
    capacity: int = Field(default=1, ge=0)
    blocked: bool = Field(default=False)

    @classmethod
    def from_str(
                cls,
                s: str,
                line: str,
                logger: Logger
            ) -> 'ConnectionMetadata':
        """Create ConnectionMetadata from a string of attributes.

        Args:
            s: String containing space-separated key=value pairs.
            line: The original parsed line (for error messages).
            logger: Logger instance for warnings.

        Returns:
            A new ConnectionMetadata instance.

        Raises:
            ValueError: If attribute format is invalid.
        """
        attrs: dict[str, str] = {}
        allowed_keys = {'max_link_capacity', 'blocked'}

        if s:
            for pair in s.split(' '):
                key, sep, value = pair.strip().partition('=')
                if key not in allowed_keys:
                    logger.warning(
                        f'Unknown attribute {key!r} in line: {line!r}. '
                    )
                if not sep:
                    raise ValueError(
                        f'Malformed attribute {pair.strip()!r} '
                        f'(expected key=value) in line: {line!r}'
                    )
                attrs[key.strip()] = value.strip()

        return cls(
            capacity=int(attrs.get('max_link_capacity', 1)),
            blocked=attrs.get('blocked', 'false').lower() == 'true'
        )
