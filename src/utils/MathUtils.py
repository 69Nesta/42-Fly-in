from pyray import Vector2
import math


class MathUtils:
    @staticmethod
    def get_angle_between_points(p1: Vector2, p2: Vector2) -> float:
        return math.atan2(p2.y - p1.y, p2.x - p1.x) * (180 / math.pi)

    @staticmethod
    def get_distance_between_points(p1: Vector2, p2: Vector2) -> float:
        return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)
