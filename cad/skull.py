"""Czaszka v3 (styl endoszkieletu T-800). Moduły: M1 środek, M2 twarz, M8 tył, M3 szczęka, M7 oczy.

Układ współrzędnych (mm): +X do przodu, +Y w lewo, +Z w górę. Głowa ma ok. 238 mm wysokości
(korona z=+100, podbródek z=-138 z szczęką), ok. 140 mm szerokości i ok. 210 mm głębokości.
Kształt zewnętrzny powstaje przez wyciągnięcie (loft) przez zaokrąglone przekroje na kolejnych wysokościach;
wnętrze to ten sam loft pomniejszony o grubość ściany T. Proporcje i cechy (skośne czoło, brew, głębokie
oczodoły, szczelina nosa, rzędy zębów, tłoki, tarcza na skroni) wzorowane na zdjęciach referencyjnych;
wymiary to moje przybliżenia z fotografii, nie pomiary oryginału.
"""
import math

import cadquery as cq

from . import params as P
from .geom import BIG, V, box, cut, cyl, ell, fuse, xrange_box

T = P.T

# przekroje: (z, x_tyl, x_przod, pół-szerokość y, wykładnik superelipsy: większy = bardziej prostokątny)
SECTIONS = [
    (100.0, -28.0, 33.0, 22.0, 2.6),
    (92.0, -65.0, 55.0, 48.0, 3.2),
    (75.0, -98.0, 70.0, 63.0, 3.4),
    (50.0, -108.0, 82.0, 69.0, 3.6),
    (25.0, -110.0, 94.0, 70.0, 3.8),
    (0.0, -108.0, 100.0, 68.0, 4.0),
    (-30.0, -95.0, 100.0, 65.0, 4.0),
    (-45.0, -40.0, 100.0, 63.0, 4.0),
    (-70.0, 30.0, 98.0, 57.0, 4.0),
    (-80.0, 30.0, 97.0, 53.0, 4.0),
]
Z_FACE_BOTTOM = -80.0                                 # dół szczęki górnej (od niego wiszą zęby górne)
X_MOUTH = 88.0                                        # przód dolnej części twarzy w zagłębieniu ust
EYE_Y, EYE_Z = 35.0, -9.0
CAM_Z = -12.0
TOOTH_Y = [(i - 4) * 7.4 for i in range(9)]
BROW_Z = (8.0, 32.0)
BROW_OFFSET = 7.0
N_PTS = 40


def rbox(x0, x1, y0, y1, z0, z1, r):
    r = min(r, (x1 - x0) / 2 - 0.01, (y1 - y0) / 2 - 0.01, (z1 - z0) / 2 - 0.01)
    w = cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
    return (w.edges().fillet(r) if r > 0.2 else w).val()


def _wire(z, xb, xf, hw, n):
    cx, a, b = (xb + xf) / 2, (xf - xb) / 2, hw
    pts = []
    for i in range(N_PTS):
        t = 2 * math.pi * i / N_PTS
        c, s = math.cos(t), math.sin(t)
        pts.append(V(cx + a * math.copysign(abs(c) ** (2 / n), c), b * math.copysign(abs(s) ** (2 / n), s), z))
    return cq.Wire.assembleEdges([cq.Edge.makeSpline(pts, periodic=True)])


def envelope(d=0.0):
    """Loft przez przekroje; d>0 pomniejsza (wnętrze skorupy)."""
    wires = [_wire(z, xb + d, xf - d, hw - d, n) for z, xb, xf, hw, n in SECTIONS]
    solid = cq.Solid.makeLoft(wires, False)
    if d:
        solid = solid.intersect(box(-BIG, BIG, -BIG, BIG, Z_FACE_BOTTOM + d, 100.0 - d))
    return solid


def brow(d=0.0):
    """Pas nadoczodołowy: obrys głowy powiększony o BROW_OFFSET, wycięty w pasie z=8..32 od x=45 do przodu."""
    return envelope(-(BROW_OFFSET - d)).intersect(box(45 + d, BIG, -BIG, BIG, BROW_Z[0] + d, BROW_Z[1] - d))


def socket(sg, d=0.0):
    """Prostokątny oczodół z lekkim przechyłem (zewnętrzny kraniec wyżej). d>0: powiększony (obwiednia ścianki)."""
    ya, yb = sorted((sg * 12.0, sg * 58.0))
    s = rbox(66 - d, 125, ya - d, yb + d, -24 - d, 6 + d, 10 + d)
    return s.rotate(V(0, sg * 35, EYE_Z), V(1, sg * 35, EYE_Z), sg * 8.0)


def nose(d=0.0):
    return rbox(80 - d, 125, -6 - d, 6 + d, -84 - d, -4 + d, 5 + d)


def mouth(d=0.0):
    return rbox(X_MOUTH - d, 125, -42 - d, 42 + d, Z_FACE_BOTTOM - 1 - d, -58 + d, 8 + d)


def _cavity():
    cav = fuse([envelope(T), brow(T)])
    return cut(cav, [socket(1, T), socket(-1, T), nose(T), mouth(T)])


def _boss_spots(outer, xp, rb=5.5):
    """Środki słupków przy płaszczyźnie x=xp: ray casting od środka przekroju do ścianki, z wnikaniem w nią o 1 mm."""
    zs = [z for z in range(-140, 121) if outer.isInside(V(xp, 0, z))]
    zc = (zs[0] + zs[-1]) / 2.0
    spots = []
    for ang in (20, 70, 110, 160, 200, 340):
        dy, dz = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        r = 0.0
        while outer.isInside(V(xp, r * dy, zc + r * dz)) and r < 200:
            r += 0.5
        spots.append((round((r - T - rb + 2.0) * dy, 2), round(zc + (r - T - rb + 2.0) * dz, 2)))
    return spots


def _bosses(xp, outer, front, spots, rb=5.5):
    """Słupki M3 wzdłuż X przy płaszczyźnie podziału. front=+1: wkładki (część o większym x), -1: otwory przelotowe."""
    parts, holes = [], []
    for y, z in spots:
        x0, x1 = (xp, xp + 12) if front > 0 else (xp - 12, xp)
        parts.append(cyl(rb, (x0, y, z), (x1, y, z)).intersect(outer))
        if front > 0:
            holes.append(cyl(P.D_INSERT / 2, (xp - 0.01, y, z), (xp + 9, y, z)))
        else:
            holes.append(cyl(P.D_CLEAR / 2, (xp - 13, y, z), (xp + 0.01, y, z)))
    return parts, holes


def _tooth_row(z0, z1, x_c):
    row = []
    for y in TOOTH_Y:
        x = x_c - y * y / 280.0
        t = rbox(-4.2, 4.2, -3.3, 3.3, z0, z1, 1.3)
        t = t.rotate(V(0, 0, 0), V(0, 0, 1), math.degrees(-y / 140.0)).translate(V(x, y, 0))
        row.append(t)
    return row


def build_head():
    outer = fuse([envelope(), brow()])
    solid = cut(outer, [socket(1), socket(-1), nose(), mouth()])
    shell = cut(solid, [_cavity()])

    eye_holes = [cyl(8.2, (50, sg * EYE_Y, EYE_Z), (80, sg * EYE_Y, EYE_Z)) for sg in (-1, 1)]
    cam_hole = cyl(5.2, (50, 0, CAM_Z), (83, 0, CAM_Z))

    parts, holes = [], []
    for xp in (P.X_FACE, P.X_REAR):
        spots = _boss_spots(outer, xp)
        for front in (+1, -1):
            b, h = _bosses(xp, outer, front, spots)
            parts += b
            holes += h

    # tarcze osi pochylenia po bokach czaszki (jak okrągły mechanizm na skroni oryginału)
    tx, _, tz = P.TILT_AXIS
    for sg in (-1, 1):
        parts.append(cyl(30, (tx, sg * 50, tz), (tx, sg * P.PAD_Y, tz)))
        holes.append(cyl(4, (tx, sg * 50, tz), (tx, sg * (P.PAD_Y + 0.1), tz)))
        for k in range(4):
            a = math.radians(45 + 90 * k)
            px, pz = tx + 18 * math.cos(a), tz + 18 * math.sin(a)
            holes.append(cyl(P.D_INSERT / 2, (px, sg * (P.PAD_Y - 10), pz), (px, sg * (P.PAD_Y + 0.1), pz)))
        holes.append(cut(cyl(25, (tx, sg * (P.PAD_Y - 2), tz), (tx, sg * (P.PAD_Y + 0.1), tz)),
                         [cyl(22, (tx, sg * (P.PAD_Y - 2.1), tz), (tx, sg * (P.PAD_Y + 0.2), tz))]))

    # uszy zawiasu szczęki i tłoki hydrauliczne z przodu policzków (M2)
    jx, _, jz = P.JAW_PIVOT
    for sg in (-1, 1):
        parts.append(cyl(9, (jx, sg * 46, jz), (jx, sg * 67, jz)))
        holes.append(cyl(P.D_INSERT / 2, (jx, sg * 56, jz), (jx, sg * 67.1, jz)))
        parts.append(cyl(5.5, (101, sg * 52, -50), (101, sg * 52, -76)))            # tuleja tłoka
        parts.append(cyl(3.25, (101, sg * 52, -76), (101, sg * 52, -112)))          # tłoczysko

    parts += _tooth_row(-92.0, Z_FACE_BOTTOM + 0.5, 88.0)        # zęby górne
    shell = fuse([shell] + parts)
    grille = [cyl(1.6, (-72, y, z), (-130, y, z)) for y in (-16, -8, 0, 8, 16) for z in (30, 38, 46, 54, 62)]
    shell = cut(shell, eye_holes + [cam_hole] + holes + grille)

    m2 = shell.intersect(xrange_box(P.X_FACE, BIG))
    m1 = shell.intersect(xrange_box(P.X_REAR, P.X_FACE))
    m8 = shell.intersect(xrange_box(-BIG, P.X_REAR))
    return {"M1_srodek": m1, "M2_twarz": m2, "M8_tyl": m8}


def build_jaw():
    """Szczęka: trapezowa płyta z kieszenią, rząd zębów, belki boczne i ramiona z otworami zawiasu."""
    z0, z1 = -138.0, -105.0
    pts = [(40, -44), (40, 44), (74, 47), (92, 32), (94, 12), (94, -12), (92, -32), (74, -47)]
    plate = cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)
    pocket = cq.Workplane("XY").workplane(offset=z0 + 4).polyline(pts).close().offset2D(-9).extrude(z1 - z0)
    parts = [plate.cut(pocket).val()]
    jx, _, jz = P.JAW_PIVOT
    for sg in (-1, 1):
        ya, yb = sorted((sg * 42.0, sg * 72.0))
        yc, yd = sorted((sg * 67.0, sg * 72.0))
        parts.append(box(jx - 11, jx + 11, ya, yb, z0, z1))                  # belka boczna
        parts.append(box(jx - 11, jx + 11, yc, yd, z0, jz))                  # ramię
        parts.append(cyl(9, (jx, yc, jz), (jx, yd, jz)))
    jaw = cut(fuse(parts), [cyl(P.D_CLEAR / 2 + 0.1, (jx, sg * 66, jz), (jx, sg * 73, jz)) for sg in (-1, 1)])
    return fuse([jaw] + _tooth_row(z1 - 1.0, -92.5, 88.0))


def build_eyes():
    """Wkładki oczu: kołnierz Ø26 od przodu, korpus Ø16 przez dno oczodołu, soczewka-kopułka, 4 kołki."""
    eyes = []
    for sg in (-1, 1):
        y = sg * EYE_Y
        bezel = cut(cyl(13, (66.2, y, EYE_Z), (69.5, y, EYE_Z)), [cyl(8.6, (66.0, y, EYE_Z), (70.0, y, EYE_Z))])
        body_ = cyl(8.0, (56, y, EYE_Z), (69.0, y, EYE_Z))
        lens = ell((69.0, y, EYE_Z), (4.0, 7.6, 7.6)).intersect(box(69.0, BIG, -BIG, BIG, -BIG, BIG))
        pegs = [cyl(1.6, (66.2, y + 11.5 * math.cos(a), EYE_Z + 11.5 * math.sin(a)),
                    (71.0, y + 11.5 * math.cos(a), EYE_Z + 11.5 * math.sin(a))) for a in (0.8, 2.4, 3.9, 5.5)]
        eyes.append(fuse([bezel, body_, lens] + pegs))
    return eyes
