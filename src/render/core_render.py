from .renderer.environment_renderer import EnvironmentRenderer
from .renderer.connection_renderer import ConnectionRenderer
from .controller.input_controller import InputController
from .renderer.drones_renderer import DronesRenderer
from .renderer.nodes_renderer import NodesRenderer
from .renderer.ui_renderer import UIRenderer
from ..utils import Logger, Color
from ..network import Network
from .utils.ray_cast import RayCast

from pyray import Vector3
import pyray as pr


class CoreRender:
    """Main 3D renderer for the Fly In simulation visualization.

    Manages all rendering components including nodes, connections, drones,
    environment, and UI. Orchestrates the main render loop.

    Attributes:
        WIDTH: Window width in pixels.
        HEIGHT: Window height in pixels.
        logger: Logger instance for debug output.
        level: The Level instance to render.
        title: Window title.
        camera: PyRay 3D camera.
        input_controller: Handles user input and camera movement.
        ray_cast: Ray casting system for intersection detection.
        node_renderer: Renderer for node objects.
        connection_renderer: Renderer for connections.
        drones_renderer: Renderer for drone models.
        ui_renderer: Renderer for UI overlay.
    """
    WIDTH: int = 1280
    HEIGHT: int = 720

    logger: Logger
    network: Network

    title: str
    camera: pr.Camera3D
    input_controller: InputController
    ray_cast: RayCast

    node_renderer: NodesRenderer
    connection_renderer: ConnectionRenderer
    drones_renderer: DronesRenderer
    ui_renderer: UIRenderer

    def __init__(self, network: Network, verbose: bool = False) -> None:
        """Initialize the core renderer.

        Sets up the PyRay window, camera, and all rendering components.

        Args:
            level: The Level instance to render.
            verbose: Whether to enable verbose logging. Defaults to False.
        """
        self.title = "Fly In - Renderer"
        self.logger = Logger(
            print_log=verbose,
            name='Renderer',
            color=Color.BRIGHT_CYAN
        )
        self.logger.log('Initializing renderer...')

        self.network = network
        pr.set_trace_log_level(pr.TraceLogLevel.LOG_NONE)
        pr.init_window(self.WIDTH, self.HEIGHT, self.title)
        pr.set_target_fps(60)

        self.camera = pr.Camera3D(
            Vector3(10.0, 4.0, 10.0),
            Vector3(0.0, 0.0, 0.0),
            Vector3(0.0, 1.0, 0.0),
            60.0,
            pr.CameraProjection.CAMERA_PERSPECTIVE,
        )

        pr.gui_set_style(
            pr.GuiControl.DEFAULT, pr.GuiDefaultProperty.TEXT_SIZE, 30
        )

        self.input_controller = InputController(
            self.camera,
            self.WIDTH,
            self.HEIGHT
        )
        self.ray_cast = RayCast(verbose)

        self.environment_renderer = EnvironmentRenderer(self.network)
        self.node_renderer = NodesRenderer(self.network, self.ray_cast)
        self.connection_renderer = ConnectionRenderer(self.network)
        self.drones_renderer = DronesRenderer(self.network, self.ray_cast)
        self.ui_renderer = UIRenderer(
            self.network,
            self.WIDTH, self.HEIGHT,
            self.ray_cast,
            self.camera,
            self.input_controller
        )

    def run(self) -> None:
        """Start the main render loop.

        Continuously updates all renderers, handles input, and draws
        the 3D scene and UI overlay until the window is closed.
        """
        while not pr.window_should_close():
            time: float = pr.get_time()

            # Update
            self.input_controller.update()
            self.environment_renderer.update(time)
            self.node_renderer.update()
            self.connection_renderer.update()
            self.drones_renderer.update()

            ray = pr.get_screen_to_world_ray(
                self.input_controller.get_current_pointing(),
                self.camera
            )
            self.ui_renderer.update(ray)

            # Clear and start drawing
            # pr.rl_set_clip_planes(0.1, 100000.0)
            pr.begin_drawing()
            pr.clear_background(pr.BLACK)

            # 3D scene
            pr.begin_mode_3d(self.camera)
            self.environment_renderer.draw()
            self.connection_renderer.draw()
            self.node_renderer.draw()
            self.drones_renderer.draw()
            pr.end_mode_3d()

            # 2D overlay
            self.ui_renderer.draw()

            pr.end_drawing()

        self.logger.log('Closing renderer...')
        self.environment_renderer.unload()
        self.node_renderer.unload()
        self.connection_renderer.unload()
        self.drones_renderer.unload()
        pr.close_window()
