from raylib import ffi
from pyray import (Mesh, Model, Vector3, Matrix)
import pyray as pr


class Galaxy:
    """
    Renders a skybox with black hole and stars using Kerr-Newman black hole
    shader from Shadertoy. Features a dynamic accretion disk, photon ring,
    and procedurally generated star field.
    """
    cube: Mesh
    skybox: Model
    loc_time: int
    loc_resolution: int
    loc_mouse: int

    def __init__(self) -> None:
        self.cube = pr.gen_mesh_cube(1.0, 1.0, 1.0)
        self.skybox = pr.load_model_from_mesh(self.cube)

        # Load the stars shader with galaxy, moon, and star field
        self.skybox.materials[0].shader = pr.load_shader(
            'src/renderer/glsl/stars.vs',
            'src/renderer/glsl/stars.fs'
        )

        # Get uniform locations for shader parameters
        self.loc_time = pr.get_shader_location(
            self.skybox.materials[0].shader, 'iTime'
        )
        self.loc_resolution = pr.get_shader_location(
            self.skybox.materials[0].shader, 'iResolution'
        )
        self.loc_mouse = pr.get_shader_location(
            self.skybox.materials[0].shader, 'iMouse'
        )

        self.loc_view = pr.get_shader_location(
            self.skybox.materials[0].shader, 'matVie'
        )

    def update(
        self,
        time: float,
        view_matrix: Matrix
    ) -> None:
        # Update time uniform
        time_val = ffi.new('float[1]', [float(time)])
        pr.set_shader_value(
            self.skybox.materials[0].shader,
            self.loc_time,
            time_val,
            pr.ShaderUniformDataType.SHADER_UNIFORM_FLOAT
        )

        # Update resolution uniform
        resolution_val = ffi.new('float[2]', [
            float(pr.get_screen_width()),
            float(pr.get_screen_height())
        ])
        pr.set_shader_value(
            self.skybox.materials[0].shader,
            self.loc_resolution,
            resolution_val,
            pr.ShaderUniformDataType.SHADER_UNIFORM_VEC2
        )

        pr.set_shader_value_matrix(
            self.skybox.materials[0].shader,
            self.loc_view,
            view_matrix
        )

        # Update mouse position uniform
        # mouse_val = ffi.new('float[2]', [float(mouse_x), float(mouse_y)])
        # pr.set_shader_value(
        #     self.skybox.materials[0].shader,
        #     self.loc_mouse,
        #     mouse_val,
        #     pr.ShaderUniformDataType.SHADER_UNIFORM_VEC2
        # )

    def draw_3d(self) -> None:
        pr.rl_disable_backface_culling()
        pr.rl_disable_depth_mask()

        pr.draw_model(self.skybox, Vector3(0, 0, 0), 1.0, pr.WHITE)

        pr.rl_enable_backface_culling()
        pr.rl_enable_depth_mask()

    def unload(self) -> None:
        pr.unload_shader(self.skybox.materials[0].shader)
        pr.unload_model(self.skybox)
