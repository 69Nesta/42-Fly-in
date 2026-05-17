from .CollisionModel import CollisionModel
from ..ColorMap import color_map
from pyray import Model, Vector3
# from ...Node import Node
from ...network import Node
import pyray as pr


class NodeModel(CollisionModel):
    """3D visual model for a node with color indicator.

    Renders node geometry with a color cylinder to indicate node properties.

    Attributes:
        model: PyRay model for node geometry.
        color_model: PyRay model for the color indicator.
        collision_model: Flat cube mesh for collision detection.
        node: The Node object this model represents.
    """
    model: Model
    color_model: Model

    collision_model: Model
    node: Node

    def __init__(self, node: Node, model: Model, color_model: Model) -> None:
        """Initialize a node model.

        Args:
            node: The Node object to visualize.
            model: PyRay model for node geometry.
            color_model: PyRay model for color indicator.
        """
        super().__init__()
        self.node = node
        self.model = model
        self.color_model = color_model
        self.collision_model = pr.load_model_from_mesh(
            pr.gen_mesh_cube(1, 0.1, 1)
        )

    def get_collision_model(self) -> Model:
        """Get the collision model for raycasting.

        Returns:
            The flat cube collision model.
        """
        return self.collision_model

    def get_position(self) -> Vector3:
        """Get the node's 3D world position.

        Returns:
            Vector3 position in world space.
        """
        return Vector3(self.node.x * 3, 1, self.node.y * 3)

    def get_collision_position(self) -> Vector3:
        """Get the collision model's world position.

        Returns:
            Vector3 position slightly above the node.
        """
        return Vector3(self.node.x * 3, 1.05, self.node.y * 3)

    def draw(self) -> None:
        """
        Draw the node model with color indicator and optional collision
        wireframe
        """
        pr.draw_model_ex(
            self.model,
            self.get_position(),
            Vector3(0, 1, 0),
            0,
            Vector3(0.5, 0.5, 0.5),
            pr.WHITE
        )
        pr.draw_model_ex(
            self.color_model,
            self.get_position(),
            Vector3(0, 1, 0),
            0,
            Vector3(1, 0.4, 1),
            color_map.get(
                self.node.metadata.get_color(),
                pr.RAYWHITE
            )
        )

        if self.is_selected:
            self.is_selected = False
            pr.draw_model_wires_ex(
                self.collision_model,
                self.get_collision_position(),
                self.get_collision_rotation_axis(),
                self.get_collision_rotation(),
                Vector3(1, 1, 1),
                pr.WHITE
            )

    def unload(self) -> None:
        """Unload and clean up the collision model."""
        pr.unload_model(self.collision_model)
