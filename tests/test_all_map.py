from src.network import Network
from src.map_loader import MapLoader
from src.algo.dinic import Dinic
from src.utils import Logger

import os


def load_maps(maps_dir: str) -> dict[str, list[str]]:
    """
    Load maps from a directory and return a structured dictionary.

    Args:
        maps_dir: The directory path containing map folders and files.
    Returns:
        A dictionary where keys are folder names and values are lists of map
        file names.
    """
    folders: list[str] = [
        f
        for f in os.listdir(maps_dir)
        if os.path.isdir(os.path.join(maps_dir, f))
    ]
    maps: dict[str, list[str]] = {}

    for folder in folders:
        for file in os.listdir(os.path.join(maps_dir, folder)):
            if file.endswith('.txt'):
                if folder not in maps:
                    maps[folder] = []
                maps[folder].append(file)
        maps[folder].sort()

    return maps


def run_all_map(map_dir: str, verbose: bool, logger: Logger) -> None:
    """
    Run all maps in the specified directory using the Dinic algorithm.

    Args:
        map_dir: The directory containing map folders and files.
        verbose: Whether to enable verbose logging during execution.
    """
    results: list[tuple[str, int | str]] = []

    for map_folder, map_files in load_maps(map_dir).items():
        for map_file in map_files:
            file_path: str = os.path.join(map_dir, map_folder, map_file)
            try:
                logger.info(f'Running map: {file_path}')
                results.append((file_path, _run_map(file_path, verbose)))
            except Exception as e:
                logger.error(
                    f'Error running map {file_path}: {e}'
                )
                results.append((file_path, 'Error'))
            print('\n' * 1)

    w0, w1 = (
        max(len(r[0]) for r in results),
        max(len(str(r[1])) for r in results)
    )
    w1 = max(w1, len('sim_len'))

    print('\n\nResults:')
    print(f'\n| {"map_path":<{w0}} | {"sim_len":<{w1}} |')
    print(f'|{"-" * (w0 + 2)}|{"-" * (w1 + 2)}|')
    for map_path, sim_len in results:
        print(f'| {map_path:<{w0}} | {sim_len:<{w1}} |')


def _run_map(map_path: str, verbose: bool) -> int:
    """
    Run a single map using the Dinic algorithm.

    Args:
        map_path: The file path to the map to run.
        verbose: Whether to enable verbose logging during execution.
    """
    loaded_map: MapLoader = MapLoader(filepath=map_path, verbose=verbose)
    network: Network = Network(loaded_map, verbose)

    dinic: Dinic = Dinic(network, verbose)
    dinic.solve()
    dinic.print_stats()

    sim_len: int = network.simulation_length

    try:
        network.unload()
    except Exception:
        pass

    del dinic
    del network
    del loaded_map

    return sim_len
