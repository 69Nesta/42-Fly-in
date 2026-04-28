from pyray import Mesh, Model, Image
import pyray as pr


class SkyBox:
    """Renders the background skybox environment.

    Attributes:
        skybox_mesh: Sphere mesh for skybox geometry.
        skybox_model: PyRay model for the skybox.
        hdr_image: HDR image texture for the skybox.
    """
    skybox_mesh: Mesh
    skybox_model: Model

    hdr_image: Image

    def __init__(self) -> None:
        """Initialize the skybox with mesh and texture."""
        self.skybox_mesh = pr.gen_mesh_sphere(1.0, 32, 100)
        self.skybox_model = pr.load_model_from_mesh(self.skybox_mesh)

        self.hdr_image = pr.load_image('src/assets/skybox/skybox.jpg')
        self.skybox_model.materials[0].maps[
            pr.MaterialMapIndex.MATERIAL_MAP_ALBEDO
        ].texture = pr.load_texture_from_image(self.hdr_image)

    def update(self) -> None:
        """Update skybox (placeholder for future logic)."""
        pass

    def draw_3d(self) -> None:
        """Draw the skybox centered at camera position."""
        pr.draw_model_ex(
            self.skybox_model,
            pr.Vector3(0, 0, 0),
            pr.Vector3(1, 0, 0),
            -90,
            pr.Vector3(-500, -500, -500),
            pr.WHITE
        )

    def unload(self) -> None:
        """Unload and clean up skybox resources."""
        pr.unload_model(self.skybox_model)
        pr.unload_image(self.hdr_image)
