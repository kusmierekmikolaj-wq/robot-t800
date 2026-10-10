"""Głowa w MuJoCo jako implementacja RobotInterface (wymaga pakietu `mujoco`)."""
import math
from pathlib import Path

from brain.robot_iface import RobotInterface

HEAD_XML = Path(__file__).with_name("head.xml")


class MuJoCoHead(RobotInterface):
    def __init__(self, xml_path: Path = HEAD_XML, scene: str = "Biurko, kubek po lewej, laptop na wprost."):
        import mujoco

        self._mj = mujoco
        self.model = mujoco.MjModel.from_xml_path(str(xml_path))
        self.data = mujoco.MjData(self.model)
        self.scene = scene
        self.spoken: list[str] = []
        self.eye = "off"
        self._eye_geoms = [mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_GEOM, n) for n in ("eye_l", "eye_r")]
        self._set_eye_color("off")

    _COLORS = {"off": (0.1, 0.1, 0.1, 1), "red": (1, 0, 0, 1), "amber": (1, 0.6, 0, 1), "blue": (0, 0.4, 1, 1)}

    def _set_eye_color(self, color: str) -> None:
        for gid in self._eye_geoms:
            self.model.geom_rgba[gid] = self._COLORS[color]

    def say(self, text: str) -> None:
        self.spoken.append(text)

    def look(self, pan_deg: float, tilt_deg: float) -> None:
        self.data.ctrl[0] = math.radians(pan_deg)
        self.data.ctrl[1] = math.radians(tilt_deg)
        for _ in range(1500):  # ok. 3 s symulacji, aż głowa się ustabilizuje
            self._mj.mj_step(self.model, self.data)

    def eyes(self, color: str) -> None:
        self.eye = color
        self._set_eye_color(color)

    def describe_scene(self) -> str:
        return self.scene

    def state(self) -> dict:
        return {
            "pan_deg": math.degrees(self.data.qpos[0]),
            "tilt_deg": math.degrees(self.data.qpos[1]),
            "eyes": self.eye,
        }
