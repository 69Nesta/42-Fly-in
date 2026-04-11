from .Connections import Connection
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
t_path = list[tuple[Hub | Connection, int]]


class Solver():
    level: Level
    logger: Logger
    reservations: dict[Hub, dict[int, Drone]]
    reservations_connection: dict[Connection, dict[int, int]]

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

    def _hub_is_available(self, hub: Hub, t: int) -> bool:
        restriced_cond = True
        if hub.is_restricted():
            restriced_cond = self.reservations[hub].get(t - 1) is None
        return self.reservations[hub].get(t) is None and restriced_cond

    def _connection_is_available(self, conn: Connection, t: int) -> bool:
        for dt in range(t, t + conn.get_travel_time(conn.hubs[0])):
            if (self.reservations_connection[conn].get(dt, 0) >=
                    conn.get_capacity()):
                return False
        return True

    def _apply_reservation(self, drone: Drone, path: t_path) -> None:
        for i in range(len(path) - 1):
            node, t = path[i]
            next_node, _ = path[i + 1]

            if not isinstance(node, Hub) or not isinstance(next_node, Hub):
                continue
            self.reservations[node][t] = drone
            if node != next_node:
                conn = self.level.connections.get_between(node, next_node)
                for dt in range(t + 1, t + conn.get_travel_time(next_node)):
                    self.reservations_connection[conn][dt] = (
                        self.reservations_connection[conn].get(dt, 0) + 1
                    )

    def dijkstra_with_reservations(self, departure_time: int = 0) -> t_path:
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
                self.logger.log('Finished solving.')
                return self._reconstruct_path(prev)

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
                   and self._connection_is_available(conn, t)):
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
            end_state = min(
                states,
                key=lambda s: s[1]
            )
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
            # state = prev.get(state)
            state = new_state

        path.reverse()
        return path

    def reset_reservations(self) -> None:
        self.reservations = defaultdict(dict)
        self.reservations_connection = defaultdict(dict)

    def plan_all_drones(self) -> None:
        self.reset_reservations()

        for drone in self.level.drones:
            path: t_path = self.dijkstra_with_reservations(departure_time=0)
            drone.path = path

            self._apply_reservation(drone, path)
            for node, t in path:
                if isinstance(node, Hub):
                    self.logger.log(
                        f'Drone {drone.id} reserved {node.name} at time {t}'
                    )
                if isinstance(node, Connection):
                    self.logger.log(
                        f'Drone {drone.id} reserved connection between '
                        f'{node.hubs[0].name} and {node.hubs[1].name} '
                        f'at time {t}'
                    )

        self.level.update_number_of_steps()
