from collections import defaultdict, deque
from .Connections import Connection
from .utils import Logger, Color
from typing import Generator
from .Level import Level
from .Drone import Drone
from .Hub import Hub
import heapq

t_dist = dict[tuple[Hub, int], float]
t_prev = dict[tuple[Hub, int], tuple[Hub, int]]
t_heap_queue = list[tuple[float, Hub, int]]
t_path = list[tuple[Hub | Connection, int]]


class Solver():
    __slots__: list[str] = [
        'level', 'logger', 'reservations', 'reservations_connection'
    ]

    level: Level
    logger: Logger
    reservations: dict[Hub, dict[int, int]]
    reservations_connection: dict[Connection, dict[int, int]]

    def __init__(self, level: Level) -> None:
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='Solver',
            color=Color.GREEN
        )
        self.logger.log('Initializing solver...')

        self.reset_reservations()

    def _hub_is_available(self, hub: Hub, t: int) -> bool:
        return (
            self.reservations[hub].get(t, 0) < hub.metadata.max_drones
        )

    def _connection_is_available(self, conn: Connection, t: int) -> bool:
        return (
            self.reservations_connection[conn].get(t, 0) < conn.get_capacity()
        )

    def _apply_reservation(self, drone: Drone, path: t_path) -> None:
        for i in range(len(path) - 1):
            node, t = path[i]
            next_node, _ = path[i + 1]
            if isinstance(node, Hub):
                self.reservations[node].update({
                    t: self.reservations[node].get(t, 0) + 1
                })
            if (isinstance(node, Hub)
               and isinstance(next_node, Hub)
               and node != next_node):
                conn = self.level.connections.get_between(node, next_node)
                self.reservations_connection[conn][t + 1] = (
                    self.reservations_connection[conn].get(t + 1, 0) + 1
                )

            if isinstance(node, Connection):
                self.reservations_connection[node][t] = (
                    self.reservations_connection[node].get(t, 0) + 1
                )

        last_node, last_t = path[-1]
        if isinstance(last_node, Hub):
            self.reservations[last_node].update({
                last_t: self.reservations[last_node].get(last_t, 0) + 1
            })

    def _static_path_exists(self) -> bool:
        seen: set[Hub] = {self.level.start_hub}
        queue: deque[Hub] = deque([self.level.start_hub])

        while queue:
            hub = queue.popleft()
            if hub.is_end():
                return True

            for conn in self.level.connections.get_from_hub(hub):
                if conn.capacity < 1:
                    continue
                other = conn.get_other(hub)
                if other.is_blocked() or other.metadata.max_drones < 1:
                    continue
                if other not in seen:
                    seen.add(other)
                    queue.append(other)

        return False

    def dijkstra_with_reservations(self, departure_time: int = 0) -> t_path:
        dist: t_dist = defaultdict(lambda: float('inf'))
        prev: t_prev = {}
        visited: set[tuple[Hub, int]] = set()

        pq: t_heap_queue = [
            (0, self.level.start_hub, departure_time)
        ]
        dist[(self.level.start_hub, departure_time)] = 0.0

        while pq:
            cost, node, t = heapq.heappop(pq)
            if node == self.level.end_hub:
                return self._reconstruct_path(prev)

            if (node, t) in visited:
                continue
            visited.add((node, t))

            if cost > dist[(node, t)]:
                continue

            wait_t: int = t + 1
            for conn in self.level.connections.get_from_hub(node):
                neighbor: Hub = conn.get_other(node)
                travel_time: int = conn.get_travel_time(node)
                arrival_time: int = t + travel_time

                if neighbor.is_blocked():
                    continue

                hub_cost: float = float(travel_time)
                if not neighbor.is_priority():
                    hub_cost += 0.5

                if (self._hub_is_available(neighbor, arrival_time)
                   and self._connection_is_available(conn, arrival_time)):

                    new_cost = cost + hub_cost
                    if new_cost < dist[(neighbor, arrival_time)]:
                        dist[(neighbor, arrival_time)] = new_cost
                        prev[(neighbor, arrival_time)] = (node, t)
                        heapq.heappush(pq, (new_cost, neighbor, arrival_time))

            new_wait_cost: float = cost + 1
            if new_wait_cost < dist[(node, wait_t)]:
                dist[(node, wait_t)] = new_wait_cost
                prev[(node, wait_t)] = (node, t)
                heapq.heappush(pq, (new_wait_cost, node, wait_t))

        raise ValueError('No path found from start to end hub. !')

    def _reconstruct_path(self, prev: t_prev) -> t_path:
        states: Generator[tuple[Hub, int], None, None] = (
            (node, t) for (node, t) in prev if node == self.level.end_hub
        )
        try:
            end_state = heapq.nsmallest(1, states, key=lambda s: s[1])[0]
        except ValueError:
            raise ValueError('No path found from start to end hub.')

        path: t_path = []
        state: tuple[Hub, int] | None = end_state
        while state is not None:
            path.append(state)
            new_state: tuple[Hub, int] | None = prev.get(state)
            if new_state is not None and new_state[1] + 1 != state[1]:
                path.append((
                    self.level.connections.get_between(state[0], new_state[0]),
                    state[1] - 1
                ))
            state = new_state

        path.reverse()
        return path

    def reset_reservations(self) -> None:
        self.reservations = defaultdict(dict)
        self.reservations_connection = defaultdict(dict)

    def plan_all_drones(self) -> None:
        self.reset_reservations()

        if not self._static_path_exists():
            raise ValueError('No path found from start to end hub.')

        self.logger.log('Planning paths for all drones...')
        for drone in self.level.drones:
            path: t_path = self.dijkstra_with_reservations(departure_time=0)
            drone.path = path
            self._apply_reservation(drone, path)
            self.logger.log(f'Planned path for drone {drone.get_name()}')

        self.logger.log('All drones planned successfully.')
        self.level.update_number_of_steps()
        self.level.reservations = self.reservations
        self.level.reservations_connection = self.reservations_connection
