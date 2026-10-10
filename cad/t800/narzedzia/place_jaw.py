"""Osadza szczękę: oś tarcz zawiasu szczęki -> gniazda w czaszce, potem obrót do zetknięcia zębów.
python -I place_jaw.py <ref> <zlozona> [sign theta]   (bez sign/theta: przegląd kątów + plansza)
"""
import json
import os
import sys

import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree

SRC, D = sys.argv[1], sys.argv[2]
sys.path.insert(0, r"C:\Users\Jeff\Documents\druk3d-robot\robot")
from cad.mjrender import render_scene  # noqa: E402

skull = trimesh.load(os.path.join(D, "czaszka_ustawiona.stl"), force="mesh")
jaw = trimesh.load(os.path.join(SRC, "obj_1_jaw_001.stl"), force="mesh")
HINGE_SKULL = np.array([19.5, -1.7, -64.8])
HINGE_JAW = np.array([(48.0 + 135.2) / 2, 44.6, 47.1])


def T_of(sign, theta):
    # kolumny: obrazy osi pliku szczęki (x -> sign*Y, y -> X, z -> -sign*Z), wyznacznik +1
    B = np.array([[0, 1, 0], [sign, 0, 0], [0, 0, -sign]], float)
    assert abs(np.linalg.det(B) - 1) < 1e-9
    T = np.eye(4)
    T[:3, :3] = B
    T[:3, 3] = HINGE_SKULL - B @ HINGE_JAW
    return trimesh.transformations.rotation_matrix(np.radians(theta), [0, 1, 0], HINGE_SKULL) @ T


pieces = [os.path.join(D, f) for f in sorted(os.listdir(D)) if f.startswith("zl_") and f.endswith(".stl")]
M = np.array(json.load(open(os.path.join(D, "orientacja.json")))["M"])
ori = []
for i, p in enumerate(pieces):
    m = trimesh.load(p, force="mesh")
    m.apply_transform(M)
    q = os.path.join(D, f"_ori{i}.stl")
    m.export(q)
    ori.append(q)


def render(sign, theta, fname, az=90, el=-5, size=(420, 420), dist=0.5):
    j = jaw.copy()
    j.apply_transform(T_of(sign, theta))
    j.export(os.path.join(D, "_jaw.stl"))
    items = [(q, (0.62, 0.65, 0.7, 1)) for q in ori] + [(os.path.join(D, "_jaw.stl"), (0.85, 0.6, 0.3, 1))]
    render_scene(items, fname, D, azimuth=az, elevation=el, distance=dist, lookat=(0.0, 0, -0.02), size=size)


if len(sys.argv) > 4:
    sign, theta = int(sys.argv[3]), float(sys.argv[4])
    T = T_of(sign, theta)
    json.dump({"T_szczeka": T.tolist(), "sign": sign, "theta": theta, "zawias": HINGE_SKULL.tolist()},
              open(os.path.join(D, "szczeka.json"), "w"), indent=1)
    j = jaw.copy()
    j.apply_transform(T)
    j.export(os.path.join(D, "szczeka_ustawiona.stl"))
    for nm, az, el in (("final_bok", 90, -5), ("final_przod", 180, -5), ("final_34", 140, -15)):
        render(sign, theta, nm + ".png", az, el, (900, 900), 0.6)
    print("zapisano")
    sys.exit(0)

sk_pts, _ = trimesh.sample.sample_surface(skull, 250000, seed=2)
tree = cKDTree(sk_pts)
jw_pts, _ = trimesh.sample.sample_surface(jaw, 20000, seed=3)
tiles = []
for sign in (1, -1):
    for theta in np.arange(-180, 180, 2.0):
        T = T_of(sign, theta)
        p = (T[:3, :3] @ jw_pts.T).T + T[:3, 3]
        c = p.mean(0) - HINGE_SKULL
        if not (c[0] > 15 and c[2] < -5):
            continue
        far = np.linalg.norm((p - HINGE_SKULL)[:, [0, 2]], axis=1) > 30      # bez okolic zawiasu
        d, _ = tree.query(p[far])
        print(sign, theta, "styk<0.8mm:", int((d < 0.8).sum()), "srodek:", np.round(c[[0, 2]], 1))
for sign in (1, -1):
    for theta in (20, 30, 40, 50):
        th = theta if sign > 0 else theta  # ten sam zakres
        render(sign, th, "_t.png")
        im = Image.open(os.path.join(D, "_t.png")).convert("RGB")
        ImageDraw.Draw(im).text((8, 8), f"sign={sign} theta={th}", fill=(0, 0, 0))
        tiles.append(im)
W = Image.new("RGB", (420 * 4, 420 * 2), "white")
for i, im in enumerate(tiles):
    W.paste(im, ((i % 4) * 420, (i // 4) * 420))
W.save(os.path.join(D, "szczeka_plansza.png"))
print("ok")
