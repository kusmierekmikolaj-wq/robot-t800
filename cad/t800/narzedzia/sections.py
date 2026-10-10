"""Przekroje złożonej czaszki z obrysami podzespołów. python -I sections.py <zlozona>"""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402

D = sys.argv[1]
sk = trimesh.load(os.path.join(D, "czaszka_ustawiona.stl"), force="mesh")
jw = trimesh.load(os.path.join(D, "szczeka_ustawiona.stl"), force="mesh")
print("czaszka bounds", np.round(sk.bounds, 1).tolist(), "\nszczeka bounds", np.round(jw.bounds, 1).tolist())


def draw_section(ax, mesh, origin, normal, axes, color):
    sec = mesh.section(plane_origin=origin, plane_normal=normal)
    if sec is None:
        return
    for loop in sec.discrete:
        p = np.asarray(loop)
        ax.plot(p[:, axes[0]], p[:, axes[1]], color=color, lw=0.8)


def rect(ax, x0, x1, y0, y1, color, label):
    ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec=color, lw=1.6))
    ax.text(x0, y1 + 1, label, color=color, fontsize=7)


fig, axs = plt.subplots(2, 3, figsize=(18, 12))
# przekrój strzałkowy (y = środek symetrii)
ax = axs[0, 0]
ys = (sk.bounds[0][1] + sk.bounds[1][1]) / 2
draw_section(ax, sk, [0, ys, 0], [0, 1, 0], (0, 2), "k")
draw_section(ax, jw, [0, ys, 0], [0, 1, 0], (0, 2), "tab:orange")
ax.set_title(f"przekroj strzalkowy y={ys:.1f} (x przod, z gora)")
# poziome
for i, z in enumerate((-50, -30, -10, 10, 30)):
    ax = axs.flat[i + 1]
    draw_section(ax, sk, [0, 0, z], [0, 0, 1], (0, 1), "k")
    draw_section(ax, jw, [0, 0, z], [0, 0, 1], (0, 1), "tab:orange")
    ax.set_title(f"przekroj poziomy z={z} (x przod, y bok)")
for ax in axs.flat:
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
fig.savefig(os.path.join(D, "przekroje.png"), dpi=80, bbox_inches="tight")
print("ok")
