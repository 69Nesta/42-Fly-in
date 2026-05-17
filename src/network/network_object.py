from abc import ABC, abstractmethod
from pyray import Vector2


class NetworkObject(ABC):
    @abstractmethod
    def get_capacity(self) -> int:
        """Get the capacity of this network object.

        Returns:
            The capacity of this network object.
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this network object.

        Returns:
            The name of this network object.
        """
        pass

    @abstractmethod
    def get_position(self) -> Vector2:
        """Get the position of this network object.

        Returns:
            The position of this network object as a Vector2.
        """
        pass
