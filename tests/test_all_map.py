from src.network import Network
from src.map_loader import MapLoader
from src.algo.dinic import Dinic

import os


# Collect results as (map_path, simulation_length)
results: list[tuple[str, int]] = []


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


def run_all_map(map_dir: str, verbose: bool) -> None:
    """
    Run all maps in the specified directory using the Dinic algorithm.

    Args:
        map_dir: The directory containing map folders and files.
        verbose: Whether to enable verbose logging during execution.
    """
    for map_folder, map_files in load_maps(map_dir).items():
        if map_folder == 'customs':
            continue
        for map_file in map_files:
            _run_map(os.path.join(map_dir, map_folder, map_file), verbose)

    # Print summary table
    print('\n| map_path | simulation_length |')
    print('|---|---|')
    for map_path, sim_len in results:
        print(f'| {map_path} | {sim_len} |')


def _run_map(map_path: str, verbose: bool) -> int:
    """
    Run a single map using the Dinic algorithm.

    Args:
        map_path: The file path to the map to run.
        verbose: Whether to enable verbose logging during execution.
    """
    print(f'Running map: {map_path}')
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
