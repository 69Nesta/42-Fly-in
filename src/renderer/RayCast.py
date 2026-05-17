from pyray import Vector3, Ray, RayCollision, BoundingBox, Matrix
from .models import CollisionModel
from ..utils import Logger, Color
from ..Level import Level
import pyray as pr


class RayCast:
    """Ray casting system for 3D object intersection detection.

    Manages collision detection between rays (e.g., mouse rays) and
    3D models in the scene.

    Args:
        verbose: Whether to enable verbose logging.

    Attributes:
        _entries: Dictionary mapping collision models to their bounding boxes.
    """
    level: Level

    _entries: dict[CollisionModel, BoundingBox]

    def __init__(self, verbose: bool) -> None:
        """Initialize the ray casting system.

        Args:
            level: The Level instance containing scene data.
        """
        self.logger = Logger(
            print_log=verbose,
            name='RayCast',
            color=Color.YELLOW
        )
        self.logger.log('Initializing ray cast...')

        self._entries = {}

    def register(self, model: CollisionModel) -> None:
        """Register a collision model for ray casting.

        Args:
            model: The collision model to register.
        """
        bounds: BoundingBox = pr.get_mesh_bounding_box(
            model.get_collision_model().meshes[0]
        )

        self._entries.update({
            model: bounds
        })

    def cast(self, ray: Ray) -> list[tuple[CollisionModel, RayCollision]]:
        """Cast a ray and find all intersected models.

        Args:
            ray: The ray to cast.

        Returns:
            List of (model, collision) tuples, sorted by distance.
        """
        touched_models: list[tuple[CollisionModel, RayCollision]] = []
        bounds: BoundingBox = BoundingBox()

        for model, local_bounds in self._entries.items():
            position: Vector3 = model.get_collision_position()

            bounds.min = pr.vector3_add(local_bounds.min, position)
            bounds.max = pr.vector3_add(local_bounds.max, position)

            if not pr.get_ray_collision_box(ray, bounds).hit:
                continue

            translation: Matrix = pr.matrix_translate(
                position.x, position.y, position.z
            )
            rotation: Matrix = pr.matrix_rotate(
                model.get_collision_rotation_axis(),
                model.get_collision_rotation()
            )

            transform: Matrix = pr.matrix_multiply(rotation, translation)
            col: RayCollision = pr.get_ray_collision_mesh(
                ray, model.get_collision_model().meshes[0], transform
            )
            if col.hit:
                touched_models.append((model, col))

        touched_models.sort(key=lambda x: x[1].distance)
        return touched_models
