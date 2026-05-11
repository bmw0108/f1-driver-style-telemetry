# Porownanie cech zespolow z wiedza zewnetrzna

## Po co jest ten plik

Ten plik zapisuje kolejna wazna obserwacje metodologiczna: skoro model potrafi przewidywac zespol na podstawie telemetrii, trzeba sprawdzic, jakie cechy za tym stoja i czy maja sens w realiach Formuly 1.

To jest osobny temat od predykcji kierowcy. W praktyce analizujemy dwa pytania:

1. Czy w telemetrii istnieje "podpis zespolu/samochodu"?
2. Czy kierowcow da sie rozroznic takze wtedy, gdy kontrolujemy zespol, czyli porownujemy ich w tym samym samochodzie?

## Najwazniejsze pliki

Skrypt:

- `06_team_bias_and_team_signature_analysis.py`

Eksporty:

- `exports/team_bias_team_classification_summary.csv`
- `exports/team_bias_team_feature_importance.csv`
- `exports/team_bias_same_team_driver_summary.csv`
- `exports/team_bias_same_team_driver_feature_importance.csv`
- `exports/team_bias_group_feature_means.csv`

## Wynik ogolny

Zespol da sie przewidywac z telemetrii dosc dobrze:

- kwalifikacje `2018-2025`: najlepszy wariant macro F1 ok. `0.788`,
- wyscigi `2025`: najlepszy wariant macro F1 ok. `0.824`,
- kwalifikacje `2023-2025`: najlepszy wariant macro F1 ok. `0.734`.

Co wazne, wynik pozostaje wysoki nawet po usunieciu bezposrednich cech czasowych. To oznacza, ze w danych jest realny podpis samochodu/zespolu, a nie tylko informacja typu "kto byl szybszy na okrazeniu".

## Cechy rozrozniajace zespoly w setupie wyscigowym 2025

Najbardziej czytelny do interpretacji jest setup wyscigowy `2025`, bo obejmuje jeden sezon i cztery zespoly:

- `Ferrari`,
- `Haas F1 Team`,
- `Red Bull Racing`,
- `Williams`.

### Red Bull Racing

W danych `Red Bull Racing` odroznial sie m.in. przez:

- wysoka srednia predkosc (`speed_mean`),
- najwyzsza minimalna predkosc w okrazeniu (`speed_min`),
- najwyzszy udzial pelnego gazu (`throttle_full_frac`),
- najnizszy udzial sredniego gazu (`throttle_mid_frac`),
- najnizsza aktywnosc hamowania (`brake_active_frac`, `brake_on_count`),
- niski `gear_mean` i malo zmian biegow.

To dobrze pasuje do zewnetrznych opisow RB21. Autosport opisuje, ze Red Bull ma wysoki sufit osiagow, szczegolnie w srednio- i szybkich zakretach, ale wymaga specyficznego sposobu jazdy. W tym samym materiale podkreslono, ze samochod wymaga utrzymywania wyzszych predkosci minimalnych i zdecydowanego operowania gazem.

Ocena: zgodnosc mocna. Model widzi Red Bulla przez cechy zwiazane z utrzymaniem predkosci, mocniejszym powrotem do gazu i mniejsza liczba faz posrednich. To jest spojne z publicznym opisem samochodu o wysokim potencjale, ale trudnym oknie pracy.

### Ferrari

W setupie wyscigowym 2025 `Ferrari` bylo rozpoznawane glownie przez:

- wysoki `throttle_mean`,
- wysoki `throttle_mid_frac`,
- niski `throttle_zero_frac`,
- relatywnie nizszy `throttle_full_frac`,
- wysoka srednia predkosc,
- cechy zmiennosci predkosci.

Zewnetrzne zrodla wskazuja, ze SF-25 mial dobra predkosc na prostych, ale tracil w zakretach i mial problem ze znalezieniem stabilnego kompromisu ustawien. Motorsport pisal po Miami 2025, ze sama predkosc na prostych nie wystarczala, bo Ferrari tracilo zbyt duzo w zakretach i mialo trudnosci z optymalnym oknem pracy.

Ocena: zgodnosc czesciowa. Nasze dane nie mowia po prostu "Ferrari = najwyzsza predkosc maksymalna". Raczej wskazuja na profil z wiekszym udzialem sredniego gazu i mniejsza liczba pelnych odjec gazu. To moze pasowac do obrazu samochodu, ktory nie pozwala tak jednoznacznie przechodzic do pelnego gazu jak Red Bull, ale nadal utrzymuje wysokie tempo srednie.

### Williams

W danych `Williams` mial:

- najwyzsze `speed_max`,
- najwyzsze `speed_q90`,
- wysokie `gear_mean`,
- nizsza srednia predkosc niz Ferrari i Red Bull,
- nizszy `throttle_mean` niz Ferrari i Red Bull.

Zewnetrzne zrodla Formula1.com wskazywaly, ze Williams w FW47 celowal w lepszy docisk w szybkich partiach i szersze okno balansu miedzy wolnymi i szybkimi zakretami. Motorsport cytowal Albona, ktory mowil, ze auto stalo sie mniej nerwowe, bardziej przewidywalne i latwiejsze do jazdy na limicie. RaceFans klasyfikowal Williamsa jako szosty najszybszy samochod sezonu 2025, mimo ze zespol skonczyl wyzej w tabeli konstruktorow.

Ocena: zgodnosc umiarkowana. Najbardziej pasuje wysoka predkosc maksymalna i gorne percentyle predkosci, ale srednia predkosc nie jest tak wysoka jak u topowych zespolow. To sugeruje, ze podpis Williamsa w modelu moze byc bardziej "szybkie fragmenty / wysokie biegi" niz ogolna dominacja tempa.

### Haas F1 Team

W danych `Haas` odroznial sie przez:

- wysoka zmiennosc predkosci (`speed_std`),
- wysoka aktywnosc hamowania (`brake_active_frac`, `brake_on_count`),
- wysoka liczbe zmian biegow,
- relatywnie nizszy `speed_mean`.

Zewnetrznie Haas VF-25 byl opisywany jako samochod z problemami stabilnosci w szybkich zakretach. Motorsport cytowal Ayao Komatsu, ktory mowil o problemach z wysokopredkosciowa niestabilnoscia i trudnoscia przewidywania, kiedy problem sie pojawi. Formula1.com pisalo, ze Haas chcial poprawic aero i adaptowalnosc samochodu do torow o roznych charakterystykach.

Ocena: zgodnosc czesciowa. Wysoka zmiennosc predkosci oraz wieksza aktywnosc hamowania moga pasowac do samochodu mniej stabilnego i bardziej wymagajacego w roznych fazach okrazenia, ale nie jest to tak jednoznaczny przypadek jak Red Bull.

## Test wewnatrz jednego zespolu: Ferrari 2025, Hamilton vs Leclerc

Najwazniejszy test kontrolny to `HAM` vs `LEC` w Ferrari 2025:

- ten sam zespol,
- ten sam sezon,
- `1742` okrazenia,
- predykcja kierowcy na podstawie rdzenia cech bez czasu i kontekstu,
- accuracy `0.882`,
- macro F1 `0.882`.

To pokazuje, ze sygnal kierowcy nie znika po kontroli zespolu.

### Jak model odroznial Hamiltona i Leclerca

Srednie cechy w Ferrari 2025:

- `LEC` mial wyzszy udzial pelnego gazu (`throttle_full_frac`: ok. `0.526` vs `0.413` u `HAM`),
- `LEC` mial nizszy udzial sredniego gazu (`throttle_mid_frac`: ok. `0.335` vs `0.434` u `HAM`),
- `LEC` mial nizszy udzial jazdy bez gazu (`throttle_zero_frac`: ok. `0.140` vs `0.153` u `HAM`),
- `LEC` mial wyzszy `rpm_mean`,
- `HAM` mial wyzszy `brake_active_frac`,
- `HAM` mial wyzszy `gear_mean`, ale mniej zmian biegow.

Interpretacja:

- `LEC` wyglada bardziej zdecydowanie po stronie przechodzenia do pelnego gazu,
- `HAM` czesciej przebywa w srednim zakresie przepustnicy i ma wyzszy udzial aktywnego hamowania,
- roznica nie sprowadza sie do zespolu, bo obaj kierowcy jechali Ferrari.

Zewnetrznie Formula1.com pisalo, ze Hamilton mial trudnosci z adaptacja do Ferrari i ze glowne roznice dotyczyly hamowania oraz wejscia w zakret. Autosport opisywal, ze Leclerc poszedl w bardziej ekstremalny, bardziej "pointy" setup, ktory jest trudniejszy, ale pozwala mu wydobywac wiecej z auta, podczas gdy Hamilton preferuje bardziej przewidywalny i stabilny tyl.

Ocena: zgodnosc mocna. Nasze dane pokazuja, ze Leclerc w tym samym Ferrari czesciej dochodzi do pelnego gazu i ma bardziej zdecydowany profil przepustnicy, a Hamilton ma bardziej posredni profil gazu i wiekszy udzial hamowania. To pasuje do zewnetrznego obrazu roznic w adaptacji do SF-25.

## Wazne zastrzezenie o wspolczynnikach modelu

Wspolczynniki regresji logistycznej sa liczone po standaryzacji i przy wielu skorelowanych cechach. Dlatego nie nalezy interpretowac pojedynczego wspolczynnika jako prostego zdania "wiecej tej cechy zawsze oznacza ten zespol". Bezpieczniejsza interpretacja laczy:

- ranking cech modelu,
- srednie wartosci cech dla zespolow/kierowcow,
- wiedze zewnetrzna o samochodach i kierowcach.

## Wniosek do zapamietania

Analiza biasu zespolowego wzmacnia prace, bo pokazuje dwa fakty jednoczesnie:

1. Samochod/zespol ma w telemetrii wyrazny podpis i moze byc zrodlem biasu.
2. Kierowcow nadal da sie rozrozniac w tym samym zespole, wiec model nie sprowadza sie wylacznie do rozpoznawania samochodu.

Najmocniejsze "pewniaki" na tym etapie:

- Red Bull: zgodnosc miedzy wysokimi predkosciami minimalnymi, pelnym gazem i publicznym opisem RB21 jako samochodu o wysokim potencjale, wymagajacego odwaznej jazdy.
- Ferrari `HAM` vs `LEC`: zgodnosc miedzy roznicami w gazie/hamowaniu w danych a publicznie opisywana adaptacja Hamiltona i bardziej "pointy" podejsciem Leclerca.

## Zrodla

- Autosport, 1 kwietnia 2025, o charakterystyce Red Bulla RB21 i Racing Bulls:
  - https://www.autosport.com/f1/news/racing-bulls-car-might-be-easier-to-handle-but-red-bulls-rb21-offers-bigger-rewards-for-bravery/10708665/
- Motorsport, 3 maja 2025, o problemach Haasa z wysokopredkosciowa niestabilnoscia:
  - https://www.motorsport.com/f1/news/the-surprise-factor-holding-haas-f1-team-back-at-race-weekends/10719223/
- Formula1.com, 20 lutego 2025, analiza techniczna Haas VF-25:
  - https://www.formula1.com/en/latest/article/tech-analysis-whats-changed-with-haas-vf-25-and-are-they-set-for-a-massive.nymZx9e5kZuUeKnxX2hh9
- Motorsport, 4 maja 2025, o Ferrari SF-25: dobra predkosc na prostych, straty w zakretach:
  - https://es.motorsport.com/f1/news/analisis-ferrari-miami-velocidad-recta-pierden-decimas-curvas/10719793/
- Formula1.com, 14 lutego 2025, analiza Williams FW47:
  - https://www.formula1.com/en/latest/article/tech-analysis-the-gains-williams-are-targeting-with-the-new-fw47.6AftD0iRAiKGPtq5GrIxLY
- Motorsport, 1 maja 2025, o bardziej przewidywalnym Williamsie FW47:
  - https://www.motorsport.com/f1/news/less-snappy-more-predictable-car-helps-williams-to-best-f1-start-in-nine-years/10718487/
- RaceFans, 29 grudnia 2025, ranking samochodow F1 2025:
  - https://www.racefans.net/2025/12/29/the-formula-1-cars-of-2025-ranked-from-slowest-to-fastest/
- Formula1.com, 13 maja 2025, o roznicach Hamilton-Leclerc w Ferrari:
  - https://www.formula1.com/en/latest/article/tech-weekly-the-key-differences-between-how-hamilton-and-leclerc-are-driving.6bJgv5Kb4PrIYHBKUDoxwT
- Autosport, 2 maja 2025, o bardziej ekstremalnym setupie Leclerca:
  - https://www.autosport.com/f1/news/leclerc-extreme-set-up-changes-make-ferrari-f1-car-trickier-but-faster/10718754/
