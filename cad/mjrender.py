"""Render modeli STL silnikiem MuJoCo (oświetlenie, cienie). Wymaga mujoco; używa GPU/OpenGL, gdy jest dostępny."""
import os

import mujoco
import numpy as np
from PIL import Image


def render_scene(items, fname, out_dir, azimuth=135, elevation=-20, distance=0.9, lookat=(0.0, 0.0, -0.03),
                 size=(1100, 1000)):
    """items: lista (stl_path, (r, g, b, a)). Współrzędne w mm w pliku, w scenie w metrach."""
    assets, geoms, mats = [], [], []
    for i, (path, rgba) in enumerate(items):
        assets.append(f'<mesh name="m{i}" file="{os.path.abspath(path).replace(os.sep, "/")}" scale="0.001 0.001 0.001"/>')
        geoms.append(f'<geom type="mesh" mesh="m{i}" material="mat{i}" contype="0" conaffinity="0"/>')
        mats.append(f'<material name="mat{i}" rgba="{rgba[0]} {rgba[1]} {rgba[2]} {rgba[3]}" specular="0.9" shininess="0.85"/>')
    xml = f"""
<mujoco>
  <visual><global offwidth="{size[0]}" offheight="{size[1]}"/><quality shadowsize="4096"/>
    <headlight ambient="0.35 0.35 0.35" diffuse="0.5 0.5 0.5" specular="0.1 0.1 0.1"/></visual>
  <asset>
    <texture type="skybox" builtin="gradient" rgb1="0.96 0.97 0.99" rgb2="0.78 0.82 0.88" width="64" height="64"/>
    {''.join(mats)}{''.join(assets)}
  </asset>
  <worldbody>
    <light pos="0.6 -0.6 1.2" dir="-0.4 0.4 -1" diffuse="0.8 0.8 0.8" castshadow="true"/>
    <light pos="-0.6 0.6 0.8" dir="0.5 -0.5 -0.8" diffuse="0.35 0.35 0.4" castshadow="false"/>
    {''.join(geoms)}
  </worldbody>
</mujoco>"""
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    cam = mujoco.MjvCamera()
    cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.azimuth, cam.elevation, cam.distance = azimuth, elevation, distance
    cam.lookat[:] = lookat
    renderer = mujoco.Renderer(model, height=size[1], width=size[0])
    renderer.update_scene(data, camera=cam)
    img = renderer.render()
    renderer.close()
    Image.fromarray(img).save(os.path.join(out_dir, fname))
