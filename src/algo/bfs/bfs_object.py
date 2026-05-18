from abc import ABC, abstractmethod


class BFSObject(ABC):
    """Base class for objects with flow capacity in the BFS graph.

    Represents nodes and edges that have limited capacity and track
    the amount of load (flow) applied to them.

    Attributes:
        capacity: Maximum capacity of the object.
        load: Current load (flow) applied to the object.
    """
    capacity: int
    load: int

    def __init__(self, capacity: int) -> None:
        """Initialize a BFS object with a capacity.

        Args:
            capacity: Maximum capacity for flow.
        """
        self.capacity = capacity
        self.load = 0

    def get_remaining_capacity(self) -> int:
        """Get the remaining available capacity.

        Returns:
            Capacity minus current load.
        """
        return self.capacity - self.load

    def get_load(self) -> int:
        """Get the current load applied to this object.

        Returns:
            Current flow load.
        """
        return self.load

    def is_full(self) -> bool:
        """Check if the object has reached capacity.

        Returns:
            True if remaining capacity is zero or negative.
        """
        return self.get_remaining_capacity() <= 0

    def add_load(self, load: int) -> None:
        """Add load (flow) to this object.

        Args:
            load: Amount of load to add.

        Raises:
            ValueError: If total load would exceed capacity.
        """
        if self.load + load > self.capacity:
            raise ValueError('Load exceeds capacity')
        self.load += load

    @abstractmethod
    def get_name(self) -> str:
        """Get a string name for this object.

        Returns:
            A string identifier for the object.
        """
        pass
