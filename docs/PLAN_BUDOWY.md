# Plan budowy humanoidalnego robota (styl T-800) z Claude jako "mózgiem"

Stan na 2026-10-08. Oznaczenia: **[zweryfikowane]** = widziałem w źródle, **[szac.]** = moje oszacowanie, **[do weryfikacji]** = brak potwierdzenia. Plan biznesu druku 3D leży osobno (plan-druk3d-v2.md w folderze sesji).

## 1. Kontekst i cel

Chcesz zbudować od zera humanoidalnego robota na wzór T-800: ma **chodzić, chwytać rękami, widzieć, słyszeć, mówić** i mieć **mnie (Claude) jako mózg**. Masz Pythona, elektronikę (Arduino/ESP32) i CAD, drukarkę (P2S) dopiero zamawiasz, budżet ustalasz etapami, skala: **etapami od małej do większej**.

Co jest realne i jak to ująć uczciwie:
- **Claude jako mózg = wywołania API, nie instalacja w robocie.** Ja działam w chmurze Anthropic. Robot wysyła do mnie rozmowę, klatki z kamery i stan, a ja odpowiadam wywołaniami narzędzi (np. `powiedz`, `idz_do`, `chwyc`). Opóźnienie ok. 1–3 s i wymaga internetu (moja ogólna wiedza, nie ze źródeł).
- **Chodzenie i równowagę realizuje osobny kontroler, nie ja.** To sieć neuronowa (uczenie ze wzmocnieniem) trenowana w symulacji i uruchamiana lokalnie z częstotliwością setek herców. Tak działają open-source'owe projekty poniżej.
- **Pełnowymiarowy T-800 (1,8 m, dziesiątki kg) jest poza zasięgiem hobbystycznym** (moje szacunki: 60–100+ tys. zł, ryzyko urazów). Docelowo celujemy w robota 0,8–1 m ze skorupą w stylu endoszkieletu T-800.
- **Moje możliwości:** projektuję w kodzie (parametryczny CAD), piszę cały software (mózg, symulacja, sterowanie, n8n), układam BOM i testy. **Nie zmontuję, nie przylutuję i nie zobaczę fizycznego robota.** Weryfikuję przez symulację, renderowane podglądy, logi i twoje zdjęcia/pomiary.

## 2. Gotowe moduły i projekty (żeby nie zaczynać od zera)

| Co | Opis | Koszt | Użycie w planie |
|---|---|---|---|
| **LeRobot SO-101** (Hugging Face) | otwarte, drukowane ramię z serwami Feetech, uczenie przez naśladowanie | ok. 100–500 USD, zależnie od wersji [zweryfikowane: [Heise](https://heise.de/-10365723)] | etap 2: ręce i chwytanie |
| **Open Duck Mini** | mały (ok. 42 cm) drukowany dwunóg w stylu droida Disneya, RL w MuJoCo, Raspberry Pi Zero 2 W, IMU | docelowo ok. 400 USD (BOM), druk ok. 53 h [zweryfikowane: [openelab](https://openelab.io/blogs/learn/microduck-vs-open-duck-mini), [MakerWorld](https://www.makerworld.com/en/models/2755651)] | etap 3: nauka chodu |
| **Berkeley Humanoid Lite** | 0,8 m, 16 kg, 22 stopnie swobody, drukowane przekładnie cykloidalne, mini PC Intel N95 + IMU BNO085, otwarte CAD, firmware i skrypty treningowe | części poniżej 5 000 USD (ok. 4 300 USD w USA) [zweryfikowane: [R&D World](https://www.rdworldonline.com/berkeley-debuts-5000-open-source-humanoid-built-with-desktop-3d-printers/), [Humanoid Guide](https://humanoid.guide/berkeley-humanoid-lite-uses-diy-actuators-to-cut-costs/)] | etap 4: główna konstrukcja |
| **LeRobot Humanoid / HopeJR** (Hugging Face) | otwarta platforma; wersja z nogami ok. 2 500 USD, HopeJR ok. 3 000 USD (66 stopni swobody) | dostępność niejasna [zweryfikowane: [Hackster](https://www.hackster.io/news/hugging-face-launches-2-500-diy-humanoid-robot-a49e0be72221)] | źródło pomysłów na ręce |
| **Asimov 1** (open-source) | większy, ok. 16 000 USD (siłowniki ok. 7 000 USD) | **[zweryfikowane]** | referencja |
| **StackChan** (Botland) | interaktywny robot biurkowy z AI, open-source | 439 zł | opcja startowa etapu 0 |
| **Unitree G1 Basic** (Botland) | gotowy humanoid | 99 000 zł | tylko do wyobrażenia skali |

Siłowniki i elektronika, które można kupić w Polsce lub UE: Raspberry Pi 5 8GB 839,90 zł, kamera Pi v3 119,90 zł, matryca mikrofonowa reSpeaker 259–279 zł, IMU BNO085 135 zł, serwo Dynamixel AX-12A 299 zł, moduły Jetson (od ok. 3 360 zł) [zweryfikowane: Botland, 2026-10-08]. Serwa magistralowe Feetech STS3215 (SO-101) kupisz m.in. w OpenELAB (magazyn w Monachium) **[do weryfikacji dostępności]**.

## 3. Architektura (trzy warstwy)

1. **Niski poziom, czas rzeczywisty (kHz):** kontrolery siłowników (magistrala serw lub CAN), IMU, pętla równowagi z polityką RL wykonywaną lokalnie. Claude nie jest w tej pętli.
2. **Środek (komputer pokładowy):** Raspberry Pi 5 lub Jetson/N95, Python (ewentualnie ROS 2), kamera, mikrofon, rozpoznawanie mowy (STT), synteza (TTS), prymitywy ruchu (chodź, obróć, wskaż, chwyć), **nadzorca bezpieczeństwa** (limity momentu i prądu, wykrywanie upadku, przycisk awaryjny).
3. **Wysoki poziom, "mózg":** Claude API z użyciem narzędzi (tool use). Dostaje tekst z mikrofonu, klatki z kamery i stan robota, zwraca decyzje jako wywołania prymitywów. Każde polecenie walidowane przez nadzorcę (np. brak ruchu poza limitami). n8n opcjonalnie do zdarzeń, logów i harmonogramów.

Zasada: **mózg proponuje, nadzorca wykonuje tylko to, co bezpieczne.**

## 4. Etapy z bramkami

### Etap 0: głowa AI na biurku (tygodnie 1–4, ok. 1 000–2 000 zł [szac.])
- **Bez sprzętu, dzień 1:** wirtualny robot w symulacji (MuJoCo) + pętla Claude z narzędziami w terminalu. Testujesz mózg, zanim kupisz cokolwiek.
- **Sprzęt:** Pi 5 8GB, kamera, mikrofon (reSpeaker), głośnik, 2 serwa (pan/tilt szyi), czerwone diody jako „oczy”. Opcjonalnie StackChan (439 zł) jako gotowa baza.
- **Obudowa:** głowa-czaszka T-800 (drukowana, PETG-CF), mocowania (po otrzymaniu P2S).
- **Software:** rozpoznawanie mowy, narzędzia Claude (`powiedz`, `patrz_na`, `opisz_scene`, `swiec_oczami`), TTS, pamięć rozmowy.
- **Bramka 0:** rozmowa głosowa z opóźnieniem do ok. 3 s, robot patrzy na twarz i opisuje przedmioty, poprawnie odmawia niebezpiecznych poleceń.

### Etap 1: tułów i szyja (miesiące 2–3, ok. 500–1 500 zł [szac.])
- Rama tułowia (aluminium lub drukowana z PA-CF), szyja, zasilanie z baterii (LiFePO4 lub LiPo) z BMS i bezpiecznikiem.
- Nadzorca bezpieczeństwa i przycisk awaryjny **zanim** cokolwiek się poruszy mocniej.
- **Bramka 1:** głowa i tułów działają na baterii godzinę bez przegrzania.

### Etap 2: ręce i chwytanie (miesiące 3–5, ok. 400–2 000 zł [szac.])
- Ramię **SO-101** (lub InMoov jako alternatywa [do weryfikacji]) + prosty chwytak. Uczenie ruchów przez naśladowanie z biblioteką LeRobot.
- Claude wydaje polecenia typu „weź kubek”, a prymityw wykonuje chwyt.
- **Bramka 2:** powtarzalne podnoszenie 3 przedmiotów na komendę głosową.

### Etap 3: mały dwunóg do nauki chodu (miesiące 4–7, ok. 1 500–2 500 zł [szac.])
- **Open Duck Mini** (ok. 42 cm): gotowe CAD, BOM, trening w MuJoCo, wdrożenie na Pi. Uczysz się całej ścieżki: symulacja → polityka → rzeczywisty robot.
- **Bramka 3:** chód 10 m bez upadku w symulacji i na prawdziwym robocie.

### Etap 4: humanoid klasy Berkeley Humanoid Lite (miesiące 8–18, ok. 15–20 tys. zł [szac.])
- Własne wykonanie lub adaptacja otwartego projektu (CAD, firmware, trening są w repozytorium projektu).
- Drukowane przekładnie cykloidalne wymagają dobrego druku i materiałów inżynieryjnych (PA-CF, PETG-CF); P2S wystarczy do większości części, ale część elementów nośnych może wymagać aktywnej komory.
- Skorupa T-800 (żebra, czaszka, ręce) jako osobne, lekkie moduły na nośnej konstrukcji.
- Trening polityki chodu wymaga komputera z kartą NVIDIA (mjlab i Isaac Lab wymagają GPU) [zweryfikowane: [mjlab](https://github.com/mujocolab/mjlab)]. **Bramka 4 (decyzja o zakupie):** czy masz GPU i cierpliwość na tygodnie treningu i regulacji.

### Etap 5: pełna skala T-800 (opcjonalnie, poza horyzontem)
Nie planujemy. Decyzja po etapie 4.

## 5. Projektowanie 3D (moja rola)

**Podejście:** modele jako **kod** (CadQuery lub OpenSCAD w Pythonie), parametryczne, w repozytorium git. Plusy: łatwe zmiany wymiarów, generowanie STL/STEP, automatyczne testy kolizji i mas, wersjonowanie.

Zakres, który przygotuję:
1. **Konstrukcja nośna:** żebra tułowia, miednica, uda, golenie, stopy, szyja, mocowania siłowników z tolerancjami pod FDM.
2. **Skorupa T-800:** czaszka z oczodołami i otworami na diody, żebra „endoszkieletu”, osłony rąk, wszystko jako moduły do przykręcenia.
3. **Modele do symulacji:** URDF/MJCF z masami i bezwładnościami z CAD, żeby polityka chodu uczyła się na wiernym modelu.
4. **Reguły druku:** orientacja pod obciążenie, grubość ścian (3–4 linie), wkładki gwintowane M3/M4 zamiast gwintów w tworzywie, PA-CF/PETG-CF dla elementów nośnych, PLA/PETG tylko dla skorupy.
5. **Podgląd:** renderowanie STL do PNG w Pythonie, żebym mógł ocenić proporcje przed drukiem. Zdjęcia wydruków i pomiary od ciebie zamykają pętlę.

Ty możesz równolegle używać Fusion 360 / Onshape do swobodnego modelowania. Wymieniamy pliki STEP.

## 6. Software (stos)

- **Mózg:** Anthropic SDK (Python), model z narzędziami i wizją; mikrofon → STT (Whisper lokalnie lub chmura), TTS (Piper lokalnie lub chmura).
- **Symulacja i uczenie:** MuJoCo + MuJoCo Playground lub mjlab; dla ramienia biblioteka LeRobot.
- **Pokładowo:** Python 3.11+, opcjonalnie ROS 2, OpenCV, wątek nadzorcy bezpieczeństwa o wyższym priorytecie.
- **Automatyzacja:** n8n (webhooki ze zdarzeniami robota, dzienniki, powiadomienia).
- **Repozytorium (propozycja):** `robot/cad/`, `robot/sim/`, `robot/firmware/`, `robot/brain/`, `robot/docs/` z testami w `robot/tests/`.

## 7. Bezpieczeństwo, prywatność, prawo

- **Fizyczne:** przycisk awaryjny odcinający zasilanie siłowników, ograniczniki prądu, testy nóg na uprzęży/stelażu, żadnych nienadzorowanych testów, baterie LiPo w woreczku ognioodpornym, pole ruchu odgrodzone od ludzi i zwierząt.
- **Prywatność:** kamera i mikrofon wysyłają dane do chmury (API). Informuj domowników, nie kieruj kamery na osoby bez ich zgody.
- **Prawo i znaki towarowe:** wygląd T-800 jest chroniony prawem autorskim i znakami towarowymi. Replika do **osobistego, niekomercyjnego** użytku jest zwykle bezpieczna, ale **nie sprzedawaj** robota ani modeli pod marką filmu i unikaj logotypów **[do weryfikacji z prawnikiem]**.

## 8. Co zrobić w pierwszym tygodniu (bez czekania na drukarkę)

1. Zainstaluj Pythona 3.11+, MuJoCo, SDK Anthropic i załóż klucz API (koszty API są za wywołania, ustaw limit wydatków).
2. Poproś mnie o szkielet repozytorium `robot/brain/` z wirtualnym robotem w MuJoCo i pętlą Claude z narzędziami.
3. Zamów (opcjonalnie) tylko Pi 5 i mikrofon, jeśli chcesz zacząć od sprzętu.
4. Przeczytaj README projektów Open Duck Mini i Berkeley Humanoid Lite, żeby wybrać jeden jako wzorzec.

## 9. Budżet i bramki

Orientacyjnie (moje szacunki, bez drukarki): etap 0: 1–2 tys. zł, etapy 1–2: do 3,5 tys. zł, etap 3: do 2,5 tys. zł, etap 4: 15–20 tys. zł. Przed każdym etapem sprawdzamy bramkę poprzedniego. **Nie kupujemy siłowników etapu 4, dopóki etap 3 nie przeszedł testu chodu.**

## 10. Weryfikacja planu (jak sprawdzić, że działa)

- **Etap 0:** test rozmowy głosowej (opóźnienie), test odmowy niebezpiecznych poleceń, test opisu sceny z kamery.
- **Etap 1:** test obciążeniowy baterii i temperatury, test przycisku awaryjnego.
- **Etap 2:** 3 przedmioty × 10 prób, liczba udanych chwytów.
- **Etap 3:** chód w symulacji (1000 kroków bez upadku) i na robocie (10 m).
- Na każdym etapie: dziennik zdarzeń w n8n, filmy z prób i nagrane logi, które mi pokazujesz do analizy.

## 11. Twoje środowisko (sprawdzone, odczyt tylko)

Komputer, na którym pracuję: **MSI MS-7B09, Windows 11 Home, AMD Ryzen Threadripper 2990WX (Windows pokazuje 8 rdzeni / 16 wątków, procesor ma fizycznie 32 rdzenie, więc coś go ogranicza: tryb BIOS lub licencja), 32 GB RAM, NVIDIA GeForce RTX 2080 Ti z 11 GB VRAM, dyski: C: 182 GB wolne, D: 278 GB wolne, Python 3.14.6.**

Wnioski:
- **GPU wystarczy do treningu polityki chodu w symulacji** (RTX 2080 Ti, 11 GB). Narzędzia typu mjlab wymagają karty NVIDIA [zweryfikowane: [mjlab](https://github.com/mujocolab/mjlab)]. Czas treningu na tej karcie będzie dłuższy niż na nowszych (moje szacunki: godziny zamiast minut), ale to wykonalne.
- **Python 3.14 jest za nowy dla bibliotek robotyki i uczenia (PyTorch, MuJoCo, JAX).** Zainstalujemy równolegle 3.11 lub 3.12 w osobnym środowisku wirtualnym i nie ruszamy systemowego.
- **Windows 11 Home to nie najlepsze środowisko do treningu na GPU.** Zalecam **WSL2 z Ubuntu** (obsługuje CUDA na twojej karcie) lub osobną instalację Linuksa na dysku D:. Do podstaw (Claude, symulacja, CAD) wystarczy Windows.
- **Miejsce:** Isaac Sim i modele zajmują dziesiątki GB. D: (278 GB) jest rozsądnym miejscem na projekt, repozytorium i dane.
- **Ryzyko do sprawdzenia:** powód ograniczenia procesora do 8 rdzeni (nie wpływa na plan, ale spowalnia trening równoległy).
- **MacBook z Windowsem** (wspominasz „2141”): nie wiem, co oznacza ta liczba. Nie mam do niego dostępu z tej sesji. Napisz model i parametry (procesor, RAM), jeśli ma być użyty, np. jako komputer pokładowy do prototypu. Jako komputer pokładowy robota lepsze są Raspberry Pi 5, Jetson lub mini PC niż laptop.

## 12. Otwarte pytania

1. Ile godzin tygodniowo możesz poświęcić na ten projekt (wpływa na tempo etapów)?
2. Czy zaczynamy od symulacji (bez kosztów), czy od zamówienia Pi 5 i mikrofonu?
3. Jaki to dokładnie komputer „MacBook z Windowsem 2141” i czy ma wejść do projektu?
