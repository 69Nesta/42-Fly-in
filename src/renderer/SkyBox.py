from pyray import Mesh, Model, Image
import pyray as pr


class SkyBox:
    skybox_mesh: Mesh
    skybox_model: Model

    hdr_image: Image

    def __init__(self) -> None:
        self.skybox_mesh = pr.gen_mesh_sphere(1.0, 32, 100)
        self.skybox_model = pr.load_model_from_mesh(self.skybox_mesh)

        self.hdr_image = pr.load_image('src/assets/skybox/skybox.jpg')
        self.skybox_model.materials[0].maps[
            pr.MaterialMapIndex.MATERIAL_MAP_ALBEDO
        ].texture = pr.load_texture_from_image(self.hdr_image)

    def update(self) -> None:
        pass

    def draw_3d(self) -> None:
        pr.draw_model_ex(
            self.skybox_model,
            pr.Vector3(0, 0, 0),
            pr.Vector3(1, 0, 0),
            -90,
            pr.Vector3(-500, -500, -500),
            pr.WHITE
        )

    def unload(self) -> None:
        pr.unload_model(self.skybox_model)
        pr.unload_image(self.hdr_image)
