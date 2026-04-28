from dataclasses import dataclass, field
from .Connections import Connection
from pyray import Vector2
from .Hub import Hub


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

    path: list[tuple[Hub | Connection, int]] = field(default_factory=list)

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

    def get_step_at_time(self, t: int) -> Hub | Connection | None:
        """Get the path step (hub or connection) at a specific time.

        Args:
            t: The time step.

        Returns:
            The hub or connection at time t, or None if not available.
        """
        for idx, (step, step_t) in enumerate(self.path):
            if step_t == t:
                next_step: tuple[Hub | Connection, int] | None = (
                    self.path[idx + 1] if idx + 1 < len(self.path) else None
                )
                if (next_step and isinstance(step, Hub)
                   and isinstance(next_step[0], Hub)
                   and next_step[0].is_start()):
                    return None
                return step
        return None

    def get_position_at_step(self, t: int) -> Vector2:
        """Get the drone's position at a specific time step.

        Args:
            t: The time step.

        Returns:
            The drone's position at time t as a Vector2.
        """
        for idx, (step, step_t) in enumerate(self.path):
            if step_t == t:
                next_step: tuple[Hub | Connection, int] | None = (
                    self.path[idx + 1] if idx + 1 < len(self.path) else None
                )
                if (next_step and isinstance(step, Hub)
                   and isinstance(next_step[0], Hub)
                   and next_step[0].is_start()):
                    return self.get_position()
                if isinstance(step, Hub) or isinstance(step, Connection):
                    return step.get_position()
                break
        return self.get_end_postion()

    def get_first_position(self) -> Vector2:
        """Get the drone's first position in its planned path.

        Returns:
            The position of the first step in the path, or starting position
            if path is empty.
        """
        if len(self.path) > 0:
            step, _ = self.path[0]
            if isinstance(step, Hub):
                return Vector2(step.x, step.y)
        return self.get_position()

    def get_end_postion(self) -> Vector2:
        """Get the drone's destination/end position.

        Returns:
            The destination position as a Vector2.
        """
        return self.end_point
