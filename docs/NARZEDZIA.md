# Narzędzia, wtyczki i umiejętności potrzebne do budowy robota

Stan na 2026-10-08. Nic z tej listy nie zostało zainstalowane poza tymczasowym środowiskiem testowym (patrz sekcja 5). Instalacje zatwierdzasz ty.

## 1. Co już mam w tej sesji (wystarczy na etap 0)

| Narzędzie / umiejętność | Do czego |
|---|---|
| Edycja plików, PowerShell/Bash | pisanie kodu, uruchamianie testów, symulacji, skryptów |
| WebSearch / WebFetch, wbudowana przeglądarka, Chrome | dokumentacja, ceny, sklepy (Botland) |
| Umiejętność `claude-api` | wzorce API Claude: tool use, wizja, buforowanie, limity |
| `engineering:system-design`, `architecture`, `testing-strategy`, `documentation` | projekt architektury, strategia testów, dokumentacja |
| `anthropic-skills:xlsx` | arkusz BOM, budżet, śledzenie zakupów |
| `schedule`, `loop` | cykliczne zadania i przypomnienia (np. sprawdzanie cen) |

## 2. Czego brakuje i trzeba zainstalować lokalnie (oprogramowanie, nie wtyczki)

| Co | Po co | Etap |
|---|---|---|
| **Python 3.12** (jest) w osobnym venv | środowisko projektu (systemowy 3.14 jest za nowy dla bibliotek ML) | 0 |
| `anthropic` | prawdziwy mózg (API Claude) | 0 |
| `mujoco`, `numpy` | symulacja głowy i robota (zweryfikowane na wersji 3.15.0) | 0 |
| `pytest` (opcjonalnie) | wygodniejsze testy niż unittest | 0 |
| `pyserial`, `pyaudio` / `sounddevice` | serwa i mikrofon na prawdziwym sprzęcie | 0–1 |
| Whisper (STT) i Piper (TTS) | mowa lokalnie, bez chmury | 0 |
| `cadquery` (lub OpenSCAD), `trimesh`, `matplotlib` | **parametryczny CAD w kodzie** i renderowanie podglądu STL | 0–2 |
| OrcaSlicer lub Bambu Studio | cięcie modeli na P2S (ręcznie lub z linii poleceń) | 0 |
| FreeCAD / Fusion 360 / Onshape (ty) | swobodne modelowanie, wymiana plików STEP | 1+ |
| **WSL2 + Ubuntu** (WSL jest, brak dystrybucji) | trening polityki chodu na GPU | 3–4 |
| PyTorch z CUDA, `mjlab` (lub MuJoCo Playground) | uczenie ze wzmocnieniem; karta RTX 2080 Ti 11 GB wystarczy | 3–4 |
| LeRobot (Hugging Face) | ramię SO-101, uczenie przez naśladowanie | 2 |
| ROS 2 (opcjonalnie) | komunikacja między modułami, na początku niepotrzebne | 3+ |
| Git | wersjonowanie CAD, firmware i kodu | 0 |

## 3. Wtyczki i konektory z katalogu (przeszukane dziś)

| Nazwa | Co robi | Moja ocena |
|---|---|---|
| **3D CAD Converter** (ContentaSoft AB, społeczność, uruchamiana lokalnie) | konwersja STEP, IGES, STL, OBJ, 3MF, glTF itd. | **Przydatna** do wymiany STEP↔STL. Nie testowana przeze mnie; zaufanie do autora trzeba ocenić samemu. |
| SpeakCAD Slicer (społeczność, zdalna) | cięcie STL/3MF z profilami OrcaSlicer, wynik przez ich serwis online | Opcjonalna. Plik trafia do zewnętrznej usługi, więc nie dla własnych projektów. Lepiej lokalny OrcaSlicer. |
| Trimble SketchUp (MCP) | tworzenie modeli 3D w SketchUp | Nie polecam: to modelowanie bryłowe/architektoniczne, nie parametryczne i nie inżynierskie. |
| Roboflow | wizja komputerowa (zbiory, trening modeli) | Na później (rozpoznawanie przedmiotów, etap 2+). |
| Three.js 3D Viewer (demo) | interaktywny podgląd 3D | Demo, nie narzędzie robocze. |

W bibliotece twoich umiejętności claude.ai (`SearchSkills`) ani w katalogu do dodania (`SuggestSkills`) **nie ma dedykowanych umiejętności CAD ani robotyki** (oba wyszukiwania zwróciły 0 wyników). Dlatego utworzyłem własne **skile projektu** w `.claude/skills/`:

| Skill | Zakres |
|---|---|
| `fdm-cad-design` | CadQuery pod druk FDM na P2S: tolerancje startowe (do skalibrowania), ściany, orientacja, materiały, kontrola szczelności STL i podgląd |
| `robot-brain-safety` | dodawanie narzędzi mózgu robota przez nadzorcę, e-stop odblokowywany tylko przez człowieka, wymagane testy |
| `mujoco-sim` | konwencje MJCF (jednostki), strojenie siłowników, weryfikacja testem, środowisko |

Skile projektu ładują się po otwarciu folderu projektu w nowej sesji (`C:\Users\Jeff\Documents\druk3d-robot\robot`). Wartości tolerancji w `fdm-cad-design` to punkt wyjścia, nie sprawdzone dane dla twojej drukarki.

## 4. Sprzęt pomocniczy do pracy (poza robotem)

Multimetr, zasilacz laboratoryjny z ograniczeniem prądu (ważne przy pierwszym uruchomieniu siłowników), lutownica z regulacją, suwmiarka, wkładki gwintowane M3/M4 i lutownica do ich wtapiania, przycisk awaryjny, stelaż/uprząż do testów nóg, woreczek ognioodporny na LiPo.

## 5. Co zostało zainstalowane (2026-10-08)

**Środowisko projektu: `C:\Users\Jeff\.venvs\robot`** (Python 3.12.10, poza folderem projektu, bo ścieżka jest krótka). Aktywacja: `C:\Users\Jeff\.venvs\robot\Scripts\activate`. Dokładne wersje: `requirements-lock.txt`.

| Pakiet | Wersja | Zweryfikowane |
|---|---|---|
| anthropic | 1.12.1 | import; **nie** wywołane (brak klucza API) |
| mujoco, numpy, scipy | 3.15.0, 2.5.3, 1.18.1 | 21 testów, model głowy w symulacji |
| cadquery (z OCP) | 2.8.0 | model → STL: siatka szczelna, wymiary i objętość zgodne z obliczeniami |
| trimesh, matplotlib | 5.1.1, 3.11.2 | wczytanie STL, podgląd PNG |
| pytest | 9.1.1 | 21 przeszło |
| opencv-python | 5.0.0.93 | tylko import; **kamera nie testowana** |
| sounddevice | 0.5.6 | widzi 9 wejść i 20 wyjść audio; **mikrofon i głośnik nie testowane** |
| faster-whisper | 1.2.1 | tylko import; **modele STT nie pobrane** |
| piper-tts | 1.8.0 | tylko import; **głosy TTS nie pobrane** |
| pyserial | 3.5 | tylko import |

Już było w systemie: Git, winget, ffmpeg, Node, Python 3.12 i 3.14.

**Celowo NIE zainstalowane (niepotrzebne na etapach 0–2, duże albo wymagające uprawnień):**
- PyTorch z CUDA, mjlab / MuJoCo Playground, LeRobot: dopiero etap 2–3 (kilka GB).
- **WSL2 z Ubuntu**: wymaga uprawnień administratora i prawdopodobnie ponownego uruchomienia komputera, potrzebny dopiero do treningu chodu (etap 3).
- OrcaSlicer / Bambu Studio: pliki instalacyjne GUI. Bambu Studio zainstalujesz, gdy dojdzie drukarka.
- ROS 2, FreeCAD, Fusion 360 i inne programy graficzne.

**Do usunięcia, jeśli chcesz:** `C:\Users\Jeff\AppData\Local\Temp\rvenv` (wcześniejsze środowisko testowe, już niepotrzebne).
