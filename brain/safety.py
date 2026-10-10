"""Nadzorca bezpieczeństwa: waliduje każde polecenie, zanim trafi do robota.

Zasada: mózg (Claude) proponuje, nadzorca wykonuje tylko to, co bezpieczne.
Claude może zatrzymać robota (e-stop), ale odblokować go może wyłącznie człowiek.
"""
from dataclasses import dataclass


class SafetyError(Exception):
    """Polecenie odrzucone przez nadzorcę (komunikat po polsku, trafia do Claude)."""


@dataclass(frozen=True)
class Limits:
    pan_deg: tuple = (-90.0, 90.0)
    tilt_deg: tuple = (-30.0, 40.0)
    max_step_deg: float = 60.0
    max_say_chars: int = 300
    eye_colors: tuple = ("off", "red", "amber", "blue")


class Supervisor:
    def __init__(self, limits: Limits | None = None):
        self.limits = limits or Limits()
        self._estop = False
        self.log: list[tuple[str, str]] = []

    @property
    def estop(self) -> bool:
        return self._estop

    def trigger_estop(self, reason: str) -> None:
        self._estop = True
        self.log.append(("estop", reason))

    def release_estop(self, human_confirmation: bool) -> None:
        """Odblokowanie wymaga potwierdzenia człowieka (nie wywołuje tego Claude)."""
        if not human_confirmation:
            raise SafetyError("Odblokowanie e-stop wymaga potwierdzenia człowieka.")
        self._estop = False
        self.log.append(("estop_release", "human"))

    def check_say(self, text: str) -> str:
        if not isinstance(text, str) or not text.strip():
            raise SafetyError("Tekst do wypowiedzenia jest pusty.")
        if len(text) > self.limits.max_say_chars:
            raise SafetyError(f"Tekst za długi (max {self.limits.max_say_chars} znaków).")
        return text.strip()

    def check_look(self, pan: float, tilt: float, cur_pan: float, cur_tilt: float) -> tuple[float, float]:
        if self._estop:
            raise SafetyError("E-stop aktywny: ruch zablokowany.")
        for name, value in (("pan", pan), ("tilt", tilt)):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise SafetyError(f"Parametr {name} musi być liczbą.")
        lo, hi = self.limits.pan_deg
        if not lo <= pan <= hi:
            raise SafetyError(f"pan poza zakresem {lo}..{hi} stopni.")
        lo, hi = self.limits.tilt_deg
        if not lo <= tilt <= hi:
            raise SafetyError(f"tilt poza zakresem {lo}..{hi} stopni.")
        step = max(abs(pan - cur_pan), abs(tilt - cur_tilt))
        if step > self.limits.max_step_deg:
            raise SafetyError(f"Zbyt duży skok ({step:.0f}°, max {self.limits.max_step_deg:.0f}°). Wykonaj ruch etapami.")
        return float(pan), float(tilt)

    def check_eyes(self, color: str) -> str:
        if color not in self.limits.eye_colors:
            raise SafetyError(f"Kolor oczu musi być jednym z: {', '.join(self.limits.eye_colors)}.")
        return color
