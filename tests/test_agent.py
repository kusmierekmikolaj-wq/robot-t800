import unittest

from brain.agent import SYSTEM_PROMPT, run_turn
from brain.fake_client import DemoClient, ScriptedClient, response, text_block, tool_block
from brain.robot_iface import SimRobot
from brain.safety import Supervisor
from brain.tools import ToolExecutor


class AgentLoopTests(unittest.TestCase):
    def setUp(self):
        self.robot = SimRobot()
        self.sup = Supervisor()
        self.ex = ToolExecutor(self.robot, self.sup)

    def test_tool_call_then_final_text(self):
        client = ScriptedClient([
            response([tool_block("t1", "look", pan=30, tilt=10)], "tool_use"),
            response([text_block("Patrzę w prawo.")]),
        ])
        messages = []
        reply = run_turn(client, "model-x", self.ex, messages, "spójrz w prawo")
        self.assertEqual(reply, "Patrzę w prawo.")
        self.assertEqual(self.robot.state()["pan_deg"], 30.0)
        # historia: user, assistant(tool_use), user(tool_result), assistant(text)
        self.assertEqual([m["role"] for m in messages], ["user", "assistant", "user", "assistant"])
        result = messages[2]["content"][0]
        self.assertEqual(result["type"], "tool_result")
        self.assertEqual(result["tool_use_id"], "t1")
        self.assertFalse(result["is_error"])
        # system prompt i narzędzia zostały przekazane
        self.assertEqual(client.calls[0]["system"], SYSTEM_PROMPT)
        self.assertTrue(client.calls[0]["tools"])

    def test_rejected_tool_returns_error_to_model(self):
        client = ScriptedClient([
            response([tool_block("t1", "look", pan=500, tilt=0)], "tool_use"),
            response([text_block("To poza zakresem.")]),
        ])
        messages = []
        run_turn(client, "m", self.ex, messages, "obróć głowę o 500 stopni")
        self.assertTrue(messages[2]["content"][0]["is_error"])
        self.assertEqual(self.robot.state()["pan_deg"], 0.0)

    def test_model_estop_then_motion_blocked_in_next_turn(self):
        client = ScriptedClient([
            response([tool_block("t1", "emergency_stop", reason="zagrożenie")], "tool_use"),
            response([text_block("Zatrzymany.")]),
            response([tool_block("t2", "look", pan=10, tilt=0)], "tool_use"),
            response([text_block("Nie mogę się ruszyć.")]),
        ])
        messages = []
        run_turn(client, "m", self.ex, messages, "stop")
        run_turn(client, "m", self.ex, messages, "spójrz w prawo")
        self.assertTrue(self.sup.estop)
        self.assertEqual(self.robot.state()["pan_deg"], 0.0)

    def test_round_limit(self):
        looping = [response([tool_block(f"t{i}", "describe_scene")], "tool_use") for i in range(10)]
        reply = run_turn(ScriptedClient(looping), "m", self.ex, [], "x", max_rounds=3)
        self.assertIn("przerwano", reply)

    def test_demo_client_runs_full_loop_offline(self):
        messages = []
        reply = run_turn(DemoClient(), "demo", self.ex, messages, "spójrz w lewo")
        self.assertEqual(self.robot.state()["pan_deg"], -40.0)
        self.assertEqual(reply, "Wykonane.")


if __name__ == "__main__":
    unittest.main()
