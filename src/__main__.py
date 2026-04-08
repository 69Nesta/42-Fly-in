from pydantic import ValidationError
from .ArgsParser import ArgsParser
from argparse import Namespace
from .MapLoader import MapLoader
from .utils import Logger, Color
from .Graphics import Graphics
import sys


def run() -> None:
    try:
        args_parser: ArgsParser = ArgsParser()
        args: Namespace = args_parser.parse_args(sys.argv[1:])

        logger: Logger = Logger(
            ACTIVE=args.verbose,
            name='Main',
            color=Color.MAGENTA
        )
        logger.log('Starting the program...')

        level: MapLoader = MapLoader(
            filepath=args.input,
            verbose=args.verbose
        )

        print('\nHubs: ')
        for hub in level.hubs.values():
            print(hub.model_dump())

        print('\nConnections: ')
        for connection in level.connections.get():
            print(connection.model_dump())

        print(f'\nNb drones: {level.nb_drones}')
        graphics: Graphics = Graphics(verbose=args.verbose)
        print('Entering main loop...')
        graphics.run()

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
