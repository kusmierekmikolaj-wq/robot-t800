"""Pomocnicze bryły CadQuery: elipsoidy, walce, prostopadłościany, operacje na kształtach."""
import math

import cadquery as cq

V = cq.Vector
BIG = 1000.0


def ell(c, semi):
    """Elipsoida o środku c i półosiach semi=(a, b, c) wzdłuż X, Y, Z."""
    s = cq.Solid.makeSphere(1.0, V(0, 0, 0), V(0, 0, 1), -90, 90, 360)
    s = s.transformGeometry(cq.Matrix([[semi[0], 0, 0, 0], [0, semi[1], 0, 0], [0, 0, semi[2], 0]]))
    return s.translate(V(*c))


def grow(spec, d):
    """Elipsoida o półosiach powiększonych (d>0) lub zmniejszonych (d<0) o d."""
    c, semi = spec
    return ell(c, tuple(max(1.0, s + d) for s in semi))


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(r, p0, p1):
    """Walec o promieniu r od punktu p0 do p1."""
    d = V(*p1) - V(*p0)
    return cq.Solid.makeCylinder(r, d.Length, V(*p0), d.normalized())


def fuse(parts):
    parts = list(parts)
    return parts[0].fuse(*parts[1:]).clean() if len(parts) > 1 else parts[0]


def cut(a, parts):
    parts = list(parts)
    return a.cut(*parts).clean() if parts else a


def xrange_box(x0=-BIG, x1=BIG):
    return box(x0, x1, -BIG, BIG, -BIG, BIG)


def rot_y(shape, angle_deg, pivot):
    """Obrót wokół osi równoległej do Y przez punkt pivot. Dodatni kąt: przód (+X) idzie w dół."""
    p = V(*pivot)
    return shape.rotate(p, p + V(0, 1, 0), angle_deg)


def polar_xy(cx, cy, rx, ry, deg):
    t = math.radians(deg)
    return cx + rx * math.cos(t), cy + ry * math.sin(t)
