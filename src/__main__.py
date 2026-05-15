from .network import Network, Node as NetworkNode
from .MapSelector import MapSelector
from .ArgsParser import ArgsParser
from .map_loader import MapLoader
from .utils import Logger, Color

from .algo.time_graph import TimeGraph
from .algo.bfs import BFS
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
        bfs: BFS = BFS(args.verbose, time_graph)  # noqa: F841
        dfs: DFS = DFS(args.verbose, time_graph)  # noqa: F841

        # dfs.run()

        # for i in range(0, 4):
        #     step_nodes = time_graph.get_step(i)

        for i in range(0, 4):
            step_nodes = time_graph.get_step(i)
            print(f'Time step {i} has {len(step_nodes)} nodes.')
            for node in step_nodes:
                if not isinstance(node.object, NetworkNode):
                    continue
                print(f'  Node: {node.object.get_name()} | at time {node.time}')
                print(f'    Connections: {len(node.get_connections())}')
                for edge, conn in node.get_connections():
                    if isinstance(edge.object, NetworkNode):
                        print(
                            f'      Neighbor: {edge.object.get_name()} | at time {edge.time}'
                        )

        for i in range(0, 4):
            step_nodes = bfs.get_step(i)
            logger.log(f'Time step {i} has {len(step_nodes)} nodes.')
            for node in step_nodes:
                if not isinstance(node.node.object, NetworkNode):
                    continue
                logger.log(f'  Node: {node.node.object.get_name()} | at time {node.node.time}')
                logger.log(f'    Connections: {len(node.edges)}')
                for edge in node.edges:
                    if isinstance(edge.get_other(node).node.object, NetworkNode):
                        logger.log(
                            f'      Neighbor: {edge.get_other(node).node.object.get_name()} | at time {edge.get_other(node).node.time} | capacity: {edge.capacity}'
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
    except ValueError as e:
        logger.error(f'Error: {e.__cause__ or e}')
    # except Exception as e:
    #     logger.error(f'Unexpected error: {e}')


if __name__ == '__main__':
    run()
