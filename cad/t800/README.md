# Głowa T-800: model bazowy i przeróbka pod robota

## Źródło i licencja (CC BY-NC-SA)

- Model: **"T-800 Head for a1mini Full size in parts, no stand"**, autor **BumblebeeGTR**
  https://makerworld.com/pl/models/1436143-t-800-head-for-a1mini-full-size-in-parts-no-stand
- Remiks modelu **"T800 Terminator Skull, Bust with stand"**, autor **senfsaft**
  https://makerworld.com/en/models/1057042-t800-terminator-skull-bust-with-stand
  (senfsaft podaje, że pierwotnym autorem jest "Sisco", którego modelu nie ma już w serwisie).
- Licencja: **Creative Commons Uznanie autorstwa - Użycie niekomercyjne - Na tych samych warunkach (CC BY-NC-SA)**.
  Wolno: drukować i przerabiać do użytku osobistego. Nie wolno: sprzedawać wydruków ani plików.
  Jeśli przeróbkę udostępnisz, to na tej samej licencji i z podaniem autorów powyżej.
- Pliki oryginalne: `../ref/t800_a1mini/` (bez zmian, rozpakowane z paczki pobranej 2026-10-08).

## Co tu jest (2026-10-08)

| Plik | Opis |
|---|---|
| `czaszka_ustawiona.stl` | 6 kawałków czaszki złożonych automatycznie z płaszczyzn cięcia; układ: +X przód, +Y lewo, +Z góra, środek pudełka ograniczającego w (0,0,0) |
| `szczeka_ustawiona.stl` | szczęka osadzona na zawiasie (oś Y przez (19,5; -1,7; -64,8)), zamknięta do styku zębów (kąt 25 deg) |
| `transformacje.json`, `orientacja.json`, `szczeka.json` | macierze 4x4: kawałek z pliku -> złożenie -> układ robota |
| `przekroje.png`, `final_*.png` | przekroje wnętrza i podglądy |
| `narzedzia/` | skrypty składania i analizy (uruchamiane `python -I`, bo czytają pobrane pliki) |

Dokładność składania: średnia odległość próbek na płaszczyznach cięcia 0,4-0,6 mm (to głównie gęstość próbkowania;
obrót ograniczony do zachowania osi Y, bo wszystkie cięcia są do niej równoległe). Do weryfikacji wizualnej:
szwy na podglądach się pokrywają.

## Wymiary i miejsce w środku

- Czaszka 216 x 148 x 176 mm; z szczęką 231 mm wysokości. Mieści się w polu P2S (256 mm) nawet w całości.
- Wnętrze ok. 163 x 80 x 118 mm, podłoga ok. z = -40, otwór szyi w podłodze (ok. x = -20).
- Boczne otwory pod ozdobne wkładki: ok. 66 x 87 mm (x = -45..30).
