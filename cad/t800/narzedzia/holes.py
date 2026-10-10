"""Ustawia czaszkę (obrót -40 st. wokół Y) i szuka okrągłych otworów: w czaszce o osi Y, w szczęce o osi X pliku.
python -I holes.py <folder_stl_ref> <folder_zlozona>
"""
import json
import os
import sys

import numpy as np
import trimesh

SRC, D = sys.argv[1], sys.argv[2]
ANG = -40.0
whole = trimesh.load(os.path.join(D, "czaszka_zlozona.stl"), force="mesh")
Rm = trimesh.transformations.rotation_matrix(np.radians(ANG), [0, 1, 0], whole.centroid)
w2 = whole.copy()
w2.apply_transform(Rm)
C = np.eye(4)
C[:3, 3] = -w2.bounds.mean(0)
M = C @ Rm
w2.apply_transform(C)
w2.export(os.path.join(D, "czaszka_ustawiona.stl"))
json.dump({"M": M.tolist(), "obrot_y_st": ANG}, open(os.path.join(D, "orientacja.json"), "w"), indent=1)
print("czaszka ustawiona: wymiary", np.round(w2.extents, 1), "bounds", np.round(w2.bounds, 1).tolist())


def holes(mesh, axis, offsets, rmin=1.0, rmax=7.0):
    axis = np.asarray(axis, float)
    found = []
    for o in offsets:
        sec = mesh.section(plane_origin=axis * o, plane_normal=axis)
        if sec is None:
            continue
        for loop in sec.discrete:
            pts = np.asarray(loop)
            if len(pts) < 8:
                continue
            c = pts.mean(0)
            r = np.linalg.norm(pts - c, axis=1)
            if rmin <= r.mean() <= rmax and r.std() / r.mean() < 0.06:
                found.append((round(float(o), 1), np.round(c, 2).tolist(), round(float(r.mean()), 2)))
    return found


print("\nCZASZKA - otwory o osi Y (przekroje co 3 mm):")
for h in holes(w2, [0, 1, 0], np.arange(w2.bounds[0][1] + 1, w2.bounds[1][1] - 1, 3.0)):
    print("  y=", h[0], "srodek(xyz)=", h[1], "r=", h[2])

jaw = trimesh.load(os.path.join(SRC, "obj_1_jaw_001.stl"), force="mesh")
print("\nSZCZEKA (uklad pliku): bounds", np.round(jaw.bounds, 1).tolist())
for ax, i in (([1, 0, 0], 0), ([0, 1, 0], 1), ([0, 0, 1], 2)):
    hs = holes(jaw, ax, np.arange(jaw.bounds[0][i] + 0.5, jaw.bounds[1][i] - 0.5, 1.5), rmin=0.8, rmax=9.0)
    print(" os", ax, "znaleziono", len(hs))
    for h in hs[:40]:
        print("   off=", h[0], "srodek=", h[1], "r=", h[2])
