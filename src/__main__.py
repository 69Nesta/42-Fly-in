from pydantic import ValidationError
from .ArgsParser import ArgsParser
from argparse import Namespace
from .LevelLoader import LevelLoader
from .Level import Level
from .utils import Logger, Color
from .renderer.CoreRenderer import CoreRenderer
import sys


def run() -> None:
    logger: Logger = Logger(
        print_log=False,
        name='Main',
        color=Color.MAGENTA
    )
    try:
        args_parser: ArgsParser = ArgsParser()
        args: Namespace = args_parser.parse_args(sys.argv[1:])

        logger.print_log = args.verbose
        logger.log('Starting the program...')

        loader: LevelLoader = LevelLoader(
            filepath=args.input,
            verbose=args.verbose
        )
        level: Level = Level(
            loader=loader,
            verbose=args.verbose
        )

        renderer: CoreRenderer = CoreRenderer(
            level=level,
            verbose=args.verbose
        )
        renderer.run()

    except ValidationError as e:
        for error in e.errors():
            if error.get("ctx") and error.get("ctx", {}).get("error"):
                logger.error(f"Error: {error.get('ctx', {}).get('error')}")
            else:
                logger.error(f"Error: {error['msg']}")
    except ValueError as e:
        logger.error(f'Error: {e.__cause__ or e}')
    except Exception as e:
        logger.error(f'Unexpected error: {e}')


if __name__ == '__main__':
    run()
