"""Parametry głowy (mm). Zmiana S skaluje całą czaszkę; reszta to wartości 'surowe' razy S."""
S = 1.15            # skala względem czaszki dorosłego
T = 3.0             # grubość ściany skorupy [mm]
TOL_SLIDE = 0.2     # luz ślizgowy (wartość startowa, do kalibracji planszą testową)
D_INSERT = 4.2      # otwór pod wkładkę gwintowaną M3 [mm]
D_CLEAR = 3.4       # otwór przelotowy pod śrubę M3 [mm]

# zakresy ruchu, takie same jak w brain/safety.py
PAN = (-90.0, 90.0)
TILT = (-30.0, 40.0)
JAW_MAX = 20.0

# płaszczyzny podziału (x) czaszki: M2 twarz | M1 środek | M8 tył
X_FACE = 30.0
X_REAR = -70.0

# oś pochylenia (tilt) i zawias szczęki
TILT_AXIS = (-30.0, 0.0, 10.0)            # (x, y, z), oś równoległa do Y
JAW_PIVOT = (45.0, 0.0, -70.0)
PAD_Y = 80.0                             # zewnętrzna płaszczyzna tarczy osi pochylenia
