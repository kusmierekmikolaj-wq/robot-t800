"""Składanie pociętej czaszki T-800 z płaszczyzn cięcia (dane nieufne: tylko siatki STL).

python -I reassemble.py <folder_stl> <folder_wyj>
Wynik: transformacje.json (macierze 4x4 dla każdej części), czaszka_zlozona.stl, podgląd PNG.
"""
import json
import os
import sys

import numpy as np
import trimesh
from scipy.spatial import cKDTree

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
PIECES = {
    "A_A": "obj_19_Skull_001.stl_A_A.stl", "A_B": "obj_25_Skull_001.stl_A_B.stl",
    "B_A_A": "obj_11_Skull_001.stl_B_A_A.stl", "B_A_B": "obj_9_Skull_001.stl_B_A_B.stl",
    "B_B_A": "obj_7_Skull_001.stl_B_B_A.stl", "B_B_B": "obj_13_Skull_001.stl_B_B_B.stl",
}
MESH = {k: trimesh.load(os.path.join(SRC, f), force="mesh") for k, f in PIECES.items()}
RNG = np.random.default_rng(0)


def facets_world(name, T, min_area=150.0):
    m = MESH[name]
    R, t = T[:3, :3], T[:3, 3]
    out = []
    for i, f in enumerate(m.facets):
        a = m.area_faces[f].sum()
        if a < min_area:
            continue
        n = R @ m.facets_normal[i]
        c = (R @ m.triangles_center[f].T).T.mean(0) + t
        out.append({"mesh": name, "faces": f, "n": n, "d": float(n @ c), "area": float(a)})
    return out


def clusters(group):
    """Grupuje płaskie fragmenty wszystkich części grupy według płaszczyzny (kierunek normalnej ma znaczenie)."""
    items = []
    for name, T in group.items():
        items += facets_world(name, T)
    cl = []
    for it in items:
        for c in cl:
            if np.dot(c["n"], it["n"]) > 0.999 and abs(c["d"] - it["d"]) < 1.0:
                c["parts"].append(it)
                c["area"] += it["area"]
                break
        else:
            cl.append({"n": it["n"], "d": it["d"], "area": it["area"], "parts": [it]})
    # odrzuć płaszczyzny wewnętrzne (już sklejone styki: ta sama płaszczyzna z przeciwną normalną)
    ext = [c for c in cl if not any(np.dot(c["n"], o["n"]) < -0.999 and abs(c["d"] + o["d"]) < 1.0 for o in cl)]
    return sorted(ext, key=lambda c: -c["area"])


def sample_cluster(c, group, n=2500):
    pts = []
    for it in c["parts"]:
        m = MESH[it["mesh"]]
        sub = m.submesh([it["faces"]], append=True)
        k = max(50, int(n * it["area"] / c["area"]))
        p, _ = trimesh.sample.sample_surface_even(sub, k, seed=1) if hasattr(trimesh.sample, "sample_surface_even") else trimesh.sample.sample_surface(sub, k)
        T = group[it["mesh"]]
        pts.append((T[:3, :3] @ p.T).T + T[:3, 3])
    return np.vstack(pts)


def frame(n):
    a = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(n, a)
    u /= np.linalg.norm(u)
    return u, np.cross(n, u)


def align_clusters(cP, gP, cQ, gQ):
    """Transformacja dla grupy Q, by jej płaszczyzna cQ legła na cP (normalne przeciwne). Zwraca (T, błąd_mm)."""
    pP = sample_cluster(cP, gP)
    pQ = sample_cluster(cQ, gQ)
    R1 = trimesh.geometry.align_vectors(cQ["n"], -cP["n"])
    pQ1 = (R1[:3, :3] @ pQ.T).T
    u, v = frame(cP["n"])
    P2 = np.c_[pP @ u, pP @ v]
    Q2 = np.c_[pQ1 @ u, pQ1 @ v]
    cp, cq = P2.mean(0), Q2.mean(0)
    tree = cKDTree(P2)
    sub = Q2[RNG.choice(len(Q2), min(700, len(Q2)), replace=False)] - cq

    def score(th):
        c, s = np.cos(th), np.sin(th)
        q = sub @ np.array([[c, s], [-s, c]]) + cp
        return tree.query(q)[0].mean()

    ths = np.radians(np.arange(0, 360, 1.0))
    sc = np.array([score(t) for t in ths])
    best = ths[sc.argmin()]
    for step in (0.2, 0.04, 0.008):
        cand = best + np.radians(np.arange(-5, 5.01, 1) * step)
        best = cand[np.argmin([score(t) for t in cand])]
    err = score(best)
    # złóż transformację 3D: R1, obrót wokół normalnej P o kąt best, przesunięcie w płaszczyźnie i wzdłuż normalnej
    c, s = np.cos(best), np.sin(best)
    R2d = np.array([[c, s], [-s, c]])                 # działa na wektory wierszowe: q @ R2d
    B = np.c_[u, v, cP["n"]]                           # baza P (kolumny)
    Rin = B @ np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]]) @ B.T
    # sprawdzenie zgodności konwencji: q @ R2d == (Rin @ q3)
    R = Rin @ R1[:3, :3]
    q_c3 = R1[:3, :3] @ pQ.mean(0)
    target_inplane = cp[0] * u + cp[1] * v
    moved_c = Rin @ q_c3
    t = target_inplane - (moved_c @ u) * u - (moved_c @ v) * v
    t += (cP["d"] - (moved_c @ cP["n"])) * cP["n"]
    T = np.eye(4)
    T[:3, :3], T[:3, 3] = R, t
    # błąd 3D po transformacji
    q3 = (R @ pQ.T).T + t
    err3 = cKDTree(pP).query(q3[RNG.choice(len(q3), min(800, len(q3)), replace=False)])[0].mean()
    if err3 > err * 3 + 0.3:      # gdyby konwencja obrotu była odwrotna, spróbuj kąta przeciwnego
        c, s = np.cos(-best), np.sin(-best)
        Rin = B @ np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]]) @ B.T
        R = Rin @ R1[:3, :3]
        moved_c = Rin @ q_c3
        t = target_inplane - (moved_c @ u) * u - (moved_c @ v) * v
        t += (cP["d"] - (moved_c @ cP["n"])) * cP["n"]
        T[:3, :3], T[:3, 3] = R, t
        q3 = (R @ pQ.T).T + t
        err3 = cKDTree(pP).query(q3[RNG.choice(len(q3), min(800, len(q3)), replace=False)])[0].mean()
    return T, float(err3)


def rot_axis(axis, ang):
    return trimesh.transformations.rotation_matrix(ang, axis)[:3, :3]


def align_y(cP, gP, cQ, gQ):
    """Jak align_clusters, ale obrót zachowuje oś Y (cięcia są równoległe do Y). 2 warianty odbicia,
    w płaszczyźnie tylko przesunięcie (ICP z odrzuceniem 15% najgorszych par)."""
    nP, nQ = cP["n"].copy(), cQ["n"].copy()
    nP[1] = nQ[1] = 0.0
    nP /= np.linalg.norm(nP)
    nQ /= np.linalg.norm(nQ)
    tgt = -nP
    phi = np.arctan2(nQ[2], nQ[0]) - np.arctan2(tgt[2], tgt[0])       # obrót wokół Y: x,z
    Ra = rot_axis([0, 1, 0], phi)
    if np.linalg.norm(Ra @ nQ - tgt) > 1e-6:
        Ra = rot_axis([0, 1, 0], -phi)
    pP, pQ = sample_cluster(cP, gP), sample_cluster(cQ, gQ)
    u = np.array([0.0, 1.0, 0.0])
    w = np.cross(nP, u)
    P2 = np.c_[pP @ u, pP @ w]
    tree = cKDTree(P2)
    best = None
    for R in (Ra, rot_axis(nP, np.pi) @ Ra):
        q = (R @ pQ.T).T
        Q2 = np.c_[q @ u, q @ w]
        t2 = P2.mean(0) - Q2.mean(0)
        for _ in range(80):
            d, idx = tree.query(Q2 + t2)
            keep = d <= np.percentile(d, 85)
            step = (P2[idx[keep]] - (Q2 + t2)[keep]).mean(0)
            t2 += step
            if np.linalg.norm(step) < 1e-4:
                break
        d, _ = tree.query(Q2 + t2)
        err = float(np.sort(d)[: int(0.85 * len(d))].mean())
        tn = cP["d"] - float((q @ nP).mean())
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = t2[0] * u + t2[1] * w + tn * nP
        if best is None or err < best[1]:
            best = (T, err)
    return best


def join(gP, gQ, label):
    cps, cqs = clusters(gP), clusters(gQ)
    for nm, cs in (("P", cps), ("Q", cqs)):
        print(f"  {label} {nm}: " + ", ".join(f"{c['area']:.0f}@{np.round(c['n'], 2).tolist()}/{len(c['parts'])}" for c in cs[:8]))
    best = None
    for cP in cps[:8]:
        for cQ in cqs[:8]:
            if cP["area"] < 800 or abs(cP["area"] - cQ["area"]) / max(cP["area"], cQ["area"]) > 0.15:
                continue
            if abs(cP["n"][1]) > 0.05 or abs(cQ["n"][1]) > 0.05:
                continue                              # płaszczyzny cięcia są równoległe do osi Y
            T, e = align_y(cP, gP, cQ, gQ)
            print(f"  {label}: pola {cP['area']:.0f}/{cQ['area']:.0f}  blad {e:.3f} mm")
            if best is None or e < best[1]:
                best = (T, e)
    T, e = best
    out = dict(gP)
    for k, Tq in gQ.items():
        out[k] = T @ Tq
    print(f"=> {label}: wybrany blad {e:.3f} mm")
    return out, e


I = np.eye(4)
errs = {}
gA, errs["A"] = join({"A_A": I}, {"A_B": I}, "A_A+A_B")
gBA, errs["B_A"] = join({"B_A_A": I}, {"B_A_B": I}, "B_A_A+B_A_B")
gBB, errs["B_B"] = join({"B_B_A": I}, {"B_B_B": I}, "B_B_A+B_B_B")
gB, errs["B"] = join(gBA, gBB, "B_A+B_B")
g, errs["A+B"] = join(gA, gB, "A+B")

json.dump({"czesci": PIECES, "T": {k: v.tolist() for k, v in g.items()}, "bledy_mm": errs},
          open(os.path.join(OUT, "transformacje.json"), "w", encoding="utf-8"), indent=1)
parts = []
for k, T in g.items():
    m = MESH[k].copy()
    m.apply_transform(T)
    m.export(os.path.join(OUT, f"zl_{k}.stl"))
    parts.append(m)
whole = trimesh.util.concatenate(parts)
whole.export(os.path.join(OUT, "czaszka_zlozona.stl"))
print("wymiary zlozonej:", np.round(whole.extents, 1), "bledy:", {k: round(v, 3) for k, v in errs.items()})

sys.path.insert(0, r"C:\Users\Jeff\Documents\druk3d-robot\robot")
from cad.mjrender import render_scene  # noqa: E402

cols = [(0.62, 0.65, 0.7, 1), (0.5, 0.55, 0.62, 1), (0.7, 0.6, 0.5, 1), (0.55, 0.65, 0.55, 1), (0.6, 0.55, 0.7, 1), (0.7, 0.7, 0.55, 1)]
items = [(os.path.join(OUT, f"zl_{k}.stl"), cols[i]) for i, k in enumerate(g)]
ctr = tuple((whole.bounds.mean(0) / 1000).tolist())
dist = float(whole.extents.max()) / 1000 * 2.6
for nm, az, el in (("zl_a", 0, -15), ("zl_b", 90, -15), ("zl_c", 180, -15), ("zl_d", 270, -15), ("zl_gora", 0, -80)):
    render_scene(items, nm + ".png", OUT, azimuth=az, elevation=el, distance=dist, lookat=ctr)
print("ok")
