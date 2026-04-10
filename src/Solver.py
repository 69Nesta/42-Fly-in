from collections import defaultdict
from .utils import Logger, Color
from typing import Generator
from .Level import Level
from .Drone import Drone
from .Hub import Hub
import heapq

t_dist = dict[tuple[Hub, int], float]
t_prev = dict[tuple[Hub, int], tuple[Hub, int]]
t_heap_queue = list[tuple[float, Hub, int]]


class Solver():
    level: Level
    logger: Logger
    reservations: dict[Hub, dict[int, Drone]]

    def __init__(self, level: Level) -> None:
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='Solver',
            color=Color.GREEN
        )
        self.logger.log('Initializing solver...')
        self.level.connections.get_from_hub(self.level.start_hub)

        for connection in self.level.connections.all:
            self.logger.log(
                f'Connection: {connection.hubs[0].name} <-> '
                f'{connection.hubs[1].name}'
            )
        self.reset_reservations()

    def dijkstra_with_reservations(
                self,
                departure_time: int = 0
            ) -> tuple[t_dist, t_prev]:
        self.logger.log('Starting to solve...')
        dist: t_dist = defaultdict(lambda: float('inf'))
        prev: t_prev = {}

        pq: t_heap_queue = [
            (0, self.level.start_hub, departure_time)
        ]
        dist[(self.level.start_hub, departure_time)] = 0.0

        while pq:
            cost, node, t = heapq.heappop(pq)
            if node == self.level.end_hub:
                break

            if cost > dist[(node, t)]:
                continue

            next_t = t + 1
            if next_t not in self.reservations[node]:
                if cost < dist[(node, next_t)]:
                    dist[(node, next_t)] = cost
                    prev[(node, next_t)] = (node, t)
                    heapq.heappush(pq, (cost, node, next_t))

            for conn in self.level.connections.get_from_hub(node):
                neighbor = conn.get_other(node)
                next_t = t + conn.get_travel_time(node)

                if neighbor.metadata.is_blocked() or conn.is_full():
                    continue

                travel_time = conn.get_travel_time(node)
                blocked = False
                for dt in range(1, travel_time + 1):
                    if self.reservations[neighbor].get(t + dt) is not None:
                        blocked = True
                        break
                    if self.reservations[node].get(t + dt) is not None:
                        blocked = True
                        break
                if blocked:
                    continue

                new_cost = cost + conn.get_weight(node)
                if new_cost < dist[(neighbor, next_t)]:
                    dist[(neighbor, next_t)] = new_cost
                    prev[(neighbor, next_t)] = (node, t)
                    heapq.heappush(pq, (new_cost, neighbor, next_t))

        self.logger.log('Finished solving.')

        return dist, prev

    def reconstruct_path(self, prev: t_prev) -> list[tuple[Hub, int]]:
        states: Generator[tuple[Hub, int], None, None] = (
            (node, t) for (node, t) in prev if node == self.level.end_hub
        )
        try:
            end_state = min(
                states,
                key=lambda s: s[1]
            )
        except ValueError:
            raise ValueError('No path found from start to end hub.')

        path = []
        state: tuple[Hub, int] | None = end_state
        while state is not None:
            path.append(state)
            state = prev.get(state)

        path.reverse()
        return path

    def reset_reservations(self) -> None:
        self.reservations = defaultdict(dict)

    def plan_all_drones(self) -> None:
        self.reset_reservations()

        for drone in self.level.drones:
            _, prev = self.dijkstra_with_reservations()
            path = self.reconstruct_path(prev)

            for node, timestep in path:
                self.reservations[node][timestep] = drone
            drone.path = path
