from .renderer.CoreRenderer import CoreRenderer
from pydantic import ValidationError
from .LevelLoader import LevelLoader
from .MapSelector import MapSelector
from .ArgsParser import ArgsParser
from .OutputFile import OutputFile
from .utils import Logger, Color
from argparse import Namespace
from .Solver import Solver
from .Level import Level
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

        map_path: str
        if not args.input:
            map_path = MapSelector('maps').ask()
        else:
            map_path = args.input

        loader: LevelLoader = LevelLoader(
            filepath=map_path,
            verbose=args.verbose
        )

        level: Level = Level(
            loader=loader,
            verbose=args.verbose
        )

        solver: Solver = Solver(
            level=level
        )
        solver.plan_all_drones()

        output: OutputFile = OutputFile(
            filepath=args.output,
            level=level
        )
        output.generate()
        output.write()

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
    # except Exception as e:
    #     logger.error(f'Unexpected error: {e}')


if __name__ == '__main__':
    run()
