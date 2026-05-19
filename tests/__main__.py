from src.utils import Logger, Color
from .test_all_map import run_all_map

from argparse import ArgumentParser
import sys


def run_tests() -> None:
    """Run all test cases for the Fly In application."""
    argparse = ArgumentParser(description='Run Fly In tests')
    argparse.add_argument(
        '--maps-dir',
        '-m',
        type=str,
        default='maps',
        help='Directory containing map files for testing'
    )
    argparse.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging during tests'
    )
    args = argparse.parse_args(sys.argv[1:])

    logger = Logger(
        name='TestRunner',
        print_log=args.verbose,
        color=Color.GREEN
    )

    logger.info('Running all tests...')
    run_all_map(args.maps_dir, args.verbose)


if __name__ == '__main__':
    run_tests()
