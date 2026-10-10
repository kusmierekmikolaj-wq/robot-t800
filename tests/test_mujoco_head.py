import importlib.util
import unittest

HAS_MUJOCO = importlib.util.find_spec("mujoco") is not None


@unittest.skipUnless(HAS_MUJOCO, "pakiet mujoco nie jest zainstalowany")
class MuJoCoHeadTests(unittest.TestCase):
    def test_head_follows_commands_within_limits(self):
        from sim.mujoco_robot import MuJoCoHead

        head = MuJoCoHead()
        head.look(30, 10)
        st = head.state()
        self.assertAlmostEqual(st["pan_deg"], 30, delta=3)
        self.assertAlmostEqual(st["tilt_deg"], 10, delta=3)

    def test_ctrl_range_clamps_unsafe_command(self):
        from sim.mujoco_robot import MuJoCoHead

        head = MuJoCoHead()
        head.look(170, 0)  # supervisor odrzuciłby to wcześniej; model też ma twardy limit
        self.assertLessEqual(head.state()["pan_deg"], 91)


if __name__ == "__main__":
    unittest.main()
