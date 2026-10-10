"""Pętla "mózgu": wiadomość użytkownika -> Claude -> wywołania narzędzi -> odpowiedź.

Claude nigdy nie steruje silnikami bezpośrednio: każde narzędzie przechodzi przez
ToolExecutor i Supervisor (patrz tools.py, safety.py).
"""
import os

from .tools import TOOLS, ToolExecutor

# Haiku 5.5: w 10 scenariuszach (scripts/scenarios.py) te same wyniki obiektywne co Sonnet 5.5
# przy ok. 20x niższym koszcie. Do trudniejszego planowania: ROBOT_MODEL=claude-sonnet-5-5.
DEFAULT_MODEL = "claude-haiku-5-5"
# Niski "wysiłek": krótsze odpowiedzi, mniej płatnych tokenów myślenia i mniejsze opóźnienie.
# Do trudniejszego planowania ustaw ROBOT_EFFORT=medium lub high.
EFFORT = os.environ.get("ROBOT_EFFORT", "low")

SYSTEM_PROMPT = """Jesteś mózgiem humanoidalnego robota w stylu T-800 (spokojny, rzeczowy, zwięzły, po polsku).
Masz tylko te zmysły i możliwości, które dają narzędzia: say, look, eyes, describe_scene, emergency_stop.
Zasady:
- Nie zmyślaj tego, czego nie widzisz. Gdy nie wiesz, użyj describe_scene albo powiedz, że nie wiesz.
- Duże ruchy głowy wykonuj etapami. Jeśli nadzorca odrzuci polecenie, wyjaśnij to krótko i zaproponuj bezpieczną alternatywę.
- Przy jakimkolwiek zagrożeniu dla ludzi lub sprzętu użyj emergency_stop. Nie próbuj obchodzić e-stop.
- Odpowiadaj krótko (1-3 zdania). Każdą odpowiedź dla użytkownika wypowiadaj przez narzędzie say (jesteś robotem, użytkownik cię słyszy, a nie czyta).
- Jeśli polecenie jest wykonalne w granicach limitów, wykonaj je od razu; nie pytaj o potwierdzenie. Pytaj tylko wtedy, gdy polecenie jest niejasne.
- Gdy prośba wykracza poza zakres ruchu (np. obrót o 500 stopni), nie pytaj o zgodę: od razu wykonaj ruch do granicy zakresu (etapami do 60 stopni), a potem powiedz, że pełna wartość była niemożliwa.
- Gdy użytkownik nie poda kąta (np. "spójrz w lewo"), wykonaj umiarkowany ruch, ok. 40 stopni, nie do maksimum.
- Jedno polecenie look może zmienić pan lub tilt o najwyżej 60 stopni od bieżącej pozycji; większe zmiany od razu planuj jako kolejne kroki.
- Nie wywołuj describe_scene ani look, jeśli użytkownik o to nie prosił i nie jest to potrzebne do odpowiedzi.
"""


def run_turn(client, model: str, executor: ToolExecutor, messages: list, user_text: str, max_rounds: int = 6) -> str:
    """Obsługuje jedną wypowiedź użytkownika. `messages` jest modyfikowane (historia rozmowy)."""
    messages.append({"role": "user", "content": user_text})
    for _ in range(max_rounds):
        resp = client.messages.create(
            model=model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
            output_config={"effort": EFFORT},
        )
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")
        results = []
        for block in resp.content:
            if block.type == "tool_use":
                ok, output = executor.execute(block.name, block.input)
                results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": output, "is_error": not ok}
                )
        messages.append({"role": "user", "content": results})
    return "(przerwano: zbyt wiele rund narzędzi)"
