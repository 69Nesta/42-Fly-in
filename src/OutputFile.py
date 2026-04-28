from .errors import (
    FileNotFoundError as _FileNotFoundError,
    PermissionError as _PermissionError,
    NotAFileError
)
from collections import defaultdict
from .Connections import Connection
from .utils import Logger, Color
from .Level import Level
from .Hub import Hub
import os


class OutputFile:
    """Generates and writes simulation output to a file.

    Attributes:
        filepath: Path where the output file will be written.
        level: The Level instance containing drone and step information.
        logger: Logger instance for debug/info messages.
        lines: Dictionary mapping step numbers to lists of drone position str.
    """
    filepath: str
    level: Level
    logger: Logger
    lines: dict[int, list[str]]

    def __init__(self, filepath: str, level: Level) -> None:
        """Initialize the output file generator.

        Args:
            filepath: Path where the output will be written.
            level: The Level instance to generate output from.
        """
        self.filepath = filepath
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='OutputFile',
            color=Color.BLUE
        )
        self.lines = defaultdict(list)

    def generate(self) -> None:
        """Generate output by simulating each step.

        Populates self.lines with drone-to-location mappings for each step.
        """
        self.logger.log('Generating output file...')
        for step in range(self.level.number_of_steps):
            for drone in self.level.drones:
                hub_or_conn = drone.get_step_at_time(step)

                if hub_or_conn is None:
                    continue
                if isinstance(hub_or_conn, Hub):
                    self.lines[step].append(
                        f'{drone.get_name()}-{hub_or_conn.name}'
                    )
                elif isinstance(hub_or_conn, Connection):
                    self.lines[step].append(
                        f'{drone.get_name()}-{hub_or_conn.get_id()}'
                    )

    def write(self) -> None:
        """Write the generated output to the file.

        Raises:
            FileNotFoundError: If the file cannot be created.
            PermissionError: If there's a permission issue.
            NotAFileError: If the path is a directory.
        """
        self.logger.log('Writing output file...')
        directory = os.path.dirname(self.filepath)
        if directory:
            try:
                os.makedirs(directory, exist_ok=True)
            except PermissionError:
                raise _PermissionError(self.filepath)
        try:
            with open(self.filepath, 'w') as f:
                f.write(
                    '\n'.join(
                        ' '.join(line) for line in self.lines.values()
                    )
                )
                self.logger.log(f'Output file written to {self.filepath}')
        except FileNotFoundError:
            raise _FileNotFoundError(self.filepath)
        except PermissionError:
            raise _PermissionError(self.filepath)
        except IsADirectoryError:
            raise NotAFileError(self.filepath)
