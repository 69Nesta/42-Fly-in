from .utils import Logger, Color
from .Level import Level
# import heapq


class Solver():
    def __init__(self, level: Level):
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='Solver',
            color=Color.BRIGHT_RED
        )
        self.logger.log('Initializing solver...')
        self.level.connections.get_from_hub(self.level.start_hub)
        for connection in self.level.connections.all:
            self.logger.log(
                f'Connection: {connection.hubs[0].name} <-> '
                f'{connection.hubs[1].name}'
            )

    def solve(self) -> None:
        pass
