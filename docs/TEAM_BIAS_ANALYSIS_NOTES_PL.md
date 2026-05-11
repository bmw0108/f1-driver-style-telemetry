# Analiza biasu w strone zespolu - notatki

## Dlaczego ten test jest wazny

Glowny problem metodologiczny: model rozpoznajacy kierowce moze czesciowo rozpoznawac nie kierowce, tylko samochod lub zespol.

To jest szczegolnie wazne w Formule 1, bo:

- kazdy zespol ma inna charakterystyke samochodu,
- roznice w predkosci maksymalnej, przyspieszeniu, stabilnosci i pracy ukladu napedowego moga byc widoczne w telemetrii,
- czesc kierowcow przez dlugi czas jezdzi w jednym zespole,
- czas okrazenia i predkosci moga latwo przenosic informacje o sile samochodu, a nie tylko o stylu jazdy.

## Co sprawdzono

Dodano pierwszy kontrolny eksperyment:

- predykcja zespolu (`Team`) na podstawie tych samych cech telemetrycznych,
- walidacja grupowana po sesji,
- trzy warianty cech:
  - wszystkie cechy telemetryczne,
  - bez bezposrednich cech czasowych,
  - rdzen stylu bez czasu i kontekstu wyscigowego,
- dodatkowo testy "ten sam zespol, rozni kierowcy".

Skrypt:

- `06_team_bias_and_team_signature_analysis.py`

Eksporty:

- `exports/team_bias_driver_team_coverage.csv`
- `exports/team_bias_team_classification_summary.csv`
- `exports/team_bias_same_team_driver_summary.csv`

## Wynik 1: zespol da sie przewidywac z telemetrii

Wyniki klasyfikacji zespolu regresja logistyczna:

| Setup | Najlepszy wariant cech | Accuracy | Macro F1 |
|---|---:|---:|---:|
| Kwalifikacje 2018-2025 | style core bez czasu i kontekstu | 0.871 | 0.788 |
| Wyscigi 2025 | wszystkie / bez czasu bardzo podobnie | 0.832 | 0.824 |
| Kwalifikacje 2023-2025 | style core bez czasu i kontekstu | 0.750 | 0.734 |

Najwazniejsza obserwacja: zespol jest przewidywalny nawet po usunieciu cech czasowych. To znaczy, ze w samej telemetrii istnieje silny podpis samochodu/zespolu.

To jest istotne ograniczenie dla interpretacji modelu kierowcy. Nie mozna twierdzic, ze model kierowcy uczy sie wylacznie stylu jazdy. Czesciowo moze korzystac z charakterystyki samochodu.

## Wynik 2: driver signal nie znika po kontroli zespolu

Najwazniejszy test kontrolny to rozroznienie kierowcow w tym samym zespole.

### Ferrari 2025: Hamilton vs Leclerc

Setup:

- tylko wyscigi 2025,
- tylko Ferrari,
- kierowcy: `HAM` i `LEC`,
- liczba okrazen: `1742`,
- ten sam zespol, ten sam sezon.

Wynik:

- style core bez czasu i kontekstu: accuracy `0.882`, macro F1 `0.882`.

To jest bardzo wazny wynik. Skoro model potrafi dobrze rozroznic `HAM` i `LEC` w tym samym Ferrari, to znaczy, ze przynajmniej w tym przypadku rozpoznawanie kierowcy nie jest tylko rozpoznawaniem zespolu.

### Ferrari 2023-2024: Leclerc vs Sainz

Setup:

- kwalifikacje 2023-2025,
- tylko Ferrari,
- kierowcy: `LEC` i `SAI`,
- liczba okrazen: `87`.

Wynik:

- style core bez czasu i kontekstu: accuracy `0.874`, macro F1 `0.861`.

Ten wynik jest obiecujacy, ale trzeba go interpretowac ostrozniej, bo probek jest znacznie mniej.

### Ferrari 2018-2025: Leclerc, Sainz, Hamilton

Setup:

- kwalifikacje 2018-2025,
- tylko Ferrari,
- kierowcy: `LEC`, `SAI`, `HAM`,
- liczba okrazen: `219`.

Wynik:

- no time / style core: accuracy `0.854`, macro F1 `0.746`.

Tu accuracy jest wysokie, ale macro F1 nizsze przez nierowny rozklad klas, zwlaszcza mala liczbe okrazen Hamiltona w Ferrari w tym zbiorze.

## Interpretacja

Wyniki pokazuja dwie rzeczy naraz:

1. Bias zespolowy istnieje i jest silny.
2. Sygnał kierowcy nadal istnieje po ograniczeniu danych do jednego zespolu.

To jest bardzo dobra sytuacja do pracy, bo nie trzeba udawac, ze problemu nie ma. Mozna pokazac, ze:

- model kierowcy moze korzystac zarowno z cech stylu jazdy, jak i cech samochodu,
- dlatego nalezy kontrolowac zespol jako potencjalne zrodlo biasu,
- testy wewnatrz Ferrari wskazuja jednak, ze kierowcy pozostaja rozroznialni nawet przy stalym zespole.

## Jak to mozna opisac w pracy

Roboczy wniosek:

"Poniewaz samochod w Formule 1 jest silnym elementem kontekstu, sprawdzono, czy te same cechy telemetryczne pozwalaja przewidywac nie tylko kierowce, lecz takze zespol. Wyniki potwierdzily, ze w telemetrii istnieje wyrazny podpis zespolu: klasyfikacja zespolu osiagnela macro F1 od ok. 0.73 do 0.82 w zaleznosci od setupu, nawet po usunieciu bezposrednich cech czasowych. Oznacza to, ze interpretacja modeli kierowcy musi uwzgledniac potencjalny bias zwiazany z konstrukcja samochodu. Jednoczesnie testy przeprowadzone wewnatrz jednego zespolu, szczegolnie dla pary Hamilton-Leclerc w Ferrari 2025, pokazaly, ze kierowcy nadal sa dobrze rozroznialni na podstawie telemetrii. Sugeruje to, ze model nie uczy sie wylacznie charakterystyki zespolu, ale wychwytuje rowniez indywidualne wzorce prowadzenia."

## Co warto sprawdzic dalej

- Dodac confusion matrix dla predykcji zespolu.
- Sprawdzic, ktore cechy najmocniej przewiduja zespol.
- Porownac predykcje kierowcy z predykcja zespolu na tych samych wariantach cech.
- Zbudowac wariant finalnego modelu kierowcy tylko na parach lub grupach kierowcow z tego samego zespolu.
- Dla kierowcow, ktorzy zmieniali zespoly (`SAI`, `OCO`, `HAM`, `LEC`), sprawdzic, czy model rozpoznaje kierowce po zmianie zespolu.

## Aktualizacja: interpretacja cech zespolowych

Dodano osobna notatke:

- `TEAM_SIGNATURE_REALITY_COMPARISON_PL.md`

Najwazniejsze nowe obserwacje:

- `Red Bull Racing` w setupie wyscigowym 2025 ma podpis zgodny z opisami zewnetrznymi: wysoka predkosc srednia/minimalna, wysoki udzial pelnego gazu, niski udzial sredniego gazu i niska aktywnosc hamowania.
- `Ferrari` jest rozpoznawane raczej przez profil gazu i predkosci niz przez sama predkosc maksymalna; zgodnosc z opisami SF-25 jest czesciowa.
- `Williams` ma bardzo widoczny podpis wysokich predkosci maksymalnych/gornych percentyli, co pasuje do obrazu auta mocniejszego w szybkich fragmentach, ale niekoniecznie dominujacego w calym okrazeniu.
- `Haas` ma bardziej zmienny profil predkosci i wieksza aktywnosc hamowania; mozna to ostroznie zestawic z publicznie opisywanymi problemami stabilnosci, ale to nie jest tak mocny przypadek jak Red Bull.
- W Ferrari 2025 model rozroznia `HAM` i `LEC` glownie po gazie, biegach, RPM i hamowaniu. Jest to zgodne z publicznym obrazem Hamiltona adaptujacego sie do SF-25 oraz Leclerca preferujacego bardziej "pointy", trudniejszy setup.
