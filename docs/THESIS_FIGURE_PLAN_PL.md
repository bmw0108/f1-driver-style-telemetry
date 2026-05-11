# Plan wykresow do pracy

## Cel

Ten plik opisuje, jakie wykresy warto wykorzystac w pracy i jaka role pelnia w narracji. Chodzi o to, zeby wyniki nie byly tylko tabelami, ale zeby czytelnik widzial:

- jak redukowano dane,
- jak zmienialy sie wyniki modeli,
- jak zachowywalo sie uczenie,
- ktore cechy byly wazne,
- gdzie pojawia sie bias zespolowy,
- czy alternatywne strategie modelowania mialy sens.

Generator:

- `09_thesis_figure_pack.py`

Katalog z figurami:

- `figures/thesis/`

## Rekomendowany zestaw figur

### 1. Redukcja danych po filtrach

Plik:

- `figures/thesis/01a_filter_funnel_qualifying_2023_2025.png`
- `figures/thesis/01b_filter_funnel_qualifying_2018_2025.png`
- `figures/thesis/01c_filter_funnel_race_2025.png`

Rola:

- pokazuje, ile danych tracimy na kolejnych filtrach,
- dobrze pasuje do rozdzialu "Dane i EDA",
- uzasadnia, dlaczego rozne setupy maja rozne rozmiary.

Wniosek do tekstu:

- setup wyscigowy jest najwiekszy,
- setupy kwalifikacyjne sa czystsze, ale mocniej ograniczone liczebnie.

### 2. Porownanie glownych rodzin modeli

Plik:

- `figures/thesis/02_model_progression.png`

Rola:

- pokazuje progres od regresji logistycznej do CNN i hybrydy,
- dobrze pasuje do rozdzialu "Wyniki".

Wniosek:

- modele sekwencyjne/hybrydowe przewaznie przewyzszaja regresje logistyczna,
- sama regresja logistyczna pozostaje waznym modelem interpretowalnym.

### 3. Krzywa uczenia CNN

Plik:

- `figures/thesis/03_cnn_training_curve_short_horizon.png`

Rola:

- klasyczny wykres ML: accuracy/loss po epokach,
- pokazuje przebieg uczenia i roznice train-validation,
- dobrze wyglada w metodologii lub wynikach modeli sekwencyjnych.

Uwaga:

- pelna historia epok jest zachowana dla pierwszego CNN `2023-2025`,
- dla pozniejszych eksperymentow zapisano raczej liczbe epok i najlepszy val loss, dlatego nie nalezy udawac pelnych krzywych tam, gdzie ich nie ma.

Aktualizacja 2026-05-10:

- przygotowano skrypt `10_sequence_full_history_rerun.py`, ktory ponownie trenuje modele sekwencyjne dla setupu kwalifikacyjnego 2018-2025 oraz wyscigowego 2025,
- nowe eksporty maja sufiks `sequence_full_rerun` i beda zawierac pelne historie epok, predykcje OOF, macierze pomylek oraz metryki per kierowca,
- po zakonczeniu rerunu mozna rozszerzyc figure 3 o osobne krzywe uczenia dla dlugiego horyzontu i setupu wyscigowego zamiast pokazywac tylko krotki horyzont.
- rerun zostal wykonany i `09_thesis_figure_pack.py` generuje teraz dodatkowe figury `10-12` na podstawie nowych eksportow.

### 4. Liczba epok do early stopping

Plik:

- `figures/thesis/04_epochs_to_early_stopping.png`

Rola:

- pokazuje, jak dlugo trenowaly modele sekwencyjne w roznych setupach,
- dobrze uzupelnia krzywa uczenia,
- pokazuje, ze modele nie byly trenowane przez sztywna liczbe epok.

### 5. Macierz pomylek finalnego modelu interpretowalnego

Plik:

- `figures/thesis/05_final_model_confusion_matrix.png`

Rola:

- pokazuje, ktorzy kierowcy sa najlepiej rozroznialni,
- dobrze pasuje do interpretacji modelu i dyskusji o podobienstwach stylu.

Wniosek:

- `VER` i `LEC` sa najbardziej czytelni,
- `ALB` i `SAI` sa trudniejsi i czesciej myleni.

### 6. Najwazniejsze cechy w modelu interpretowalnym

Plik:

- `figures/thesis/06_driver_feature_importance.png`

Rola:

- laczy wynik modelu z interpretacja stylu jazdy,
- pokazuje, ze najwazniejsze sa cechy gazu, biegow, RPM, hamowania i dynamiki.

Wniosek:

- model nie opiera sie tylko na czasie okrazenia,
- najwazniejsze sa wzorce operowania samochodem.

### 7. Predykcja kierowcy vs predykcja zespolu

Plik:

- `figures/thesis/07_driver_vs_team_prediction.png`

Rola:

- pokazuje, ze zespol tez ma silny podpis w telemetrii,
- dobry wykres do rozdzialu o biasie zespolowym.

Wniosek:

- bias zespolowy jest realny,
- ale nie wyjasnia calosci predykcji kierowcy.

### 8. Hierarchia i team-aware

Plik:

- `figures/thesis/08_hierarchical_team_aware_comparison.png`

Rola:

- pokazuje, ze `Team -> Driver` i `team-aware` zostaly sprawdzone,
- dobry wykres do dyskusji metodologicznej.

Wniosek:

- alternatywne strategie z informacja o zespole sa ciekawe kontrolnie,
- ale nie poprawiaja stabilnie bezposredniej predykcji kierowcy.

### 9. Ferrari 2025: HAM vs LEC

Plik:

- `figures/thesis/09_same_team_ham_lec_feature_importance.png`

Rola:

- najmocniejszy wykres do pokazania, ze sygnal kierowcy istnieje w tym samym zespole,
- bardzo dobrze pasuje do dyskusji o oddzieleniu stylu kierowcy od charakterystyki samochodu.

Wniosek:

- nawet w tym samym Ferrari model znajduje roznice miedzy Hamiltonem i Leclerkiem,
- cechy rozrozniajace dotycza przede wszystkim gazu, biegow, RPM i hamowania.

## Dodatkowe wykresy warte zrobienia pozniej

### Per-driver radar / profil stylu

Pomysl:

- radar albo heatmapa dla `VER`, `LEC`, `OCO`, `SAI`, `ALB`,
- cechy: pelny gaz, zero gazu, sredni gaz, hamowanie, biegi, RPM.

Zastosowanie:

- rozdzial interpretacyjny o stylu jazdy.

### Team signature heatmap

Pomysl:

- heatmapa srednich cech dla zespolow,
- szczegolnie `Red Bull`, `Ferrari`, `Williams`, `Haas`.

Zastosowanie:

- rozdzial o biasie zespolowym i podpisie samochodu.

### Confusion matrix dla CNN/hybrydy

Pomysl:

- porownac macierz pomylek regresji logistycznej i najlepszego modelu sekwencyjnego/hybrydowego.

Zastosowanie:

- pokazac, gdzie hybryda faktycznie redukuje bledy.

## Nowe figury po rerunie pelnych historii

### 10. Krzywe uczenia hybrydy w trzech setupach

Plik:

- `figures/thesis/10_training_curves_multisetup_hybrid.png`

Rola:

- pokazuje przebieg walidacji dla najlepszego typu modelu w trzech setupach,
- pomaga opisac, czy modele ucza sie stabilnie i kiedy early stopping zatrzymuje trening.

### 11. Zmiennosc wyniku miedzy foldami

Plik:

- `figures/thesis/11_sequence_fold_variability.png`

Rola:

- pokazuje, czy dobry wynik modelu jest stabilny, czy zalezy od konkretnego podzialu danych,
- dobrze nadaje sie do dyskusji o przeuczeniu i wiarygodnosci walidacji.

### 12. Macierze pomylek najlepszych modeli sekwencyjno-hybrydowych

Plik:

- `figures/thesis/12_best_sequence_confusion_matrices.png`

Rola:

- pokazuje, ktorzy kierowcy sa rozrozniani najlepiej przez modele sekwencyjno-hybrydowe,
- uzupelnia macierz pomylek regresji logistycznej.

## Rekomendacja do pracy

Do glownej tresci pracy warto wybrac ok. 8-10 figur:

1. redukcja danych,
2. rozmiary setupow,
3. porownanie modeli,
4. krzywa uczenia,
5. macierz pomylek,
6. feature importance,
7. bias zespolowy,
8. hierarchia/team-aware,
9. case study Ferrari.

Reszte mozna dac do dodatku albo zostawic jako material roboczy.
