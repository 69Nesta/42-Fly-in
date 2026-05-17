from .MapSelector import MapSelector
from .ArgsParser import ArgsParser
from .utils import Logger, Color
from .network import Network
from .map_loader import MapLoader
from .renderer import CoreRenderer
from .OutputFile import OutputFile

from .algo.dinic import Dinic


from pydantic import ValidationError
from argparse import Namespace
import sys


def run() -> None:
    """Main entry point for the Fly In application.

    Orchestrates the complete workflow:
    1. Parses command-line arguments
    2. Loads the selected map/level
    3. Solves drone routing paths
    4. Generates output file
    5. Runs the 3D renderer

    Handles validation and value errors gracefully with logging.
    """
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
            map_path = MapSelector(args.maps_dir).ask()
        else:
            map_path = args.input

        loaded_map: MapLoader = MapLoader(
            filepath=map_path,
            verbose=args.verbose
        )

        network: Network = Network(
            loaded_map=loaded_map,
            verbose=args.verbose
        )

        dinic: Dinic = Dinic(network, args.verbose)
        dinic.solve()

        output: OutputFile = OutputFile(
            filepath=args.output,
            network=network
        )
        output.generate()
        output.write()

        renderer: CoreRenderer = CoreRenderer(
            network=network,
            verbose=args.verbose
        )
        renderer.run()

    except ValidationError as e:
        for error in e.errors():
            if error.get('ctx') and error.get('ctx', {}).get('error'):
                logger.error(f'Error: {error.get('ctx', {}).get('error')}')
            else:
                logger.error(f'Error: {error['msg']}')
        logger.error(f'Error: {e.__cause__ or e}')
    # except Exception as e:
    #     logger.error(f'Unexpected error: {e}')


if __name__ == '__main__':
    run()
