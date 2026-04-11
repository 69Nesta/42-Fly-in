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

    # def __post_init__(self):
    #     self.history.append(Vector2(self.x, self.y))

    # def move_by(self, dx: int, dy: int) -> None:
    #     self.x += dx
    #     self.y += dy
    #     self.history.append(Vector2(self.x, self.y))

    # def move_to(self, x: int, y: int) -> None:
    #     self.x = x
    #     self.y = y
    #     self.history.append(Vector2(self.x, self.y))

    # def move_to_hub(self, hub: Hub) -> None:
    #     self.move_to(hub.x, hub.y)

    def get_position(self) -> Vector2:
        return Vector2(self.x, self.y)

    # def get_history(self) -> list[Vector2]:
    #     return self.history
