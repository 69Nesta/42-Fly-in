from .errors import (
    FileNotFoundError as _FileNotFoundError,
    PermissionError as _PermissionError,
    NotAFileError
)
from collections import defaultdict
from .Connections import Connection
from .Level import Level
from .Hub import Hub
import os


class OutputFile:
    filepath: str
    level: Level
    lines: dict[int, list[str]] = defaultdict(list)

    def __init__(self, filepath: str, level: Level) -> None:
        self.filepath = filepath
        self.level = level

    def generate(self) -> None:
        for step in range(self.level.number_of_steps):
            for drone in self.level.drones:
                hub_or_conn = drone.get_step_at_time(step)

                if hub_or_conn is None:
                    continue
                if isinstance(hub_or_conn, Hub):
                    self.lines[step].append(
                        f'D{drone.id + 1}-{hub_or_conn.name}'
                    )
                elif isinstance(hub_or_conn, Connection):
                    self.lines[step].append(
                        f'D{drone.id + 1}-{hub_or_conn.get_id()}'
                    )

    def write(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        except FileNotFoundError:
            pass
        try:
            with open(self.filepath, 'w') as f:
                f.write(
                    '\n'.join(
                        ' '.join(line) for line in self.lines.values()
                    )
                )
        except FileNotFoundError:
            raise _FileNotFoundError(self.filepath)
        except PermissionError:
            raise _PermissionError(self.filepath)
        except IsADirectoryError:
            raise NotAFileError(self.filepath)
