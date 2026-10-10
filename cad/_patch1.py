p = "cad/skull.py"
s = open(p, encoding="utf-8").read()
rep = [
    ("lugs.append(cyl(8, (jx, sg * 33, jz), (jx, sg * 44, jz)))", "lugs.append(cyl(8, (jx, sg * 33, jz), (jx, sg * 47.5, jz)))"),
    ("lug_holes.append(cyl(P.D_INSERT / 2, (jx, sg * 32, jz), (jx, sg * 44.1, jz)))", "lug_holes.append(cyl(P.D_INSERT / 2, (jx, sg * 32, jz), (jx, sg * 47.6, jz)))"),
    ("ya, yb = sorted((sg * 38.0, sg * 49.5))\n        yc, yd = sorted((sg * 44.5, sg * 49.5))", "ya, yb = sorted((sg * 38.0, sg * 53.0))\n        yc, yd = sorted((sg * 48.0, sg * 53.0))"),
    ("boss = cyl(11, (jx, yc, jz), (jx, yd, jz))", "boss = cyl(8, (jx, yc, jz), (jx, yd, jz))"),
    ("cyl(P.D_CLEAR / 2 + 0.1, (jx, sg * 43, jz), (jx, sg * 50.5, jz))", "cyl(P.D_CLEAR / 2 + 0.1, (jx, sg * 47, jz), (jx, sg * 54, jz))"),
]
for a, b in rep:
    assert a in s, a
    s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("patched")
