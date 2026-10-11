# Robot T-800: zasady projektu

Głowa (a później cały robot) w stylu T-800 z Claude jako mózgiem. Plan: `docs/PLAN_BUDOWY.md`, głowa: `docs/PROJEKT_CZASZKI.md`, model czaszki: `cad/t800/README.md`.

## Użytkownik

- Pisze po polsku (często bez polskich znaków). Odpowiadaj po polsku, prosto, krótko, w ponumerowanych krokach.
- Jedna wyraźna rekomendacja zamiast listy opcji. Mów, co zmienia się na jego dysku.
- Wygląd sprawdzaj na renderze lub zrzucie, zanim powiesz, że jest dobrze (użytkownik wyłapuje błędy wizualne).
- "stop" albo "nie rób nic" w trakcie: przerwij od razu i podsumuj stan.

## Decyzje (nie podważaj bez nowego powodu)

- **Budżet ograniczony.** Przed każdym zakupem: test za 0 zł i uzasadnienie zwrotu. Kolejny etap dopiero po zaliczeniu bramki poprzedniego (`docs/PLAN_BUDOWY.md`, sekcje 4 i 9).
- **Bez lutowania** (brak lutownicy). Tylko moduły na złączach i przewodach wtykowych.
- **Etap 0 (głowa):** płytka DFRobot ESP32-S3 AI Camera DFR1154 (kamera, mikrofon, głośnik, ok. 109 zł). Mózg, rozpoznawanie i synteza mowy działają na PC użytkownika. Bez Raspberry Pi 5 i bez serw na tym etapie. Najpierw serwer na PC testowany bez płytki.
- **Model mózgu:** domyślnie `claude-haiku-5-5` (przechodzi 10 scenariuszy bezpieczeństwa). Klucz API jest w zmiennej środowiskowej użytkownika `ANTHROPIC_API_KEY`; nigdy nie zapisuj go w plikach.
- **Drukarka:** Bambu Lab P2S (pole 256 mm). Zamówienie jeszcze niezłożone.
- **Czaszka:** model z MakerWorld na licencji **CC BY-NC-SA**: tylko użytek osobisty, **nigdy nie sprzedawać** wydruków ani plików, zachować przypisanie autorów (`cad/t800/README.md`). Druk w skali 115%, w oryginalnych 6 kawałkach.

## Środowisko

- Python: `C:\Users\Jeff\.venvs\robot\Scripts\python.exe` (3.12). Systemowy 3.14 jest za nowy dla MuJoCo i bibliotek ML.
- Testy: `C:\Users\Jeff\.venvs\robot\Scripts\python.exe -m pytest -q`
- Blender 5.2.2: `C:\Users\Jeff\blender3d`, MCP na porcie 9876. FreeCAD 1.1.4: `C:\Users\Jeff\freecad3d`, MCP na porcie 9875. Konfiguracja w `.mcp.json` (działa, gdy sesja jest otwarta w tym folderze).
- Ciężkie rendery: osobny proces Blendera w tle (GPU RTX 2080 Ti), nie przez gniazdo GUI.
- Długie ścieżki Windows psują narzędzia: używaj krótkich folderów.
- Skrypty czytające pobrane pliki (`cad/t800/narzedzia/`) uruchamiaj z `python -I`.
- Kod z ukośnikami wstecznymi (regex, ścieżki) zapisuj narzędziem Write/Edit, nie przez heredoc w Bash (gubi `\`).

## Praca z kodem

- Narzędzia mózgu zawsze przez nadzorcę bezpieczeństwa (skill `robot-brain-safety`). E-stop odblokowuje tylko człowiek.
- Części 3D: skill `fdm-cad-design`. Symulacja: skill `mujoco-sim`.
- Repozytorium jest **publiczne**: github.com/kusmierekmikolaj-wq/robot-t800 (remote `origin`, gałąź `main`). Nigdy nie commituj geometrii czaszki (`cad/ref/`, `*.stl`, `*.step`, `*.blend`: licencja CC BY-NC-SA, jest w `.gitignore`), kluczy API ani danych osobistych. Tożsamość git: adres noreply GitHuba (`299278702+kusmierekmikolaj-wq@users.noreply.github.com`), nie gmail.
- Po zakończonym kroku: testy, commit z krótkim opisem po polsku, `git push`.
