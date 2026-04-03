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
            '--verbose', '-v',
            help='Enable verbose logging',
            action='store_true'
        )
        self._logger.log('Arguments registered successfully.')

    def parse_args(self, args: Sequence[str] | None = None) -> Namespace:
        return self._parser.parse_args(args)
