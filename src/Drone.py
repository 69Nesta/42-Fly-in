from dataclasses import dataclass, field
from .Connections import Connection
from pyray import Vector2
from .Hub import Hub


@dataclass
class Drone:
    id: int = field()
    x: int = field()
    y: int = field()

    path: list[tuple[Hub | Connection, int]] = field(default_factory=list)

    def get_position(self) -> Vector2:
        return Vector2(self.x, self.y)

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
