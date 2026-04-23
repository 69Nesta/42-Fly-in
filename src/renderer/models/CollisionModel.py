from abc import ABC, abstractmethod
from pyray import Model, Vector3


class CollisionModel(ABC):
    is_selected: bool

    def __init__(self) -> None:
        self.is_selected = False

    @abstractmethod
    def get_collision_model(self) -> Model:
        pass

    @abstractmethod
    def get_collision_position(self) -> Vector3:
        pass

    def set_selected(self, selected: bool) -> None:
        self.is_selected = selected

    def get_collision_rotation_axis(self) -> Vector3:
        return Vector3(1, 0, 0)

    def get_collision_rotation(self) -> float:
        return 0.0
