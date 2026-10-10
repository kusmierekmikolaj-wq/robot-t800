"""Uruchomienie: python -m brain.main

Z kluczem ANTHROPIC_API_KEY i zainstalowanym pakietem `anthropic` używa prawdziwego Claude.
Bez klucza działa tryb demo (DemoClient), żeby można było sprawdzić całą pętlę offline.
Komendy: /stan, /odblokuj (zdejmuje e-stop, tylko człowiek), /koniec.
"""
import os

from .agent import DEFAULT_MODEL, run_turn
from .fake_client import DemoClient
from .robot_iface import SimRobot
from .safety import Supervisor
from .tools import ToolExecutor


def make_client():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        try:
            import anthropic

            return anthropic.Anthropic(api_key=key), os.environ.get("ROBOT_MODEL", DEFAULT_MODEL), "Claude API"
        except ImportError:
            print("Brak pakietu 'anthropic' (pip install anthropic). Tryb demo.")
    return DemoClient(), DEFAULT_MODEL, "tryb demo (bez API)"


def main() -> None:
    client, model, mode = make_client()
    robot, supervisor = SimRobot(), Supervisor()
    executor = ToolExecutor(robot, supervisor)
    messages: list = []
    print(f"Robot (symulacja), mózg: {mode}. Komendy: /stan /odblokuj /koniec")
    while True:
        try:
            text = input("ty> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text == "/koniec":
            break
        if text == "/stan":
            print(robot.state(), "e-stop:", supervisor.estop)
            continue
        if text == "/odblokuj":
            supervisor.release_estop(human_confirmation=True)
            print("E-stop zdjęty przez człowieka.")
            continue
        if not text:
            continue
        reply = run_turn(client, model, executor, messages, text)
        for line in robot.spoken:
            print(f"robot (mówi)> {line}")
        robot.spoken.clear()
        print(f"robot> {reply}" if reply else "robot> (brak odpowiedzi tekstowej)")


if __name__ == "__main__":
    main()
