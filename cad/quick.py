"""Szybki podgląd bez pełnych kontroli: python -m cad.quick  (kilkanaście sekund)."""
import os
import time

from . import build, neck


def main():
    t0 = time.time()
    parts, env = build.build_all()
    os.makedirs(build.OUT, exist_ok=True)
    build.export(parts)
    for k, s in parts.items():
        bb = s.BoundingBox()
        print(f"{k:12s} bryl={len(s.Solids())} poprawna={s.isValid()} obj={s.Volume() / 1000:7.1f} cm3 "
              f"wym=({bb.xlen:.0f},{bb.ylen:.0f},{bb.zlen:.0f})")
    print("budowa", round(time.time() - t0, 1), "s")
    from .mjrender import render_scene
    full = [(os.path.join(build.OUT, f"{k}.stl"), build.COL[k]) for k in parts if not k.startswith(("M5", "M6"))]
    for name, (az, el, dist) in {"przod": (180, -6, 0.55), "trzy_czwarte": (145, -14, 0.55), "bok": (90, -4, 0.6)}.items():
        render_scene(full, f"v2_{name}.png", build.OUT, azimuth=az, elevation=el, distance=dist,
                     lookat=(0.0, 0, -0.02))
    print("render", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
