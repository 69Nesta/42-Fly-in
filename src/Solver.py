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
        return self.reservations[hub].get(t) is None

    def _connection_is_available(self, conn: Connection, t: int) -> bool:
        for dt in range(t, t + conn.get_travel_time(conn.hubs[0])):
            if self.reservations_connection[conn].get(dt, 0) >= conn.get_capacity():
                return False
        return True
    
    def _apply_reservation(self, drone: Drone, path: list[tuple[Hub, int]]) -> None:
        for i in range(len(path) - 1):
            node, t = path[i]
            next_node, next_t = path[i + 1]

            self.reservations[node][t] = drone
            if node != next_node:
                conn = self.level.connections.get_between(node, next_node)
                for dt in range(t + 1, next_t + 1):
                    self.reservations_connection[conn][dt] = (
                        self.reservations_connection[conn].get(dt, 0) + 1
                    )
    
    def dijkstra_with_reservations(
                self,
                departure_time: int = 0
            ) -> list[tuple[Hub, int]]:
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

            next_t = t + 1

            for conn in self.level.connections.get_from_hub(node):
                neighbor = conn.get_other(node)
                next_t = t + conn.get_travel_time(node)

                if neighbor.is_blocked():
                    continue

                travel_time: int = conn.get_travel_time(node)
                arrival_time: int = t + travel_time
                hub_cost: float = float(travel_time)
                
                if not neighbor.is_priority():
                    hub_cost += 0.5
                
                if self._hub_is_available(neighbor, arrival_time) and self._connection_is_available(conn, t):
                    new_cost = cost + hub_cost
                    if new_cost < dist[(neighbor, next_t)]:
                        dist[(neighbor, next_t)] = new_cost
                        prev[(neighbor, next_t)] = (node, t)
                        heapq.heappush(pq, (new_cost, neighbor, next_t))

            if self._hub_is_available(node, next_t):
                dist[(node, next_t)] = cost + 1
                prev[(node, next_t)] = (node, t)
                heapq.heappush(pq, (cost + 1, node, next_t))

        raise ValueError('No path found from start to end hub. !')

    def _reconstruct_path(self, prev: t_prev) -> list[tuple[Hub, int]]:
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
        self.reservations_connection = defaultdict(dict)

    def plan_all_drones(self) -> None:
        self.reset_reservations()

        for drone in self.level.drones:
            path = self.dijkstra_with_reservations()
            # path = self.reconstruct_path(prev)
            for node, t in path:
                self.logger.log(
                    f'Drone {drone.id} reserved {node.name} at time {t}.'
                )

            for node, timestep in path:
                self.reservations[node][timestep] = drone
            for i in range(len(path) - 1):
                node, t = path[i]
                next_node, next_t = path[i + 1]
                if node != next_node:
                    conn = self.level.connections.get_between(node, next_node)
                    for dt in range(t + 1, next_t + 1):
                        self.reservations_connection[conn][dt] = (
                            self.reservations_connection[conn].get(dt, 0) + 1
                        )
            drone.path = path
