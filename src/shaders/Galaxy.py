from raylib import ffi
from pyray import (Mesh, Model, Vector3)
import pyray as pr


class Galaxy:
    def __init__(self) -> None:
        self.cube: Mesh = pr.gen_mesh_cube(1.0, 1.0, 1.0)
        self.skybox: Model = pr.load_model_from_mesh(self.cube)

        self.skybox.materials[0].shader = pr.load_shader(
            'src/shaders/glsl/galaxy.vs',
            'src/shaders/glsl/galaxy.fs'
        )
        self.loc_time = pr.get_shader_location(
            self.skybox.materials[0].shader, 'time'
        )

    def update(self, time: float) -> None:
        time_val = ffi.new("float[1]", [float(time)])

        pr.set_shader_value(
            self.skybox.materials[0].shader,
            self.loc_time,
            time_val,
            pr.ShaderUniformDataType.SHADER_UNIFORM_FLOAT
        )

    def draw_3d(self) -> None:
        pr.rl_disable_backface_culling()
        pr.rl_disable_depth_mask()

        pr.draw_model(self.skybox, Vector3(0, 0, 0), 1.0, pr.WHITE)

        pr.rl_enable_backface_culling()
        pr.rl_enable_depth_mask()

    def unload(self) -> None:
        pr.unload_shader(self.skybox.materials[0].shader)
        pr.unload_model(self.skybox)
