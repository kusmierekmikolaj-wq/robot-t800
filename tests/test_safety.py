import unittest

from brain.safety import SafetyError, Supervisor


class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.s = Supervisor()

    def test_look_within_limits(self):
        self.assertEqual(self.s.check_look(30, 10, 0, 0), (30.0, 10.0))

    def test_look_out_of_range_rejected(self):
        with self.assertRaises(SafetyError):
            self.s.check_look(120, 0, 0, 0)
        with self.assertRaises(SafetyError):
            self.s.check_look(0, -60, 0, 0)

    def test_large_step_rejected(self):
        with self.assertRaises(SafetyError):
            self.s.check_look(80, 0, -10, 0)  # skok 90 stopni

    def test_non_numeric_rejected(self):
        with self.assertRaises(SafetyError):
            self.s.check_look("10", 0, 0, 0)
        with self.assertRaises(SafetyError):
            self.s.check_look(True, 0, 0, 0)

    def test_estop_blocks_motion_until_human_release(self):
        self.s.trigger_estop("test")
        self.assertTrue(self.s.estop)
        with self.assertRaises(SafetyError):
            self.s.check_look(0, 0, 0, 0)
        with self.assertRaises(SafetyError):
            self.s.release_estop(human_confirmation=False)
        self.s.release_estop(human_confirmation=True)
        self.assertFalse(self.s.estop)
        self.assertEqual(self.s.check_look(10, 0, 0, 0), (10.0, 0.0))

    def test_say_validation(self):
        self.assertEqual(self.s.check_say("  Cześć  "), "Cześć")
        with self.assertRaises(SafetyError):
            self.s.check_say("")
        with self.assertRaises(SafetyError):
            self.s.check_say("x" * 301)

    def test_eye_colors(self):
        self.assertEqual(self.s.check_eyes("red"), "red")
        with self.assertRaises(SafetyError):
            self.s.check_eyes("green")


if __name__ == "__main__":
    unittest.main()
