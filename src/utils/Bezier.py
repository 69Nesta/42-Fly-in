from pyray import Vector2
import math


class Bezier:
    P0: Vector2
    C0: Vector2
    C1: Vector2
    P1: Vector2

    def __init__(
                self,
                P0: Vector2, P1: Vector2,
                theta0: float, theta1: float,
                strength: float = 0.3
            ) -> None:
        self.P0 = P0
        self.P1 = P1
        dx: float = P1.x - P0.x
        dy: float = P1.y - P0.y
        dist: float = math.hypot(dx, dy)

        d: float = dist * strength

        C0 = Vector2(
            P0.x + math.cos(theta0) * d,
            P0.y + math.sin(theta0) * d
        )

        C1 = Vector2(
            P1.x - math.cos(theta1) * d,
            P1.y - math.sin(theta1) * d
        )

        self.C0 = C0
        self.C1 = C1

    def bezier_point(self, t: float) -> Vector2:
        x: float = (1 - t)**3 * self.P0.x \
            + 3 * (1 - t)**2 * t * self.C0.x \
            + 3 * (1 - t) * t**2 * self.C1.x \
            + t**3 * self.P1.x

        y: float = (1 - t)**3 * self.P0.y \
            + 3 * (1 - t)**2 * t * self.C0.y \
            + 3 * (1 - t) * t**2 * self.C1.y \
            + t**3 * self.P1.y

        return Vector2(x, y)

    def bezier_tangent(self, t: float) -> float:
        dx: float = 3 * (1 - t)**2 * (self.C0.x - self.P0.x) \
            + 6 * (1-t) * t * (self.C1.x - self.C0.x) \
            + 3 * t**2 * (self.P1.x - self.C1.x)

        dy: float = 3 * (1 - t)**2 * (self.C0.y - self.P0.y) \
            + 6 * (1 - t) * t * (self.C1.y - self.C0.y) \
            + 3 * t**2 * (self.P1.y - self.C1.y)

        return math.atan2(dy, dx)

    def bezier_rotation(self, t: float) -> float:
        return self.bezier_tangent(t) * (180 / math.pi)
