from .MapSelector import MapSelector
from .ArgsParser import ArgsParser
from .network import Network, Node as NetworkNode
from .map_loader import MapLoader
from .utils import Logger, Color

from .algo.time_graph import TimeGraph
from .algo.bfs import BFS, BFSNode
from .algo.dfs import DFS

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

        time_graph: TimeGraph = TimeGraph(
            verbose=args.verbose,
            network=network
        )
        bfs: BFS = BFS(args.verbose, time_graph)
        dfs: DFS = DFS(args.verbose, bfs, network)
        dfs.solve()

        for path in dfs.paths:
            logger.log(
                'Found path: ' +
                str([
                    f'{obj.node.object.get_name()} at time {obj.node.time}'
                    for obj in path
                    if isinstance(obj, BFSNode)
                ])
            )

        # # output: OutputFile = OutputFile(
        #     filepath=args.output,
        #     level=level
        # )
        # output.generate()
        # output.write()

        # renderer: CoreRenderer = CoreRenderer(
        #     level=level,
        #     verbose=args.verbose
        # )
        # renderer.run()

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
