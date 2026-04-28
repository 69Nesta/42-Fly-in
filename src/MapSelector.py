import questionary
import os


class MapSelector:
    """Manages discovery and selection of map files organized in directories.

    Attributes:
        maps_dir: Path to the root directory containing map folders.
        maps: Dictionary mapping folder names to lists of map files.
    """
    maps_dir: str
    maps: dict[str, list[str]]

    def __init__(self, maps_dir: str) -> None:
        """Initialize the map selector with a directory path.

        Args:
            maps_dir: Path to the directory containing map folders.
        """
        self.maps_dir = maps_dir
        self.maps = {}
        self._safe_load_maps()

    def _load_maps(self) -> None:
        """Load all map files from the maps directory.

        Scans the maps directory for subdirectories and collects all .txt files
        within them, organizing them by folder.
        """
        folders: list[str] = [
            f
            for f in os.listdir(self.maps_dir)
            if os.path.isdir(os.path.join(self.maps_dir, f))
        ]
        for folder in folders:
            for file in os.listdir(os.path.join(self.maps_dir, folder)):
                if file.endswith('.txt'):
                    if folder not in self.maps:
                        self.maps[folder] = []
                    self.maps[folder].append(file)
            self.maps[folder].sort()

    def _safe_load_maps(self) -> None:
        """Safely load maps with error handling.

        Raises:
            ValueError: If there's an error loading maps from the directory.
        """
        try:
            self._load_maps()
        except Exception as e:
            raise ValueError(
                f'Error loading maps from directory {self.maps_dir!r}: {e}'
            )

    def ask(self) -> str:
        """Interactively prompt user to select a map file.

        Returns:
            The full path to the selected map file.

        Raises:
            ValueError: If no maps are found or selection is cancelled.
        """
        folders: list[str] = list(self.maps.keys())
        if not folders:
            raise ValueError(
                f'No map files were found under {self.maps_dir!r}.'
            )

        folders.sort()
        selected = questionary.select(
            "Pick a folder:",
            choices=folders
        ).ask()
        if selected is None:
            raise ValueError('Folder selection was cancelled or unavailable.')

        files: list[str] = self.maps[selected]
        if not files:
            raise ValueError(f'No map files available in folder {selected!r}.')

        file = questionary.select(
            "Pick a map:",
            choices=files
        ).ask()
        if file is None:
            raise ValueError('Map selection was cancelled or unavailable.')

        return os.path.join(self.maps_dir, selected, file)
