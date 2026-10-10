"""Szyja: M5 (jarzmo pochylenia) i M6 (obrót + podstawa) oraz obwiednie podzespołów (nie do druku)."""
from . import params as P
from .geom import box, cyl, fuse
from .skull import CAM_Z

TX, _, TZ = P.TILT_AXIS
ARM_IN, ARM_T = 81.5, 8.0          # wewnętrzna płaszczyzna ramienia jarzma i jego grubość
Z_CROSS = -195.0                   # góra poprzeczki


def build_yoke():
    """M5: dwa ramiona + poprzeczka (drukowane na leżąco, jedna część)."""
    arms = [box(TX - 18, TX + 18, *sorted((sg * ARM_IN, sg * (ARM_IN + ARM_T))), Z_CROSS - 12, TZ + 24) for sg in (-1, 1)]
    cross = box(TX - 18, TX + 18, -(ARM_IN + ARM_T), ARM_IN + ARM_T, Z_CROSS - 12, Z_CROSS)
    return fuse(arms + [cross])


def build_base():
    """M6: kolumna pod poprzeczką, talerz obrotu i ciężka podstawa Ø150."""
    column = box(TX - 16, TX + 16, -16, 16, Z_CROSS - 30, Z_CROSS - 12)
    plate = cyl(40, (TX, 0, Z_CROSS - 38), (TX, 0, Z_CROSS - 30))
    stem = cyl(30, (TX, 0, Z_CROSS - 48), (TX, 0, Z_CROSS - 38))
    base = cyl(75, (TX, 0, Z_CROSS - 62), (TX, 0, Z_CROSS - 48))
    return fuse([column, plate, stem, base])


def servo_envelopes():
    """Obwiednie: serwo tilt (na zewnątrz ramienia), serwo pan, Pi 5, kamera. Nie do druku."""
    tilt = box(TX - 22, TX + 22, ARM_IN + ARM_T, ARM_IN + ARM_T + 25, TZ - 18, TZ + 18)
    pan = box(TX - 22, TX + 22, -12, 12, Z_CROSS - 48, Z_CROSS - 13)
    pi = box(-67.5, 17.5, -28, 28, -31, -6)
    cam = box(50, 62, -12.5, 12.5, CAM_Z - 12, CAM_Z + 12)
    return {"serwo_tilt": tilt, "serwo_pan": pan, "raspberry_pi5": pi, "kamera": cam}
