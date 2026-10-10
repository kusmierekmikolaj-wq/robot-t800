"""Analiza pobranych STL (dane nieufne: tylko odczyt siatek). Użycie: python -I inspect_ref.py <folder_stl> <folder_wyj>"""
import json
import os
import sys

sys.path.insert(0, r"C:\Users\Jeff\Documents\druk3d-robot\robot")
import numpy as np  # noqa: E402
import trimesh  # noqa: E402

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
rows, allb = [], []
for f in sorted(os.listdir(src), key=lambda s: int(s.split("_")[1])):
    m = trimesh.load(os.path.join(src, f), force="mesh")
    b = m.bounds
    allb.append(b)
    rows.append({"plik": f, "trojkaty": len(m.faces), "szczelna": bool(m.is_watertight),
                 "obj_cm3": round(float(m.volume) / 1000, 1) if m.is_watertight else None,
                 "min": [round(float(v), 1) for v in b[0]], "max": [round(float(v), 1) for v in b[1]],
                 "wym": [round(float(v), 1) for v in b[1] - b[0]]})
allb = np.array(allb)
lo, hi = allb[:, 0].min(0), allb[:, 1].max(0)
print(json.dumps({"razem_min": lo.round(1).tolist(), "razem_max": hi.round(1).tolist(),
                  "razem_wym": (hi - lo).round(1).tolist()}, ensure_ascii=False))
for r in rows:
    print(f"{r['plik'][:48]:48s} tri={r['trojkaty']:7d} szczel={str(r['szczelna'])[0]} obj={r['obj_cm3']} "
          f"wym={r['wym']} min={r['min']}")
json.dump(rows, open(os.path.join(out, "ref_parts.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

from cad.mjrender import render_scene  # noqa: E402

items = []
for r in rows:
    name = r["plik"]
    col = (0.62, 0.65, 0.7, 1)
    if "eye_lense" in name:
        col = (0.9, 0.1, 0.1, 1)
    elif "Dowel" in name or "Cilindro" in name or "Cubo" in name:
        col = (0.95, 0.75, 0.2, 1)
    elif "jaw" in name and "piston" not in name:
        col = (0.75, 0.78, 0.82, 1)
    items.append((os.path.join(src, name), col))
ctr = ((lo + hi) / 2 / 1000).tolist()
dist = float((hi - lo).max()) / 1000 * 2.4
for nm, az, el in (("ref_iso", 135, -20), ("ref_gora", 90, -85)):
    render_scene(items, nm + ".png", out, azimuth=az, elevation=el, distance=dist, lookat=tuple(ctr))
print("ok")
