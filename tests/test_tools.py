import unittest

from brain.robot_iface import SimRobot
from brain.safety import Supervisor
from brain.tools import TOOLS, ToolExecutor


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.robot = SimRobot()
        self.sup = Supervisor()
        self.ex = ToolExecutor(self.robot, self.sup)

    def test_schemas_are_complete(self):
        names = {t["name"] for t in TOOLS}
        self.assertEqual(names, {"say", "look", "eyes", "describe_scene", "emergency_stop"})
        for t in TOOLS:
            self.assertIn("input_schema", t)
            self.assertEqual(t["input_schema"]["type"], "object")

    def test_look_updates_robot(self):
        ok, _ = self.ex.execute("look", {"pan": 30, "tilt": 10})
        self.assertTrue(ok)
        self.assertEqual(self.robot.state()["pan_deg"], 30.0)

    def test_rejected_look_does_not_move_robot(self):
        ok, msg = self.ex.execute("look", {"pan": 200, "tilt": 0})
        self.assertFalse(ok)
        self.assertIn("nadzorc", msg)
        self.assertEqual(self.robot.state()["pan_deg"], 0.0)

    def test_missing_arguments_rejected_not_crash(self):
        ok, _ = self.ex.execute("look", {})
        self.assertFalse(ok)

    def test_unknown_tool(self):
        ok, msg = self.ex.execute("fly", {})
        self.assertFalse(ok)
        self.assertIn("Nieznane", msg)

    def test_say_and_eyes_and_scene(self):
        self.assertTrue(self.ex.execute("say", {"text": "Cześć"})[0])
        self.assertEqual(self.robot.spoken, ["Cześć"])
        self.assertTrue(self.ex.execute("eyes", {"color": "red"})[0])
        self.assertEqual(self.robot.state()["eyes"], "red")
        ok, scene = self.ex.execute("describe_scene", {})
        self.assertTrue(ok and "kubek" in scene)

    def test_emergency_stop_blocks_following_motion(self):
        self.assertTrue(self.ex.execute("emergency_stop", {"reason": "test"})[0])
        ok, _ = self.ex.execute("look", {"pan": 10, "tilt": 0})
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
