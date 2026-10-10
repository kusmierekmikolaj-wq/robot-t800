---
name: mujoco-sim
description: Tworzenie i strojenie modeli MuJoCo (MJCF) robota w sim/: jednostki, zakresy, siłowniki, weryfikacja przez test. Używaj przy nowym modelu robota, zmianie siłowników lub podłączaniu symulacji jako RobotInterface.
---

# Symulacja MuJoCo

## Konwencje
- Model w `sim/*.xml`, klasa `MuJoCo*` implementuje `RobotInterface` (patrz `sim/mujoco_robot.py`).
- W XML kąty podajemy w stopniach (`<compiler angle="degree"/>`). **Wartości `ctrlrange` siłowników pozycyjnych są w radianach** (jednostki wewnętrzne), więc przelicz: ±90° = ±1,5708.
- Zakresy stawów i `ctrlrange` muszą odpowiadać `Limits` w `brain/safety.py`. Zmiana w jednym miejscu = zmiana w drugim + test.
- Masy i bezwładności bierz z CAD (`cad/masy.csv`), nie zgaduj, gdy model ma służyć do uczenia chodu.

## Lekcja z głowy pan/tilt
Siłownik pozycyjny z `kp=2` nie utrzymał ciężkiej głowy (odchylenie ok. 13° od zadanego tilt). Po zmianie na `kp=30 kv=1` głowa ustawia się z dokładnością ok. 1°. Zawsze sprawdź błąd ustalony pod obciążeniem grawitacją i dodaj `kv` dla tłumienia.

## Weryfikacja
1. Test jednostkowy, który zadaje pozycje i porównuje `state()` z tolerancją (patrz `tests/test_mujoco_head.py`).
2. Test limitu twardego: polecenie poza zakresem nie może wyprowadzić stawu poza `range`.
3. Dla modelu z chodem: najpierw tryb bezgłowy (bez okna), długość epizodu i częstość upadków logowane do pliku.

## Środowisko
`C:\Users\Jeff\.venvs\robot` (Python 3.12, mujoco 3.15.0). Trening chodu na GPU: osobno w WSL2/Ubuntu (jeszcze niezainstalowane), narzędzia mjlab lub MuJoCo Playground.
