from collections import defaultdict, deque
from .Connections import Connection
from .utils import Logger, Color
from typing import Generator
from .Level import Level
from .Drone import Drone
from .Hub import Hub
import heapq


t_dist = dict[tuple[Hub, int], tuple[float, int, int]]
t_prev = dict[tuple[Hub, tuple[int, int, int]], tuple[Hub, tuple[int, int, int]]]
t_heap_queue = list[tuple[int, int, int, Hub]]
t_path = list[tuple[Hub | Connection, int]]


class Solver():
    """Solves drone routing problems using Dijkstra's algorithm with
    reservations.

    Manages path planning for multiple drones with capacity constraints on hubs
    and connections, and tracks reservations to avoid conflicts.

    Attributes:
        level: The Level instance containing network and drone information.
        logger: Logger instance for debug/info messages.
        reservations: Tracks hub usage (hub -> time -> drone count).
        reservations_connection: Tracks connection usage (connection -> time
        -> drone count).
    """
    __slots__: list[str] = [
        'level', 'logger', 'reservations', 'reservations_connection'
    ]

    level: Level
    logger: Logger
    reservations: dict[Hub, dict[int, int]]
    reservations_connection: dict[Connection, dict[int, int]]

    def __init__(self, level: Level) -> None:
        """Initialize the solver with a level.

        Args:
            level: The Level instance to solve for.
        """
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='Solver',
            color=Color.GREEN
        )
        self.logger.log('Initializing solver...')

        self.reset_reservations()

    def _hub_is_available(self, hub: Hub, t: int) -> bool:
        """Check if a hub has capacity at a specific time.

        Args:
            hub: The hub to check.
            t: The time step.

        Returns:
            True if hub has available capacity at time t, False otherwise.
        """
        return (
            self.reservations[hub].get(t, 0) < hub.metadata.max_drones
        )

    def _connection_is_available(self, conn: Connection, t: int) -> bool:
        """Check if a connection has capacity at a specific time.

        Args:
            conn: The connection to check.
            t: The time step.

        Returns:
            True if connection has available capacity at time t, False
            otherwise.
        """
        return (
            self.reservations_connection[conn].get(t, 0) < conn.get_capacity()
        )

    def _apply_reservation(self, drone: Drone, path: t_path) -> None:
        """Record a drone's path in the reservations tracking.

        Updates both hub and connection reservations for each step of the path.

        Args:
            drone: The drone being assigned the path.
            path: The path (list of hub/connection, time tuples).
        """
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
                arrival: int = t + conn.get_travel_time(next_node)
                self.reservations_connection[conn][arrival] = (
                    self.reservations_connection[conn].get(arrival, 0) + 1
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
        """Check if any valid path exists from start to end hub.

        Uses BFS to verify connectivity, ignoring time and reservations.

        Returns:
            True if a path exists, False otherwise.
        """
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
        """Find shortest path from start to end hub considering reservations.

        Uses Dijkstra's algorithm with dynamic availability constraints based
        on existing drone reservations and capacity limits.

        Args:
            departure_time: The time step when the drone departs. Defaults to 0

        Returns:
            Path as list of (hub/connection, time) tuples.

        Raises:
            ValueError: If no valid path exists.
        """
        dist: t_dist = defaultdict(lambda: (float('inf'), 0, 0))
        prev: t_prev = {}
        visited: set[tuple[Hub, tuple[int, int, int]]] = set()

        pq: t_heap_queue = [
            (departure_time, 0, 0, self.level.start_hub)
        ]
        dist[(self.level.start_hub, departure_time)] = (0.0, 0, 0)

        while pq:
            t, priority_count, moves, node = heapq.heappop(pq)
            if node == self.level.end_hub:
                return self._reconstruct_path(prev)

            if (node, (t, priority_count, moves)) in visited:
                continue
            visited.add((node, (t, priority_count, moves)))

            if (t, priority_count, moves) > dist[(node, t)]:
                continue

            wait_t: int = t + 1
            for conn in self.level.connections.get_from_hub(node):
                neighbor: Hub = conn.get_other(node)
                travel_time: int = conn.get_travel_time(node)
                arrival_time: int = t + travel_time
                new_priority_count: int = priority_count

                if neighbor.is_blocked():
                    continue

                if neighbor.is_priority():
                    new_priority_count -= 1

                if (self._hub_is_available(neighbor, arrival_time)
                   and self._connection_is_available(conn, arrival_time)):

                    new_dist: tuple[int, int, int] = (
                        arrival_time,
                        new_priority_count,
                        moves + 1
                    )
                    old_dist: tuple[int, int, int] = (
                        t,
                        priority_count,
                        moves
                    )
                    if new_dist < dist[(neighbor, arrival_time)]:
                        dist[(neighbor, arrival_time)] = new_dist
                        prev[(neighbor, new_dist)] = (node, old_dist)
                        heapq.heappush(
                            pq,
                            (arrival_time, new_priority_count, moves + 1, neighbor)
                        )

            new_dist = (wait_t, priority_count, moves)
            if new_dist < dist[(node, wait_t)]:
                dist[(node, wait_t)] = new_dist
                prev[(node, new_dist)] = (node, (t, priority_count, moves))
                heapq.heappush(pq, (wait_t, priority_count, moves, node))

        raise ValueError('No path found from start to end hub. !')

    def _reconstruct_path(self, prev: t_prev) -> t_path:
        """Reconstruct the path from start to end hub from previous pointers.

        Args:
            prev: Dictionary mapping (hub, time) states to their predecessors.

        Returns:
            Path as list of (hub/connection, time) tuples.

        Raises:
            ValueError: If no complete path exists in prev.
        """
        states: Generator[tuple[Hub, tuple[int, int, int]], None, None] = (
            (node, t) for (node, t) in prev if node == self.level.end_hub
        )
        try:
            end_state = heapq.nsmallest(1, states, key=lambda s: s[1])
        except ValueError:
            raise ValueError('No path found from start to end hub.')
        if not end_state:
            raise ValueError('No path found from start to end hub.')

        path: t_path = []
        state: tuple[Hub, tuple[int, int, int]] | None = end_state[0]
        while state is not None:
            node: Hub = state[0]
            time: int = state[1][0]

            path.append((node, time))
            new_state: tuple[Hub, tuple[int, int, int]] | None = prev.get(state)
            if new_state is not None and new_state[1][0] + 1 != time:
                path.append((
                    self.level.connections.get_between(node, new_state[0]),
                    time - 1
                ))
            state = new_state

        path.reverse()
        return path

    def reset_reservations(self) -> None:
        """Clear all hub and connection reservations.

        Resets the reservation dictionaries to empty state.
        """
        self.reservations = defaultdict(dict)
        self.reservations_connection = defaultdict(dict)

    def plan_all_drones(self) -> None:
        """Plan paths for all drones in the level.

        Finds valid paths for each drone using Dijkstra's algorithm,
        respecting capacity constraints and previously assigned paths.

        Raises:
            ValueError: If no valid path exists from start to end hub.
        """
        self.reset_reservations()

        if not self._static_path_exists():
            raise ValueError('No path found from start to end hub.')

        self.logger.log('Planning paths for all drones...')
        for drone in self.level.drones:
            path: t_path = self.dijkstra_with_reservations(departure_time=0)
            drone.path = path
            self._apply_reservation(drone, path)
            self.logger.log(f'Planned path for drone {drone.get_name()}')
            self.logger.log(
                'Path: ' +
                str([
                    node.get_name()
                    for node, _ in path
                ])
            )

        self.logger.log('All drones planned successfully.')
        self.level.update_number_of_steps()
        self.level.update_drone_reached_end()
        self.print_stats()
        self.level.reservations = self.reservations
        self.level.reservations_connection = self.reservations_connection

    def print_stats(self) -> None:
        """Print statistics about the planned paths and reservations."""
        self.logger.info('--- Solver Statistics ---')
        self.logger.info(f'Total drones: {len(self.level.drones)}')
        self.logger.info(f'Total steps: {self.level.number_of_steps - 1}')
