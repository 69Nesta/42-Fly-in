import questionary
import os


class MapSelector:
    maps_dir: str
    maps: dict[str, list[str]]

    def __init__(self, maps_dir: str) -> None:
        self.maps_dir = maps_dir
        self.maps = {}
        self._safe_load_maps()

    def _load_maps(self) -> None:
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

    def _safe_load_maps(self) -> None:
        try:
            self._load_maps()
        except Exception as e:
            raise ValueError(
                f'Error loading maps from directory {self.maps_dir!r}: {e}'
            )

    def ask(self) -> str:
        folders: list[str] = list(self.maps.keys())
        if not folders:
            raise ValueError(
                f'No map files were found under {self.maps_dir!r}.'
            )

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
