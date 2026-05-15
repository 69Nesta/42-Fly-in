from abc import ABC, abstractmethod


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
