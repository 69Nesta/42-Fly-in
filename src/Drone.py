from .algo.time_graph import Node, ConnectionNode
from .network import Node as NetworkNode

from dataclasses import dataclass, field
from pyray import Vector2


@dataclass(slots=True)
class Drone:
    """Represents a delivery drone with start/end points and a planned path.

    Attributes:
        id: Unique identifier for the drone.
        start_point: Starting position of the drone.
        end_point: Destination position of the drone.
        path: List of (hub or connection, time) tuples representing the
        planned route.
    """
    id: int = field()
    start_point: Vector2 = field()
    end_point: Vector2 = field()

    path: list[Node] = field(default_factory=list)
    _cached_positions: dict[int, Vector2] = field(default_factory=dict)

    def get_id(self) -> int:
        """Get the drone's unique identifier.

        Returns:
            The drone's ID.
        """
        return self.id

    def get_name(self) -> str:
        """Get the drone's display name.

        Returns:
            The drone's name (e.g., 'D1' for drone with id 0).
        """
        return f'D{self.id + 1}'

    def get_position(self) -> Vector2:
        """Get the drone's starting position.

        Returns:
            The starting position as a Vector2.
        """
        return self.start_point

    def get_step_at_time(self, t: int) -> Node | None:
        """Get the path step (hub or connection) at a specific time.

        Args:
            t: The time step.

        Returns:
            The hub or connection at time t, or None if not available.
        """
        if t >= len(self.path) or t < 0:
            return None

        node: Node | None = self.path[t]
        if not node:
            return None
        next_node: Node | None = (
            self.path[t + 1] if t + 1 < len(self.path) else None
        )
        if not next_node:
            return node
        if next_node.object.is_start() and self.path[t].object.is_start():
            return None

        return node

    def get_position_at_step(self, t: int) -> Vector2:
        """Get the drone's position at a specific time step.

        Args:
            t: The time step.

        Returns:
            The drone's position at time t as a Vector2.
        """
        if t in self._cached_positions:
            return self._cached_positions[t]

        node: Node | None = self.get_step_at_time(t)
        if not node and t >= len(self.path):
            return self.get_end_postion()
        elif not node:
            return self.get_position()

        position: Vector2
        if isinstance(node, ConnectionNode):
            position = node.get_network_connection().get_position()
        else:
            position = Vector2(node.object.x, node.object.y)

        return self._cached_positions.setdefault(
            t,
            position
        )

    def get_first_position(self) -> Vector2:
        """Get the drone's first position in its planned path.

        Returns:
            The position of the first step in the path, or starting position
            if path is empty.
        """
        if len(self.path) > 0:
            return self.path[0].object.get_position()
        return self.get_position()

    def get_end_postion(self) -> Vector2:
        """Get the drone's destination/end position.

        Returns:
            The destination position as a Vector2.
        """
        return self.end_point
