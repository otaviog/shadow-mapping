#!/usr/bin/env python

"""Sample of TensorViz for performing shadow mapping.
"""

from pathlib import Path
import argparse

import torch
import matplotlib.pyplot as plt
import tenviz


def _create_shadow_shaders(mesh, light_pos, light_projection_view,
                           ambient_color, diffuse_color, specular_color,
                           specular_exp):
    """Load and setup the depth and color passes shaders.

    Args:

        mesh (:obj:`tenviz.geometry.Geometry`): A mesh.

        light_pos (:obj:`torch.Tensor`): Light's position. Shape-type:
         (3) float.

        light_projection_view (:obj:`torch.Tensor`): Light's
         projection @ view matrix. Shape-type: (4 x 4) float.

        ambient_color (:obj:`torch.Tensor`): Ambient
         color. Shape-type: (3) float.

        diffuse_color (:obj:`torch.Tensor`): Diffuse
         color. Shape-type: (3) float.

        specular_color (:obj:`torch.Tensor`): Specular
         color. Shape-type: (3) float.

        specular_exp (float): Specular shining factor. From 0-127.

    """

    verts = tenviz.buffer_from_tensor(mesh.verts)
    normals = tenviz.buffer_from_tensor(mesh.normals)

    ##
    # Depth pass
    depth_pass = tenviz.DrawProgram(tenviz.DrawMode.Triangles,
                                    vert_shader_file=Path(
                                        __file__).parent / "depth_pass.vert",
                                    frag_shader_file=Path(
                                        __file__).parent / "depth_pass.frag",
                                    ignore_missing=True)
    # depth_pass.indices = faces
    depth_pass.indices.from_tensor(mesh.faces)
    depth_pass["in_position"] = verts
    depth_pass["LightProjectionModelview"] = tenviz.MatPlaceholder.ProjectionModelview

    ##
    # Color pass
    color_pass = tenviz.DrawProgram(tenviz.DrawMode.Triangles,
                                    vert_shader_file=Path(
                                        __file__).parent / "color_pass.vert",
                                    frag_shader_file=Path(
                                        __file__).parent / "color_pass.frag",
                                    ignore_missing=True)
    color_pass.indices.from_tensor(mesh.faces)

    color_pass["in_position"] = verts
    color_pass["in_normal"] = normals
    color_pass["Modelview"] = tenviz.MatPlaceholder.Modelview
    color_pass["ProjectionModelview"] = tenviz.MatPlaceholder.ProjectionModelview
    color_pass["NormalModelview"] = tenviz.MatPlaceholder.NormalModelview
    color_pass["LightPos"] = light_pos
    color_pass["LightProjectionModelview"] = light_projection_view
    color_pass["AmbientColor"] = ambient_color
    color_pass["DiffuseColor"] = diffuse_color
    color_pass["SpecularColor"] = specular_color
    color_pass["SpecularExp"] = float(specular_exp)
    color_pass.set_bounds(mesh.verts)

    return depth_pass, color_pass


def shadow_map_demo(mesh):
    light_proj = torch.from_numpy(tenviz.Projection.perspective(
        45, 0.01, 10000, aspect=1).to_matrix()).float()
    light_view = torch.tensor(
        [[6.1826736e-01, -1.7682267e-02,  7.8576899e-01,  0.0000000e+00],
         [6.8335772e-01,  5.0599408e-01, -5.2630055e-01, -6.2286854e-06],
         [-3.8828495e-01,  8.6235815e-01,  3.2492039e-01, -1.2934189e+00],
         [0.0000000e+00,  0.0000000e+00,  0.0000000e+00,  1.0000000e+00]])

    light_pos = light_view.inverse()[:3, 3]

    floor_y = mesh.verts[:, 1].min()
    floor = tenviz.geometry.Geometry(torch.Tensor([[-1, floor_y, 1],
                                                   [-1, floor_y, -1],
                                                   [1, floor_y, -1],
                                                   [1, floor_y, 1]]))
    floor.verts[:, (0, 2)] *= 0.35
    floor.normals = torch.tensor([[0, 1, 0],
                                  [0, 1, 0],
                                  [0, 1, 0],
                                  [0, 1, 0]], dtype=torch.float32)
    floor.faces = torch.tensor([[0, 1, 2],
                                [2, 3, 0]], dtype=torch.int32)

    ctx = tenviz.Context()
    with ctx.current():
        depth_scene = []
        color_scene = []
        light_projection_view = light_proj @ light_view
        for geo in [mesh, floor]:
            depth_pass, color_pass = _create_shadow_shaders(
                geo, light_pos, light_projection_view,
                torch.tensor([0.8, 0.7, 0.9]),
                torch.tensor([0.8, 0.241, 0.282]),
                torch.tensor([1.0, 1.0, 1.0]),
                50)
            depth_scene.append(depth_pass)
            color_scene.append(color_pass)

        depth_framebuffer = tenviz.create_framebuffer({})

    viewer = ctx.viewer(
        color_scene, cam_manip=tenviz.CameraManipulator.TrackBall)

    print("Press <ESC> to quit")
    print("Press 'v' to show light view's depth map")
    while True:
        ctx.render(light_proj, light_view, depth_framebuffer,
                   depth_scene, width=2048, height=2048)

        with ctx.current():
            for color_pass in color_scene:
                color_pass['ShadowMap'] = depth_framebuffer.get_depth()

        key = viewer.wait_key(1)
        if key < 0:
            break

        key = chr(key & 0xff)

        if key == 'V':
            with ctx.current():
                depth_image = depth_framebuffer.get_depth().to_tensor()
                plt.imshow(depth_image.cpu().numpy())
                plt.show()


def _main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_mesh", metavar="input-mesh",
                        help="Input mesh file (.ply, .off, ...)")

    args = parser.parse_args()

    mesh = tenviz.io.read_3dobject(args.input_mesh)
    if mesh.normals is None:
        mesh.normals = tenviz.geometry.compute_normals(
            mesh.verts, mesh.faces)
    shadow_map_demo(mesh)


if __name__ == "__main__":
    _main()
