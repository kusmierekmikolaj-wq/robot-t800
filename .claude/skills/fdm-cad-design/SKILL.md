---
name: fdm-cad-design
description: Projektowanie części robota w CadQuery pod druk FDM na Bambu P2S (tolerancje, ściany, orientacja, wkładki, materiały) i kontrola jakości modelu (szczelność siatki, wymiary, podgląd). Używaj przy każdej nowej części 3D, skorupie T-800 lub zmianie wymiarów.
---

# Projektowanie części pod druk FDM (CadQuery + Bambu P2S)

## Zasady
- Modele tworzymy **jako kod** w `cad/` (CadQuery), parametrycznie: wszystkie wymiary jako nazwane stałe na górze pliku, jednostki w mm.
- Każda część ma funkcję `build(**params) -> cq.Workplane` i skrypt eksportu do `STEP` (do wymiany) i `STL` (do druku).
- Jedna część = jeden plik, nazwa opisuje funkcję (`neck_mount.py`, `skull_shell.py`).

## Wartości startowe (do skalibrowania testowym wydrukiem)
Poniższe liczby to **punkt wyjścia, nie sprawdzone dane dla tej drukarki**. Po pierwszym wydruku testowym (płytka z otworami 2,0–3,5 mm) zapisz poprawki w `cad/tolerancje.md`.
- Luz na pasowanie: ok. 0,2 mm na stronę dla elementów ruchomych, ok. 0,1 mm dla ciasnych.
- Ściany nośne: min. 3 linie (ok. 1,2 mm przy dyszy 0,4); skorupa dekoracyjna: 2 linie.
- Otwory pod wkładki gwintowane M3: dobrać do wkładki z karty producenta, nie zgadywać.
- Mostki i nawisy: unikaj nawisów powyżej 45°; dziel część tak, by płaska ściana leżała na stole.
- Orientacja druku: warstwy **prostopadle** do kierunku głównego obciążenia rozciągającego (warstwy są najsłabsze); elementy nośne drukuj tak, by siła nie rozwarstwiała.

## Materiały (P2S, pasywna komora)
- Skorupa i obudowy: PLA lub PETG (PETG-CF dla większej sztywności).
- Elementy nośne i przekładnie: PETG-CF / PET-CF; PA-CF tylko małe części (komora pasywna, nylon wymaga suszenia).
- Wnętrze nagrzewające się lub na zewnątrz: ASA.

## Kontrola jakości po wygenerowaniu (zawsze)
1. Eksport STL i wczytanie w `trimesh`: `is_watertight` musi być `True`.
2. Porównaj `extents` i objętość z oczekiwaniami z parametrów (różnica > 1% = błąd modelu).
3. Wyrenderuj podgląd PNG (matplotlib, `Agg`) i obejrzyj przed drukiem.
4. Zapisz masę (objętość × gęstość materiału) do `cad/masy.csv`, bo trafia do modelu MuJoCo.

## Szablon kontroli (działa w środowisku projektu)
```python
import cadquery as cq, trimesh
part = cq.Workplane("XY").box(120, 100, 140)          # przykład
cq.exporters.export(part, "out.stl", tolerance=0.1)
m = trimesh.load("out.stl")
assert m.is_watertight
print(m.extents, m.volume)
```
Środowisko: `C:\Users\Jeff\.venvs\robot\Scripts\python.exe`.

## Czego nie robić
- Nie projektuj z logotypami ani znakami towarowymi filmu (replika do użytku osobistego).
- Nie ufaj podglądowi zamiast pomiaru: po wydruku mierz suwmiarką i aktualizuj tolerancje.
