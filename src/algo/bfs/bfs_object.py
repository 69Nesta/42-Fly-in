from abc import ABC


class BFSObject(ABC):
    capacity: int
    load: int

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.load = 0

    def get_remaining_capacity(self) -> int:
        return self.capacity - self.load

    def get_load(self) -> int:
        return self.load

    def is_full(self) -> bool:
        return self.get_remaining_capacity() <= 0

    def add_load(self, load: int) -> None:
        if self.load + load > self.capacity:
            raise ValueError('Load exceeds capacity')
        self.load += load
