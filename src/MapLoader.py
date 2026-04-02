from pydantic import BaseModel, Field, PrivateAttr
from .Hub import Hub
from typing import ClassVar
import re


class MapLoader(BaseModel):
    filepath: str = Field()

    nb_drones: int = PrivateAttr(0)
    hubs: list[Hub] = PrivateAttr([])
    REGEX_NUMBER_DRONES: ClassVar[re.Pattern[str]] = re.compile(
        r"nb_drones: [0-9]+"
    )
    REGEX_HUB: ClassVar[re.Pattern[str]] = re.compile(
        r"(start_hub:|end_hub:|hub:)"
    )
    REGEX_CONNECTION: ClassVar[re.Pattern[str]] = re.compile(
        r"connection: "
    )

    def model_post_init(self, context):
        self.regex_number_drones = re.compile(r"nb_drones: [0-9]+")
        return super().model_post_init(context)

    def _remove_comments(self, data: str) -> list[str]:
        lines = data.splitlines()

        return [
            line.split('#')[0].strip()
            for line in lines
            if line.strip() and not line.strip().startswith('#')
        ]

    def _get_number_drones(self, line: str) -> int:
        matches: list[re.Match[str]] = list(
            self.regex_number_drones.finditer(line)
        )

        if len(matches) != 1:
            raise ValueError("'nb_drones' could not be found!")

        nb_drones_raw: str = matches[0].group(0).split('nb_drones: ')[1]
        nb_drones: int = int(nb_drones_raw)

        return (nb_drones)

    def _load(self) -> None:
        with open(self.filepath, 'r') as f:
            lines: list[str] = self._remove_comments(f.read())
            index: int = 0

            self.nb_drones = self._get_number_drones(lines[index])
            index += 1

            while (index < len(lines) and re.search(self.REGEX_HUB, lines[index])):
                self.hubs.append(Hub.from_str(lines[index]))
                index += 1

            while (index < len(lines) and re.search(self.REGEX_CONNECTION, lines[index])):
                # logic for connection parsing
                break
