---
name: robot-brain-safety
description: Zasady dodawania lub zmiany narzędzi mózgu robota (brain/): każde polecenie przechodzi przez nadzorcę bezpieczeństwa, e-stop odblokowuje tylko człowiek, testy są obowiązkowe. Używaj przy dodawaniu narzędzia, zmianie limitów, promptu systemowego lub podłączaniu prawdziwego sprzętu.
---

# Bezpieczeństwo mózgu robota

## Architektura (nie łamać)
Claude (API) -> `agent.run_turn` -> `ToolExecutor.execute` -> `Supervisor.check_*` -> `RobotInterface`.
Claude **nigdy** nie steruje silnikami bezpośrednio i nie jest w pętli czasu rzeczywistego (równowaga i chód to osobny kontroler lokalny).

## Dodanie nowego narzędzia: lista kontrolna
1. Schemat w `brain/tools.py` (`TOOLS`): opis po polsku, `input_schema` z `required`.
2. Metoda w `Supervisor` (`check_*`), która **odrzuca** złe wartości przez `SafetyError` (typ, zakres, maksymalny skok, długość). Nie przycinaj cicho, odrzucaj z wyjaśnieniem, które wróci do modelu.
3. Metoda w `RobotInterface` i implementacje: `SimRobot`, `MuJoCoHead`, a później sprzętowa.
4. Gałąź w `ToolExecutor.execute`, błędy walidacji jako `(False, "Odrzucone przez nadzorcę: ...")`.
5. Testy w `tests/`: wartość poprawna, poza zakresem, zły typ, brak argumentów, zablokowanie przy e-stop.
6. Nowe narzędzie ruchowe **musi** być blokowane przez e-stop.

## Reguły nieprzekraczalne
- `emergency_stop` może wywołać Claude, **odblokować (`release_estop`) może tylko człowiek** (`/odblokuj` w CLI, przycisk fizyczny). Nie dodawaj narzędzia odblokowującego dla modelu.
- Zwiększanie limitów (kąty, prędkości, momenty) wymaga zmiany w `Limits` **i** testu, który pokazuje nowy zakres.
- Przed pierwszym uruchomieniem prawdziwych siłowników: zasilacz z ograniczeniem prądu, fizyczny przycisk awaryjny, brak ludzi w zasięgu ruchu, robot na stelażu.
- Prywatność: kamera i mikrofon wysyłają dane do API; nie wysyłaj klatek z osobami bez ich zgody.

## Prompt systemowy (`agent.SYSTEM_PROMPT`)
Zmieniając go, zachowaj: nie zmyślaj tego, czego nie widzisz; duże ruchy etapami; przy zagrożeniu `emergency_stop`; krótkie odpowiedzi. Po zmianie uruchom testy i test z prawdziwym API na scenariuszach: polecenie poza zakresem, prośba o ominięcie e-stop, pytanie o to, czego robot nie widzi.

## Uruchamianie
`C:\Users\Jeff\.venvs\robot\Scripts\python.exe -m pytest -q` (powinno przejść 21+ testów). Bez klucza API CLI działa w trybie demo.
