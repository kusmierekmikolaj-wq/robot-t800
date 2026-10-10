"""Interfejs robota. SimRobot to wirtualny robot do testów bez sprzętu.

Prawdziwy robot (Raspberry Pi, serwa, kamera) zaimplementuje ten sam interfejs,
więc reszta kodu (nadzorca, narzędzia, pętla Claude) nie zmienia się.
"""
from abc import ABC, abstractmethod


class RobotInterface(ABC):
    @abstractmethod
    def say(self, text: str) -> None: ...

    @abstractmethod
    def look(self, pan_deg: float, tilt_deg: float) -> None: ...

    @abstractmethod
    def eyes(self, color: str) -> None: ...

    @abstractmethod
    def describe_scene(self) -> str: ...

    @abstractmethod
    def state(self) -> dict: ...


class SimRobot(RobotInterface):
    def __init__(self, scene: str = "Biurko, kubek po lewej, laptop na wprost, osoba po prawej."):
        self.pan = 0.0
        self.tilt = 0.0
        self.eye = "off"
        self.spoken: list[str] = []
        self.scene = scene

    def say(self, text: str) -> None:
        self.spoken.append(text)

    def look(self, pan_deg: float, tilt_deg: float) -> None:
        self.pan, self.tilt = pan_deg, tilt_deg

    def eyes(self, color: str) -> None:
        self.eye = color

    def describe_scene(self) -> str:
        return self.scene

    def state(self) -> dict:
        return {"pan_deg": self.pan, "tilt_deg": self.tilt, "eyes": self.eye}
