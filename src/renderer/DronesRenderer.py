from ..utils import Logger, Color, MathUtils
from .models import DroneModel
from .RayCast import RayCast
from ..network import Network
from pyray import Model
import pyray as pr


class DronesRenderer:
    """Manages drone visualization and animation.

    Coordinates drone model instances, handles step-based animation,
    and integrates with the raycasting system for collision detection.

    Attributes:
        network: The Network instance.
        logger: Logger for debug output.
        raycast: RayCast system for collision detection.
        drone_model: Shared PyRay model for all drones.
        drones: List of DroneModel instances.
        current_step: Current simulation step.
        ANNIMATION_DURATION: Duration of drone movement animation in ms.
    """
    network: Network
    logger: Logger
    raycast: RayCast
    drone_model: Model

    drones: list[DroneModel]
    current_step: int = 0
    ANNIMATION_DURATION: int = 500

    def __init__(self, network: Network, ray_cast: RayCast) -> None:
        """Initialize the drones renderer.

        Args:
            network: The Network instance.
            ray_cast: The RayCast system for collision detection.
        """
        self.network = network
        self.logger = Logger(
            print_log=network.logger.print_log,
            name='DronesRenderer',
            color=Color.BRIGHT_YELLOW
        )
        self.logger.log('Initializing drones renderer...')
        self.raycast = ray_cast
        self.drone_model = pr.load_model('src/assets/models/bb8.glb')

        self.drones = []
        for idx, drone in enumerate(self.network.drones):
            model: DroneModel = DroneModel(
                idx=idx,
                frame_rate=60,
                model=self.drone_model,
                start=(drone.get_position_at_step(0), 0)
            )
            self.drones.append(model)
            self.raycast.register(model)

    def update(self) -> None:
        """Update drone positions based on keyboard input.

        RIGHT arrow advances simulation step, LEFT arrow goes back one step.
        """
        if (pr.is_key_pressed(pr.KeyboardKey.KEY_RIGHT)):
            if self.network.update_step(1):
                for idx, drone in enumerate(self.drones):
                    drone_pos = self.network.drones[idx].get_position_at_step(
                        self.network.current_step
                    )
                    drone.move_to(
                        position=drone_pos,
                        rotation=MathUtils.get_angle_between_points(
                            drone.last_animation_pos()[0],
                            drone_pos
                        ),
                        animation_time=self.ANNIMATION_DURATION,
                    )
        elif (pr.is_key_pressed(pr.KeyboardKey.KEY_LEFT)):
            if self.network.update_step(-1):
                for idx, drone in enumerate(self.drones):
                    drone_pos = self.network.drones[idx].get_position_at_step(
                        self.network.current_step
                    )
                    drone.back_to(
                        position=drone_pos,
                        rotation=MathUtils.get_angle_between_points(
                            drone.last_animation_pos()[0],
                            drone_pos
                        ),
                        animation_time=self.ANNIMATION_DURATION,
                    )

    def draw(self) -> None:
        """Draw all drone models."""
        for drone in self.drones:
            drone.draw()

    def unload(self) -> None:
        """Unload and clean up all drone models."""
        self.logger.log('Unloading drones renderer...')
        for drone in self.drones:
            drone.unload()
        pr.unload_model(self.drone_model)
