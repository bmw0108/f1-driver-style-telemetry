# Methodology Decisions

## Ogolne zasady

- Projekt jest data-first.
- Nie nalezy wyciagac wnioskow bez pokrycia w danych lub w eksportach.
- Kazdy etap powinien byc mozliwy do zweryfikowania zewnetrznie przez CSV albo gotowy skrypt.

## Dlaczego nie "przewidywanie zwyciezcy"

Odrzucono pomysl prostego modelu przewidujacego zwyciezce, bo:

- bylby mniej oryginalny,
- mocno mieszalby styl kierowcy z forma zespolu i przebiegiem wyscigu,
- slabiej nadawalby sie do interpretacji behawioralnej.

Wybrany kierunek:

- identyfikacja stylu jazdy kierowcy na podstawie telemetrii.

## Dlaczego kwalifikacje jako punkt wyjscia

Kwalifikacje byly pierwszym setupem, bo:

- kierowcy jada blizej limitu,
- jest mniej ruchu na torze,
- sygnal stylu jest czystszy niz w wyscigu,
- latwiej uzasadnic metodologicznie analize zachowania kierowcy.

## Podstawowe filtry danych

W kwalifikacjach stosowano:

- tylko sesje kwalifikacyjne,
- tylko warunki suche,
- `LapTime` niepuste,
- `IsAccurate == True`,
- `TrackStatus == 1`,
- brak usunietych lub sztucznie wygenerowanych okrazen,
- osobny wariant: tylko okrazenia oznaczone jako personal best.

W wyscigach 2025 stosowano:

- tylko warunki suche,
- `LapTime` niepuste,
- `IsAccurate == True`,
- `TrackStatus == 1`,
- bez pit-in i pit-out,
- wstepny filtr stabilnosci: okrazenie w granicy `2s` od mediany lokalnego stintu.

## Dlaczego "one best lap per driver per session"

We wczesnej fazie projektu przyjeto jedno reprezentatywne okrazenie na kierowce na sesje, bo:

- zmniejsza to duplikacje bardzo podobnych probek,
- daje czystszy i bardziej defensywny setup,
- latwiej uzasadnic, ze porownujemy reprezentatywne przejazdy, a nie wiele bardzo podobnych probek z jednej sesji.

## Dlaczego najpierw 2023-2025, a potem 2018-2025

Najpierw wykorzystano `2023-2025`, bo:

- te sezony byly juz lokalnie dostepne,
- latwiej bylo szybko zbudowac pelny proces i sprawdzic, czy pomysl dziala.

Pozniej rozszerzono projekt do `2018-2025`, bo:

- FastF1 daje stabilne dane nowoczesnej ery od 2018,
- potrzebne bylo zwiekszenie liczby probek,
- chcielismy sprawdzic, czy wzorce kierowcow przetrwaja w dluzszym horyzoncie sezonow i roznych generacjach samochodow.

## Jak wybierano kierowcow

Nie wybierano kierowcow "na wyczucie".

Stosowana logika:

1. najpierw sprawdzic pokrycie sezonowe i liczbe dostepnych okrazen,
2. zbudowac kandydacki zbior kierowcow z mocnym pokryciem,
3. sprawdzic rozroznialnosc kierowcow w modelu bazowym,
4. wybrac podzbior, ktory dobrze laczy pokrycie danych i rozroznialnosc.

W praktyce:

- dla krotkiego horyzontu wybrano `ALB, SAI, VER, OCO, LEC`,
- dla dlugiego horyzontu wybrano `SAI, VER, LEC, OCO, HAM`.

## Dlaczego walidacja grupowana

Nie stosowac prostego losowego train/test split jako glownego wyniku.

Powod:

- wiele probek pochodzi z tych samych sesji,
- losowy podzial moze dopuscic przeciek informacji miedzy treningiem i testem,
- grouped CV po sesjach lepiej testuje uogolnianie.

Przyjety standard:

- `StratifiedGroupKFold`, grupowanie po sesji.

## Dlaczego regresja logistyczna jest wazna

Regresja logistyczna pelni role modelu bazowego, bo:

- jest interpretowalna,
- jest stabilna,
- dobrze pokazuje, czy w recznie zdefiniowanych cechach istnieje czytelny sygnal rozrozniajacy kierowcow,
- w praktyce okazala sie lepsza od modeli drzewiastych i boostingowych.

## Jak interpretowac modele sekwencyjne

- `CNN` i hybryda nie sa tylko "mocniejszym benchmarkiem", ale dowodem, ze sam przebieg telemetrii zawiera dodatkowy sygnal stylu jazdy.
- Slabe wyniki `GRU` i `LSTM` nie oznaczaja, ze sekwencje sa zle; raczej wskazuja, ze te architektury nie sa tutaj najlepszym wyborem.

## Znane ograniczenia

- Laczenie danych telemetrycznych samochodu i danych pozycyjnych bylo na wczesnym etapie robione przez dopasowanie po kolejnosci wierszy, a nie przez precyzyjne wyrównanie czasowe.
- To wystarcza do analiz na poziomie calego okrazenia, ale nie jest jeszcze gotowe do precyzyjnej segmentacji zakret po zakrecie.
- Setup wyscigowy jest wiekszy, ale bardziej zaszumiony niz setup kwalifikacyjny.
- Wariant `2018-2025` jest metodologicznie mocniejszy, ale trudniejszy przez zmiany samochodow i szerszy kontekst sezonowy.
- Charakterystyka zespolu/samochodu jest realnym zrodlem biasu. Model kierowcy moze czesciowo wykorzystywac podpis samochodu, dlatego trzeba raportowac testy kontrolne zwiazane z predykcja zespolu oraz z rozroznianiem kierowcow w tym samym zespole.
- Model hierarchiczny `Team -> Driver` zostal sprawdzony jako wariant kontrolny. Nie powinien zastapic bezposredniego modelu kierowcy, bo nie poprawil wynikow; jego rola jest pomocnicza i metodologiczna.

## Zrodlo prawdy dla wynikow

Jesli rozmowa i pliki sa niespojne, nalezy wierzyc:

1. plikom CSV w `exports`,
2. skryptom i notebookom, ktore te pliki generuja,
3. dopiero potem opisom w rozmowie albo roboczych notatkach.
