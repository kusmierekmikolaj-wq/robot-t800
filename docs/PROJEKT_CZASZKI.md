# Projekt głowy robota (czaszka w stylu T-800), etap 0

Stan na 2026-10-08. Plan konstrukcji przed modelowaniem. Oznaczenia: **[zweryfikowane]**, **[szac.]** (moje oszacowanie), **[do weryfikacji]**.
Wygląd to **oryginalny projekt inspirowany endoszkieletem**, nie kopia modelu z filmu (tylko użytek osobisty, patrz PLAN_BUDOWY.md, sekcja 7).

## 1. Ograniczenia, z których wynika podział na części

- **Pole robocze P2S: 256 x 256 x 256 mm** [zweryfikowane: oferty Micro Center; strony Bambu nie widziałem]. Bezpieczny rozmiar części: **najdłuższy wymiar do 220 mm**, bo przy krawędziach stołu bywa gorsza jakość [do weryfikacji dla P2S].
- Czaszka w skali 1,15 dorosłej (patrz parametr `S`): ok. 230 x 175 x 215 mm razem ze szczęką. W całości się zmieści, ale **drukowanie w kawałkach jest lepsze**: mniej podpór wewnątrz, dostęp do elektroniki, łatwa wymiana uszkodzonej części, każdy kawałek można drukować innym materiałem.
- Wnętrze musi pomieścić elektronikę i ruchome elementy, więc projektuję **od wnętrza na zewnątrz**: najpierw "obwiednie" (bryły zajmowane przez podzespoły i zakres ich ruchu), potem skorupa wokół nich.

## 2. Moduły (każdy to osobny plik STL i osobny wydruk)

| Moduł | Rola | Rozmiar [szac.] | Materiał startowy |
|---|---|---|---|
| **M1 Tył czaszki** | skorupa tylna i górna, mocowanie głośnika, wentylacja | ok. 190 x 170 x 150 | PLA, potem PETG |
| **M2 Twarz** | przód: oczodoły, kości policzkowe, nos, mocowanie kamery, gniazda oczu | ok. 170 x 150 x 110 | PLA |
| **M3 Szczęka** | ruchoma żuchwa na dwóch osiach (zawias), ramię od serwa | ok. 130 x 120 x 70 | PETG (zawias obciążony) |
| **M4 Tacka elektroniki** | wysuwana płyta z Pi 5, płytką serw, mikrofonem; wyjmujesz całość przez otwór z tyłu | ok. 120 x 90 x 40 | PLA/PETG |
| **M5 Szyja: tilt** | wspornik pochylenia głowy, serwo tilt blisko środka masy | ok. 100 x 80 x 80 | PETG |
| **M6 Szyja: pan i podstawa** | obrót w poziomie, ciężka płaska podstawa z otworami do przykręcenia do biurka | ok. 140 x 140 x 70 | PETG |
| **M7 Oczy (2 szt.)** | uchwyt diody, dyfuzor, wciskany od środka | ok. 25 x 25 x 20 | PLA przezroczysty/biały |
| **M8 Pokrywa tylna** | zamyka otwór po tacce, kanał na kable | ok. 100 x 80 x 6 | PLA |

Elementy ozdobne (żebra, blizny, "zęby", panele) dodajemy na końcu jako **nakładki**, żeby zmiany wyglądu nie wymagały przeprojektowania konstrukcji.

```
        [M7 oczy]
  M1 tył  <--śruby M3--> M2 twarz
      |                     |
   M4 tacka          M3 szczęka (zawias)
      |_____________________|
                |
        M5 tilt  -> M6 pan + podstawa
```

## 3. Ruch i stopnie swobody

| Oś | Zakres | Napęd | Etap 0 |
|---|---|---|---|
| Pan (obrót w poziomie) | -90..90 deg (jak w symulacji i nadzorcy) | serwo magistralowe | tak |
| Tilt (pochylenie) | -30..40 deg (jak w symulacji i nadzorcy) | serwo magistralowe | tak |
| Szczęka | 0..20 deg [szac.] | mikroserwo | **mechanizm przygotowany, serwo opcjonalnie** |
| Oczy | świecenie (wył./czerwone/bursztyn/niebieskie) | dioda RGB lub czerwona | tak, bez ruchu gałek |

Zasady konstrukcyjne:
- **Oś tilt przechodzi blisko środka masy głowy**, żeby serwo nie walczyło z ciężarem i nie nagrzewało się w bezruchu. Układ liczę w kodzie (masa i środek masy z modelu) i dobieram przeciwwagę lub położenie osi.
- **Ograniczniki mechaniczne** zawężone o kilka stopni względem limitów nadzorcy (zasada: nadzorca zatrzyma ruch, zanim dojdzie do ogranicznika).
- **Punkty przycięcia palców** (zawias szczęki, obrót szyi) mają szczeliny większe niż 8 mm albo osłony; w nadzorcy dodamy limit momentu.
- **Moment serwa:** głowa ok. 0,7-1,0 kg [szac.] przy ramieniu środka masy do 3 cm to kilka kg·cm, a serwa klasy STS3215 mają ok. 20-30 kg·cm [do weryfikacji w karcie katalogowej]. Zapas wystarczający, o ile równowaga jest dobra.

## 4. Elektronika i obwiednie w modelu

| Podzespół | Wymiar [szac./z katalogu, do weryfikacji] | Gdzie |
|---|---|---|
| Raspberry Pi 5 + radiator | 85 x 56 x 25 mm | M4 tacka |
| Kamera Pi v3 | 25 x 24 x 12 mm | M2, między oczodołami lub w jednym oczodole |
| Mikrofon (reSpeaker 2-mic lub USB) | do 65 x 30 x 15 mm | M4 lub M1, z otworami w skorupie |
| Głośnik 40 mm | Ø40 x 15 mm | M1, otwór kratkowy z tyłu/po bokach |
| Serwo magistralowe (np. Feetech STS3215 lub Dynamixel AX-12A) | ok. 45 x 25 x 35 mm | M5, M6 |
| Płytka sterownika serw | 40 x 25 x 10 mm | M4 |
| Zasilacz 5 V/5 A + 7-12 V dla serw | poza głową, w podstawie lub na zewnątrz | M6 lub na biurku |
| Diody oczu | Ø5-8 mm | M7 |

W kodzie każdy podzespół to parametr (długość, szerokość, wysokość, punkty mocowania), więc zmiana serwa lub płytki to zmiana liczby, nie przeróbka modelu.

## 5. Zasady druku i montażu

- **Połączenia:** wkładki gwintowane **M3** wtapiane lutownicą (nie gwint w tworzywie). Śruby M3 x 8 i M3 x 12, ewentualnie M2.5 dla elektroniki.
- **Ściany:** min. 2,4 mm (6 linii przy dyszy 0,4); elementy nośne 3-4 mm i 4 ściany + 25-40% wypełnienia.
- **Dopasowania (wartości startowe, kalibrujemy testem):** luz ślizgowy 0,2 mm, wcisk 0,10-0,15 mm, otwór na śrubę M3 3,3 mm, na wkładkę M3 ok. 4,0-4,2 mm (zależnie od wkładki).
- **Test przed wszystkim:** pierwszy wydruk to **plansza testowa tolerancji** (otwory, wkładki, zawias, zatrzask), 15-30 min. Z jej wyniku poprawiamy parametry, dopiero potem drukujemy moduły.
- **Orientacja:** M1 i M2 otworem do góry lub twarzą w dół z drzewem podpór w oczodołach; zawias M3 drukowany tak, żeby warstwy nie rozwarstwiały osi; wszystko, co przenosi obciążenie, ma warstwy równoległe do siły.
- **Podpory:** projektuję tak, żeby jak najwięcej było bez podpór (kąty do 45-50 deg, fazy zamiast poziomych nawisów).
- **Montaż w kolejności:** M6 -> M5 -> test ruchu pustej szyi -> M4 z elektroniką -> M1 -> M2 -> M3 -> M7 -> M8. Najpierw sprawdzamy ruch bez skorupy, potem zamykamy.
- **Serwisowalność:** wszystko wymienne bez rozkręcania pozostałych modułów; kable idą kanałem przez szyję, z zapasem na pełny obrót.

## 6. Jak będę to weryfikować (bez drukarki)

Kod: `robot/cad/`. Pierwsza wersja czaszki z prostych brył (CadQuery) została usunięta 2026-10-10 (jest w historii Git, commit e514dbd); bazą jest teraz model z `cad/t800/`. Automatyczne kontrole, uruchamiane testami:
1. Każdy STL jest szczelny, ma objętość większą od zera, a bbox nie przekracza 220 mm.
2. **Brak niezamierzonych kolizji** w złożeniu (przecięcia brył CadQuery poza wyznaczonymi stykami).
3. **Brak kolizji w pełnym zakresie ruchu**: obracam model w krokach przez pan -90..90 i tilt -30..40 i sprawdzam przecięcia.
4. Obwiednie podzespołów mieszczą się w swoich gniazdach z zapasem min. 1 mm.
5. Masa i środek masy z modelu (gęstość PLA ok. 1,24 g/cm3 skorygowana o wypełnienie [szac.]).
6. Podgląd PNG z 4 stron + przekrój przez środek, żebym widział wnętrze.

Ograniczenia, o których pamiętam: nie sprawdzę jakości druku, wytrzymałości w praktyce ani luzów po druku. To zamykają twoje zdjęcia, pomiary suwmiarką i plansza testowa.

## 7. Kolejność prac

1. Plansza tolerancji (można zrobić od razu, drukuje się po dotarciu P2S).
2. M6 + M5 (szyja) razem z modelem do symulacji, żeby zgrać z istniejącym `head.xml`.
3. M4 tacka z obwiedniami elektroniki.
4. M1 + M2 skorupa, M7 oczy, M8 pokrywa.
5. M3 szczęka.
6. Nakładki ozdobne, malowanie (efekt metalu: podkład + farba srebrna/stalowa + przecierka).

## 8. Decyzje do potwierdzenia

| Decyzja | Moja propozycja |
|---|---|
| Skala | 1,15 czaszki dorosłego (zapas na elektronikę), parametr `S` do zmiany |
| Serwa szyi | magistralowe z odczytem pozycji (STS3215 lub AX-12A, kupujemy po zatwierdzeniu wymiarów) |
| Szczęka w etapie 0 | mechanizm tak, serwo opcjonalne na później |
| Oczy | stałe, świecące (bez ruchomych gałek), wymienny dyfuzor |
| Materiał startowy | PLA do dopasowań i prób, PETG dla szyi i zawiasu |
| Podstawa | ciężka, przykręcana do blatu/płyty (bez ryzyka przewrócenia) |
