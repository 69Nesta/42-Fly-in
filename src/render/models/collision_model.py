from abc import ABC, abstractmethod
from pyray import Model, Vector3


class CollisionModel(ABC):
    """Abstract base class for 3D models with collision detection.

    Defines the interface for models that can be ray-cast and selected.

    Attributes:
        is_selected: Whether the model is currently selected.
    """
    is_selected: bool

    def __init__(self) -> None:
        """Initialize the collision model."""
        self.is_selected = False

    @abstractmethod
    def get_collision_model(self) -> Model:
        """Get the PyRay Model for collision detection.

        Returns:
            The Model object containing mesh geometry.
        """
        pass

    @abstractmethod
    def get_collision_position(self) -> Vector3:
        """Get the world position of the model.

        Returns:
            Vector3 position.
        """
        pass

    def set_selected(self, selected: bool) -> None:
        """Set the selection state of the model.

        Args:
            selected: Whether the model is selected.
        """
        self.is_selected = selected

    def get_collision_rotation_axis(self) -> Vector3:
        """Get the rotation axis for the model.

        Returns:
            Vector3 axis (default: X-axis).
        """
        return Vector3(1, 0, 0)

    def get_collision_rotation(self) -> float:
        """Get the rotation angle for the model.

        Returns:
            Rotation angle in radians (default: 0).
        """
        return 0.0
