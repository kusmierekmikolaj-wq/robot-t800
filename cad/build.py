"""Buduje wszystkie moduły głowy, sprawdza je (równolegle na wielu rdzeniach) i zapisuje STL/STEP oraz podglądy PNG.

Uruchom z katalogu robot/:   python -m cad.build
Wyniki: cad/out/ (STL do druku, STEP do CAD, raport.json, podglad_*.png)
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import cadquery as cq
import numpy as np

from . import neck, params as P, skull
from .geom import BIG, box, rot_y

OUT = os.path.join(os.path.dirname(__file__), "out")
TMP = os.path.join(OUT, "_tmp")
MAX_PART_MM = 240.0     # pole robocze P2S 256 mm minus margines na krawędzie stołu
DENSITY_PLA = 1.24      # g/cm3, pełny materiał; realna masa zależy od wypełnienia [szac.]
HEAD_SHELLS = ("M1_srodek", "M2_twarz", "M8_tyl")
HEAD_ALL = HEAD_SHELLS + ("M3_szczeka", "M7_oko_L", "M7_oko_P")
SWEEP = [(t, j) for t in (P.TILT[0], -15, 0, 20, P.TILT[1]) for j in (0, 10, P.JAW_MAX)]


def build_all():
    head = skull.build_head()
    eyes = skull.build_eyes()
    parts = {**head, "M3_szczeka": skull.build_jaw(), "M7_oko_L": eyes[0], "M7_oko_P": eyes[1],
             "M5_jarzmo": neck.build_yoke(), "M6_podstawa": neck.build_base()}
    return parts, neck.servo_envelopes()


def vol(shape):
    try:
        return shape.Volume()
    except Exception:
        return 0.0


def overlap(a, b):
    return vol(a.intersect(b))


def head_pose(parts, tilt_deg, jaw_deg):
    """Moduły głowy po pochyleniu (tilt >0: patrzy w górę) i otwarciu szczęki (jaw_deg >=0)."""
    posed = {k: rot_y(parts[k], -tilt_deg, P.TILT_AXIS) for k in HEAD_SHELLS + ("M7_oko_L", "M7_oko_P")}
    posed["M3_szczeka"] = rot_y(rot_y(parts["M3_szczeka"], jaw_deg, P.JAW_PIVOT), -tilt_deg, P.TILT_AXIS)
    return posed


def _sweep_worker(args):
    """Jedna poza zakresu ruchu; działa w osobnym procesie, wczytuje bryły z plików BREP."""
    tilt, jaw = args
    parts = {k: cq.Shape.importBrep(os.path.join(TMP, f"{k}.brep"))
             for k in HEAD_SHELLS + ("M3_szczeka", "M5_jarzmo", "M6_podstawa", "M7_oko_L", "M7_oko_P")}
    pose = head_pose(parts, tilt, jaw)
    shell = pose["M1_srodek"].fuse(pose["M2_twarz"], pose["M8_tyl"])
    head_all = shell.fuse(pose["M3_szczeka"])
    yoke_base = parts["M5_jarzmo"].fuse(parts["M6_podstawa"])
    return (f"tilt={tilt},szczeka={jaw}", {
        "glowa_vs_jarzmo_i_podstawa": round(overlap(head_all, yoke_base), 2),
        "szczeka_vs_czaszka": round(overlap(pose["M3_szczeka"], shell), 2),
    })


def checks(parts, env):
    res = {"moduly": {}, "kolizje": {}, "obwiednie": {}}
    for k, s in parts.items():
        bb = s.BoundingBox()
        dims = sorted([bb.xlen, bb.ylen, bb.zlen], reverse=True)
        res["moduly"][k] = {
            "objetosc_cm3": round(vol(s) / 1000, 1),
            "masa_g_pelne": round(vol(s) / 1000 * DENSITY_PLA),
            "wymiary_mm": [round(d, 1) for d in dims],
            "poprawna_bryla": bool(s.isValid()),
            "miesci_sie_na_stole": bool(dims[0] <= MAX_PART_MM),
        }
    shell = parts["M1_srodek"].fuse(parts["M2_twarz"], parts["M8_tyl"])
    for k in ("raspberry_pi5", "kamera"):
        res["obwiednie"][k] = round(overlap(env[k], shell), 2)
    for k in HEAD_SHELLS:
        res["kolizje"][f"M3_szczeka|{k}"] = round(overlap(parts["M3_szczeka"], parts[k]), 2)
    # kontrola dodatnia: sprawdzam, że wykrywanie kolizji w ogóle działa (kostka w płytce mocowania osi tilt)
    probe = box(P.TILT_AXIS[0] - 5, P.TILT_AXIS[0] + 5, 80, 88, -5, 5)
    res["kontrola_dodatnia_objetosc_mm3"] = round(overlap(parts["M1_srodek"], probe), 1)

    os.makedirs(TMP, exist_ok=True)
    for k, s in parts.items():
        s.exportBrep(os.path.join(TMP, f"{k}.brep"))
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=min(len(SWEEP), os.cpu_count() or 4)) as ex:
        res["zakres_ruchu"] = dict(ex.map(_sweep_worker, SWEEP))
    res["czas_kontroli_ruchu_s"] = round(time.time() - t0, 1)

    vols = np.array([vol(parts[k]) for k in HEAD_ALL])
    coms = np.array([[parts[k].Center().x, parts[k].Center().y, parts[k].Center().z] for k in HEAD_ALL])
    com = (coms * vols[:, None]).sum(0) / vols.sum()
    res["glowa"] = {"masa_g_pelne": round(vols.sum() / 1000 * DENSITY_PLA),
                    "srodek_masy_mm": [round(float(c), 1) for c in com],
                    "os_tilt_mm": list(P.TILT_AXIS)}
    return res


def export(parts):
    os.makedirs(OUT, exist_ok=True)
    for k, s in parts.items():
        s.exportStl(os.path.join(OUT, f"{k}.stl"), 0.1, 0.2)
        s.exportStep(os.path.join(OUT, f"{k}.step"))


def stl_tmp(shape, name):
    os.makedirs(TMP, exist_ok=True)
    path = os.path.join(TMP, name + ".stl")
    shape.exportStl(path, 0.15, 0.3)
    return path


COL = {"M1_srodek": (0.50, 0.53, 0.57, 1), "M2_twarz": (0.60, 0.63, 0.67, 1), "M8_tyl": (0.44, 0.47, 0.51, 1),
       "M3_szczeka": (0.68, 0.71, 0.75, 1), "M7_oko_L": (0.9, 0.1, 0.1, 1), "M7_oko_P": (0.9, 0.1, 0.1, 1),
       "M5_jarzmo": (0.25, 0.4, 0.62, 1), "M6_podstawa": (0.2, 0.32, 0.5, 1)}


def previews(parts, env):
    from .mjrender import render_scene

    full = [(os.path.join(OUT, f"{k}.stl"), COL[k]) for k in parts]
    views = {"przod": (180, -8), "bok": (90, -8), "trzy_czwarte": (140, -18), "tyl": (0, -12), "gora": (150, -70)}
    for name, (az, el) in views.items():
        render_scene(full, f"podglad_{name}.png", OUT, azimuth=az, elevation=el, distance=0.62, lookat=(0.0, 0, -0.02))

    off = {"M2_twarz": (60, 0, 0), "M8_tyl": (-60, 0, 0), "M3_szczeka": (0, 0, -45), "M7_oko_L": (110, 0, 0),
           "M7_oko_P": (110, 0, 0)}
    expl = [(stl_tmp(parts[k].translate(cq.Vector(*off.get(k, (0, 0, 0)))), f"ex_{k}"), COL[k]) for k in HEAD_ALL]
    render_scene(expl, "podglad_rozstrzelony.png", OUT, azimuth=130, elevation=-18, distance=1.1,
                 lookat=(0.0, 0, -0.04))

    # przekrój środkowy: odcinam połowę y>0, widok od strony cięcia
    half = box(-BIG, BIG, -BIG, 0, -BIG, BIG)
    sec = [(stl_tmp(parts[k].intersect(half), f"sec_{k}"), COL[k]) for k in HEAD_SHELLS + ("M3_szczeka",)]
    sec.append((stl_tmp(env["raspberry_pi5"].intersect(half), "sec_pi"), (0.1, 0.65, 0.5, 1)))
    sec.append((stl_tmp(env["kamera"].intersect(half), "sec_cam"), (0.95, 0.75, 0.2, 1)))
    render_scene(sec, "podglad_przekroj.png", OUT, azimuth=180 + 90, elevation=-4, distance=0.85,
                 lookat=(0.0, 0, -0.03))


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    parts, env = build_all()
    t1 = time.time()
    export(parts)
    res = checks(parts, env)
    res["czas_budowy_s"] = round(t1 - t0, 1)
    with open(os.path.join(OUT, "raport.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    previews(parts, env)
    res["czas_calkowity_s"] = round(time.time() - t0, 1)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
