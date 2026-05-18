from pyray import Vector2
import math


class Bezier:
    """Represents a cubic Bézier curve for smooth drone path interpolation.

    Attributes:
        P0: Start point.
        P1: End point.
        C0: First control point.
        C1: Second control point.
    """
    P0: Vector2
    C0: Vector2
    C1: Vector2
    P1: Vector2

    def __init__(
                self,
                P0: Vector2,
                P1: Vector2,
                theta0: float,
                theta1: float,
                strength: float = 0.3
            ) -> None:
        """Initialize a Bézier curve with endpoints and tangent angles.

        Args:
            P0: Starting point.
            P1: Ending point.
            theta0: Tangent angle (in radians) at P0.
            theta1: Tangent angle (in radians) at P1.
            strength: Control point distance factor. Defaults to 0.3.
        """
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
        """Get a point on the Bézier curve at parameter t.

        Args:
            t: Parameter value in range [0, 1] along the curve.

        Returns:
            Vector2 point on the curve at parameter t.
        """
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
        """Get the tangent angle (in radians) on the curve at parameter t.

        Args:
            t: Parameter value in range [0, 1] along the curve.

        Returns:
            Tangent angle in radians.
        """
        dx: float = 3 * (1 - t)**2 * (self.C0.x - self.P0.x) \
            + 6 * (1-t) * t * (self.C1.x - self.C0.x) \
            + 3 * t**2 * (self.P1.x - self.C1.x)

        dy: float = 3 * (1 - t)**2 * (self.C0.y - self.P0.y) \
            + 6 * (1 - t) * t * (self.C1.y - self.C0.y) \
            + 3 * t**2 * (self.P1.y - self.C1.y)

        return math.atan2(dy, dx)

    def bezier_rotation(self, t: float) -> float:
        """Get the tangent angle (in degrees) on the curve at parameter t.

        Args:
            t: Parameter value in range [0, 1] along the curve.

        Returns:
            Tangent angle in degrees.
        """
        return self.bezier_tangent(t) * (180 / math.pi)
