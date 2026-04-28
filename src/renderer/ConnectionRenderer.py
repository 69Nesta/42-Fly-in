from .models import ConnectionModel
from ..utils import Logger, Color
from ..Level import Level


class ConnectionRenderer:
    level: Level
    logger: Logger

    connections_models: list[ConnectionModel]

    def __init__(self, level: Level) -> None:
        self.level = level
        self.logger = Logger(
            print_log=level.logger.print_log,
            name='ConnectionRenderer',
            color=Color.BLUE
        )
        self.logger.log('Initializing connections renderer...')
        self.connections_models = []
        self._generate_models()

    def _generate_models(self) -> None:
        for connection in self.level.connections.all:
            model = ConnectionModel(connection)
            self.connections_models.append(model)

    def update(self) -> None:
        pass

    def draw(self) -> None:
        for model in self.connections_models:
            model.draw()

    def unload(self) -> None:
        self.logger.log('Unloading connection renderer...')
        for model in self.connections_models:
            model.unload()
        self.connections_models.clear()
