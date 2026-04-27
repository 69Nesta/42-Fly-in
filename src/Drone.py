from dataclasses import dataclass, field
from .Connections import Connection
from pyray import Vector2
from .Hub import Hub


@dataclass(slots=True)
class Drone:
    id: int = field()
    start_point: Vector2 = field()
    end_point: Vector2 = field()

    path: list[tuple[Hub | Connection, int]] = field(default_factory=list)

    def get_position(self) -> Vector2:
        return self.start_point

    def get_step_at_time(self, t: int) -> Hub | Connection | None:
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
        if len(self.path) > 0:
            step, _ = self.path[0]
            if isinstance(step, Hub):
                return Vector2(step.x, step.y)
        return self.get_position()

    def get_end_postion(self) -> Vector2:
        return self.end_point
