from .Color import Color
import datetime


class Logger:
    """Lightweight logger for console output.

    Attributes:
        print_log (bool): Whether logging is enabled.
        name (str): Name displayed in log messages.
        color (Color): Color used for the name tag.
    """
    print_log: bool
    name: str
    color: Color

    def __init__(
                self,
                print_log: bool = False,
                name: str = 'Logger',
                color: Color = Color.GRAY
            ) -> None:
        self.print_log = print_log
        self.name = name
        self.color = color

    def log(self, message: str, end: str | None = '\n') -> None:
        """Print a debug/info message when logging is enabled.

        Args:
            message (str): Message to print.
            end (str | None): End character appended to the message.
        """
        if (self.print_log):
            print(f'{self._get_format()} {message}', end=end)

    def error(self, message: str, end: str | None = '\n') -> None:
        """Print an error message (always shown).

        Args:
            message (str): Error message to print.
            end (str | None): End character appended to the message.
        """
        print(
            f'{self._get_format()} {Color.RED}[ERROR]{Color.RESET} {message}',
            end=end
        )

    def warning(self, message: str, end: str | None = '\n') -> None:
        """Print a warning message (always shown).

        Args:
            message (str): Warning message to print.
            end (str | None): End character appended to the message.
        """
        print(
            f'{self._get_format()} {Color.YELLOW}[WARNING]{Color.RESET} '
            f'{message}',
            end=end
        )

    @staticmethod
    def warning_static(
                name: str,
                message: str,
                color: Color = Color.WHITE,
                end: str | None = '\n'
            ) -> None:
        """Print a warning message from a static context (always shown).

        Args:
            name (str): Name to include in the log prefix.
            message (str): Warning message to print.
            color (Color): Color to use for the name tag in the log prefix.
            end (str | None): End character appended to the message.
        """
        print(
            f'{Logger.get_format_static(color, name)} {Color.YELLOW}[WARNING]'
            f'{Color.RESET} {message}',
            end=end
        )

    def info(self, message: str, end: str | None = '\n') -> None:
        """Print an informational message (always shown).

        Args:
            message (str): Message to print.
            end (str | None): End character appended to the message.
        """
        print(
            f'{self._get_format()} {Color.RESET} {message}',
            end=end
        )

    def _get_format(self) -> str:
        """Return the formatted prefix used for all log lines.

        Returns:
            str: Formatted prefix including time and colored name tag.
        """
        return self.get_format_static(self.color, self.name)

    @staticmethod
    def get_format_static(color: Color, name: str) -> str:
        """Return the formatted prefix for static contexts.

        Args:
            name (str): Name to include in the prefix.
        Returns:
            str: Formatted prefix including time and colored name tag.
        """
        return f'{Color.GRAY}[{Logger.get_date_time()}] {color}[' +\
               f'{name}]{Color.RESET}'

    @staticmethod
    def get_date_time() -> str:
        """Return the current time string used in the log prefix.

        Returns:
            str: Formatted time string (HH:MM:SS).
        """
        now = datetime.datetime.now()
        return now.strftime("%X")
