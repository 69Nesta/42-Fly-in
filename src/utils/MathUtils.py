from pyray import Vector2
import math


class MathUtils:
    """Utility class for mathematical operations on 2D vectors."""

    @staticmethod
    def get_angle_between_points(p1: Vector2, p2: Vector2) -> float:
        """Calculate angle between two points in degrees.

        Args:
            p1: First point.
            p2: Second point.

        Returns:
            Angle in degrees from p1 to p2.
        """
        return math.atan2(p2.y - p1.y, p2.x - p1.x) * (180 / math.pi)

    @staticmethod
    def get_distance_between_points(p1: Vector2, p2: Vector2) -> float:
        """Calculate Euclidean distance between two points.

        Args:
            p1: First point.
            p2: Second point.

        Returns:
            The distance between the two points.
        """
        return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)

    @staticmethod
    def is_same_2d_pos(p1: Vector2, p2: Vector2) -> bool:
        """Check if two 2D positions are the same.

        Args:
            p1: First position.
            p2: Second position.
        Returns:
            True if positions are the same, False otherwise.
        """
        return p1.x == p2.x and p1.y == p2.y
