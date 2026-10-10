"""Fałszywy klient do testów i trybu demo (bez sieci i bez klucza API)."""
from types import SimpleNamespace


def text_block(text: str):
    return SimpleNamespace(type="text", text=text)


def tool_block(tool_id: str, name: str, **args):
    return SimpleNamespace(type="tool_use", id=tool_id, name=name, input=args)


def response(blocks, stop_reason="end_turn"):
    return SimpleNamespace(content=list(blocks), stop_reason=stop_reason)


class ScriptedClient:
    """Zwraca z góry ustalone odpowiedzi, po kolei. Zapisuje wywołania do inspekcji."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        if not self._responses:
            raise AssertionError("ScriptedClient: brak kolejnych odpowiedzi")
        return self._responses.pop(0)


class DemoClient:
    """Prosty 'mózg' oparty na słowach kluczowych, żeby pokazać pętlę bez API."""

    def __init__(self):
        self.messages = SimpleNamespace(create=self._create)
        self._n = 0

    def _create(self, **kwargs):
        msgs = kwargs["messages"]
        last = msgs[-1]
        # po wyniku narzędzia: podsumuj
        if isinstance(last["content"], list):
            return response([text_block("Wykonane.")])
        text = last["content"].lower()
        self._n += 1
        if "lewo" in text:
            return response([tool_block(f"t{self._n}", "look", pan=-40, tilt=0)], "tool_use")
        if "prawo" in text:
            return response([tool_block(f"t{self._n}", "look", pan=40, tilt=0)], "tool_use")
        if "oczy" in text:
            return response([tool_block(f"t{self._n}", "eyes", color="red")], "tool_use")
        if "co widzisz" in text:
            return response([tool_block(f"t{self._n}", "describe_scene")], "tool_use")
        if "stop" in text:
            return response([tool_block(f"t{self._n}", "emergency_stop", reason="polecenie użytkownika")], "tool_use")
        return response([text_block("Tryb demo: spróbuj 'spójrz w lewo', 'oczy', 'co widzisz', 'stop'.")])
