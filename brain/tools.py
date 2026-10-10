"""Narzędzia, które Claude może wywoływać, i ich wykonawca (przez nadzorcę)."""
from .robot_iface import RobotInterface
from .safety import SafetyError, Supervisor

TOOLS = [
    {
        "name": "say",
        "description": "Powiedz coś na głos (krótko, po polsku).",
        "input_schema": {
            "type": "object",
            "properties": {"text": {"type": "string", "description": "Tekst do wypowiedzenia."}},
            "required": ["text"],
        },
    },
    {
        "name": "look",
        "description": "Obróć głowę. pan: -90 (lewo) .. 90 (prawo), tilt: -30 (dół) .. 40 (góra), w stopniach. "
                       "Duże ruchy wykonuj etapami (maks. 60° na raz).",
        "input_schema": {
            "type": "object",
            "properties": {"pan": {"type": "number"}, "tilt": {"type": "number"}},
            "required": ["pan", "tilt"],
        },
    },
    {
        "name": "eyes",
        "description": "Ustaw kolor diod oczu: off, red, amber, blue.",
        "input_schema": {
            "type": "object",
            "properties": {"color": {"type": "string", "enum": ["off", "red", "amber", "blue"]}},
            "required": ["color"],
        },
    },
    {
        "name": "describe_scene",
        "description": "Zwróć opis tego, co widzi kamera robota.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "emergency_stop",
        "description": "Natychmiast zablokuj wszystkie ruchy. Użyj przy jakimkolwiek zagrożeniu. "
                       "Odblokować może tylko człowiek.",
        "input_schema": {
            "type": "object",
            "properties": {"reason": {"type": "string"}},
            "required": ["reason"],
        },
    },
]


class ToolExecutor:
    def __init__(self, robot: RobotInterface, supervisor: Supervisor):
        self.robot = robot
        self.supervisor = supervisor

    def execute(self, name: str, args: dict) -> tuple[bool, str]:
        """Zwraca (ok, tekst_wyniku). Błędy walidacji wracają do Claude jako is_error."""
        try:
            if name == "say":
                text = self.supervisor.check_say(args.get("text"))
                self.robot.say(text)
                return True, "Powiedziano."
            if name == "look":
                st = self.robot.state()
                pan, tilt = self.supervisor.check_look(
                    args.get("pan"), args.get("tilt"), st["pan_deg"], st["tilt_deg"]
                )
                self.robot.look(pan, tilt)
                return True, f"Głowa ustawiona: pan={pan}, tilt={tilt}."
            if name == "eyes":
                color = self.supervisor.check_eyes(args.get("color"))
                self.robot.eyes(color)
                return True, f"Oczy: {color}."
            if name == "describe_scene":
                return True, self.robot.describe_scene()
            if name == "emergency_stop":
                self.supervisor.trigger_estop(str(args.get("reason", "brak powodu")))
                return True, "E-stop aktywny. Ruchy zablokowane do odblokowania przez człowieka."
            return False, f"Nieznane narzędzie: {name}."
        except SafetyError as e:
            return False, f"Odrzucone przez nadzorcę: {e}"
