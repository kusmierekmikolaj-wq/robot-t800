# Robot (styl T-800) z Claude jako mózgiem

Etap 0, dzień 1: **wirtualny robot (głowa) + pętla Claude z narzędziami + nadzorca bezpieczeństwa**, bez sprzętu.
Pełny plan: `docs/PLAN_BUDOWY.md`. Narzędzia i wtyczki: `docs/NARZEDZIA.md`.

## Uruchomienie

Wymagany Python 3.11+ (zalecany 3.12; systemowy 3.14 jest za nowy dla bibliotek ML).

Środowisko jest już zainstalowane w `C:\Users\Jeff\.venvs\robot` (lista pakietów: `requirements-lock.txt`).

```bash
C:\Users\Jeff\.venvs\robot\Scripts\activate

python -m pytest -q                      # testy (21)
python -m brain.main                     # rozmowa w terminalu (tryb demo bez klucza)
set ANTHROPIC_API_KEY=...                # prawdziwy Claude (ustaw limit wydatków w koncie API)
```

Odtworzenie środowiska od zera: `py -3.12 -m venv <ścieżka>` i `pip install -r requirements-lock.txt`.

Z kluczem `ANTHROPIC_API_KEY` i pakietem `anthropic` mózgiem jest Claude (model z `ROBOT_MODEL`,
domyślnie `claude-haiku-5-5`, ok. 20x taniej od Sonneta; do trudniejszych zadań `ROBOT_MODEL=claude-sonnet-5-5`). Ustaw limit wydatków w koncie API. Bez klucza działa tryb demo.

Komendy w terminalu: `/stan`, `/odblokuj` (zdejmuje e-stop, tylko człowiek), `/koniec`.

## Struktura

```
brain/       pętla Claude (agent.py), narzędzia (tools.py), nadzorca (safety.py), interfejs robota (robot_iface.py)
sim/         model MuJoCo głowy (head.xml) i jego implementacja interfejsu (mujoco_robot.py)
tests/       testy jednostkowe (unittest, bez sieci)
docs/        plan budowy i lista narzędzi
```

## Zasady bezpieczeństwa (w kodzie)

- Claude nigdy nie steruje silnikami wprost: każde narzędzie przechodzi przez `Supervisor` (limity kątów, maks. skok, e-stop).
- Claude może wywołać `emergency_stop`, **odblokować może tylko człowiek** (`/odblokuj`).
- Odrzucone polecenie wraca do modelu jako błąd z wyjaśnieniem, robot się nie rusza.

## Dalsze kroki (z planu)

1. Prawdziwy klucz API i test rozmowy.
2. Dodanie STT/TTS i opisu sceny z kamery.
3. Klasa `PiRobot(RobotInterface)` dla Raspberry Pi 5 i serw pan/tilt (po dojściu sprzętu i drukarki).
4. Obudowa czaszki T-800 jako parametryczny model CadQuery w `cad/`.
