from argparse import ArgumentParser, Namespace
from pydantic import BaseModel, PrivateAttr
from .utils import Logger, Color
from collections.abc import Sequence
from typing import Any


class ArgsParser(BaseModel):
    """Helper that registers and parses CLI arguments.

    Methods:
        register_arguments(): Register supported CLI flags and options.
        parse_args(args): Parse an optional list of arguments and return
            the resulting Namespace.
    """
    _logger: Logger = PrivateAttr()
    _parser: ArgumentParser = PrivateAttr()

    def model_post_init(self, _: Any) -> None:
        """Initialize the parser after model creation.

        Args:
            _: Unused context parameter from Pydantic.
        """
        self._logger = Logger(name='ArgsParser', color=Color.YELLOW)
        self.register_arguments()

    def register_arguments(self) -> None:
        """Register all supported command-line arguments.

        The arguments include input/output file paths, functions definition
        path, interactive mode toggle, cache directory and model name.
        """
        self._logger.log('Registering command-line arguments...')
        self._parser = ArgumentParser(
            description='Fly In - A nontrivial modular command-line'
            ' application'
        )

        self._parser.add_argument(
            '--input', '-i',
            help='Path to the input file',
            type=str,
            default=None
        )

        self._parser.add_argument(
            '--maps_dir', '-m',
            help='Path to the maps directory',
            type=str,
            default='maps'
        )

        self._parser.add_argument(
            '--output', '-o',
            help='Path to the output file',
            type=str,
            default='output.txt'
        )

        self._parser.add_argument(
            '--verbose', '-v',
            help='Enable verbose logging',
            action='store_true'
        )
        self._logger.log('Arguments registered successfully.')

    def parse_args(self, args: Sequence[str] | None = None) -> Namespace:
        """Parse command-line arguments.

        Args:
            args: Sequence of argument strings. If None, uses sys.argv.

        Returns:
            A Namespace object containing the parsed arguments.
        """
        return self._parser.parse_args(args)
