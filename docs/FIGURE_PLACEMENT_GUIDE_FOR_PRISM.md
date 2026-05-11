# Mapa rozmieszczenia wykresow i rysunkow w pracy

Ten plik jest sciaga dla poprawiania floatow w LaTeXu. W kilku miejscach rysunki logicznie sa w dobrym miejscu w kodzie, ale LaTeX przerzuca je na inne strony, bo uzywa `[!htbp]`. Jezeli rysunek ma byc dokladnie miedzy opisem a interpretacja, najlepiej uzyc `[H]` dla konkretnej figury albo dodac `\FloatBarrier` po danej sekcji/bloku rysunkow.

## Zasada ogolna

- Rysunek powinien byc po akapicie, ktory go zapowiada.
- Bezposrednio po rysunku powinien byc akapit interpretujacy rysunek.
- Nie powinno byc sytuacji, w ktorej dwa duze rysunki teoretyczne, np. Random Forest/Boosting i CNN, laduja obok siebie lub jeden po drugim bez tekstu pomiedzy.
- Przy figurach w rozdziale teoretycznym szczegolnie warto wymusic pozycje, bo sa czescia wyjasnienia tekstu, a nie dodatkiem.

## Rozdzial 2: Podstawy teoretyczne

### `telemetry_overlay_lec_sai_2024_r16.png`

Label: `fig:telemetry_overlay_example`

Powinien byc po akapicie:

> Przykład takiego porównania pokazano na rysunku...

Powinien byc przed akapitem:

> Na wykresie widać, że różnice między kierowcami są lokalne...

Uwagi:

- To jest klasyczny przypadek: zapowiedz, rysunek, interpretacja.
- Warto wymusic pozycje `[H]`, bo bez tego interpretacja moze oderwac sie od rysunku.

### `30_theory_logistic_sigmoid.png`

Label: `fig:theory-logistic`

Powinien byc po wzorze funkcji logistycznej i zdaniu:

> gdzie \(z\) jest wynikiem liniowym modelu...

Powinien byc przed akapitem:

> Regresja logistyczna pełni w pracy rolę modelu interpretowalnego.

Uwagi:

- Rysunek jest czescia wyjasnienia regresji logistycznej, wiec powinien zostac w sekcji `Regresja logistyczna`.
- Nie powinien przeskoczyc do sekcji o modelach drzewiastych.

### `33_theory_tree_boosting_concept.png`

Label: `fig:theory-tree-boosting`

Powinien byc po akapicie:

> Różnicę między podejściem typu Random Forest a boostingiem przedstawiono schematycznie...

Powinien byc przed sekcja:

> \section{Modele sekwencyjne i CNN 1D}

Uwagi:

- Ten rysunek nie powinien ladowac na jednej stronie razem z rysunkiem CNN, jezeli przez to oba wygladaja jak oderwane od tekstu.
- Po tej figurze mozna dac `\FloatBarrier`, zeby rysunek Random Forest/Boosting nie przeszedl do kolejnej sekcji.

### `31_theory_1d_cnn_concept.png`

Label: `fig:theory-cnn`

Powinien byc po akapicie:

> Sieć konwolucyjna 1D (\texttt{1D CNN}) przesuwa filtry po osi czasu...

Powinien byc przed akapitem:

> W tej pracy \texttt{CNN} jest naturalnym kandydatem...

Uwagi:

- Ten rysunek powinien zostac w sekcji `Modele sekwencyjne i CNN 1D`.
- Nie powinien zostac wrzucony bezposrednio po rysunku Random Forest/Boosting.
- Jezeli sekcja robi sie za ciasna, lepiej przeniesc tekst/rysunek tak, aby byl osobny blok: opis CNN, rysunek, interpretacja CNN.

### `32_theory_grouped_cv.png`

Label: `fig:theory-grouped-cv`

Powinien byc po akapicie:

> Z tego powodu główną metodą walidacji był \texttt{StratifiedGroupKFold}...

Powinien byc przed akapitem:

> Do oceny modeli użyto kilku metryk.

Uwagi:

- Rysunek jest czescia wyjasnienia walidacji, wiec powinien zostac przed metrykami.

## Rozdzial 3: Dane i EDA

### `24_eda_dataset_sizes.png`

Label: `fig:eda-dataset-sizes`

Powinien byc po tabeli:

> `tab:setups` / `Główne setupy eksperymentalne`

Powinien byc przed sekcja:

> \section{Redukcja danych}

Uwagi:

- To jest wizualne podsumowanie setupow. Moze byc po tabeli, ale jezeli zostawia duza dziure, mozna go przesunac za pierwszy akapit sekcji `Redukcja danych`.

### `01a_filter_funnel_qualifying_2023_2025.png`

Label: `fig:filter-funnel-short-qualifying`

Powinien byc po akapicie:

> Dane były filtrowane etapowo...

Powinien byc przed drugim wykresem redukcji:

> `01b_filter_funnel_qualifying_2018_2025.png`

Uwagi:

- Ten i dwa kolejne wykresy tworza jedna serie. Jesli LaTeX robi balagan, mozna rozdzielic je tekstem albo zostawic jako trzy osobne figury jedna po drugiej z `\FloatBarrier` po trzeciej.

### `01b_filter_funnel_qualifying_2018_2025.png`

Label: `fig:filter-funnel-long-qualifying`

Powinien byc po pierwszym wykresie redukcji.

Powinien byc przed trzecim wykresem redukcji.

### `01c_filter_funnel_race_2025.png`

Label: `fig:filter-funnel-race`

Powinien byc po drugim wykresie redukcji.

Powinien byc przed akapitem:

> Największa redukcja w kwalifikacjach wynikała z trzech decyzji...

Uwagi:

- Bezposrednio po trzecim wykresie powinien isc akapit interpretujacy redukcje.
- Po tym akapicie mozna dac `\FloatBarrier`.

### `27_eda_sequence_lengths.png`

Label: `fig:eda-sequence-lengths`

Powinien byc po liscie:

> jako wektor ręcznie zdefiniowanych cech...
> jako sekwencja telemetryczna...

Powinien byc przed akapitem:

> Sekwencje telemetryczne miały zmienną długość...

### `29_eda_feature_correlation_heatmap.png`

Label: `fig:eda-correlation`

Powinien byc po akapicie:

> Przed modelowaniem warto sprawdzić, czy wybrane cechy opisują niezależne informacje...

Powinien byc przed akapitem:

> Na macierzy korelacji widać między innymi powiązania...

## Rozdzial 5: Badanie 1

### `05_final_model_confusion_matrix.png`

Label: `fig:final-confusion`

Powinien byc po akapicie:

> ...regresja logistyczna osiągnęła 0.8617 macro F1.

Powinien byc przed akapitem:

> Ten wynik jest zgodny z ogólnym kierunkiem badań...

### `03_cnn_training_curve_short_horizon.png`

Label: `fig:cnn-training-short`

Powinien byc po akapicie:

> Model \texttt{1D CNN} okazał się bardzo mocnym wariantem...

Powinien byc przed akapitem:

> Lepszy wynik \texttt{CNN} jest spójny z podejściem...

### `10_training_curves_multisetup_hybrid.png`

Label: `fig:training-curves`

Powinien byc po akapicie:

> Ten wariant był najlepszy w krótkim setupie kwalifikacyjnym oraz w setupie wyścigowym...

Powinien byc przed akapitem:

> Na wykresie widać, że liczba faktycznie wykonanych epok...

### `04_epochs_to_early_stopping.png`

Label: `fig:epochs-early-stopping`

Powinien byc po akapicie:

> Na wykresie widać, że liczba faktycznie wykonanych epok...

Powinien byc przed sekcja:

> \section{GRU i LSTM}

Uwagi:

- Jezeli ta figura laduje dziwnie, mozna rozwazyc przesuniecie jej po sekcji `GRU i LSTM`, ale logicznie najlepiej pasuje do komentarza o early stoppingu.

### `02_model_progression.png`

Label: `fig:model-progression`

Powinien byc po tabeli:

> `tab:model-results` / `Macro F1 dla głównych rodzin modeli`

Powinien byc przed akapitem:

> Wyniki pokazują, że identyfikacja kierowcy...

### `11_sequence_fold_variability.png`

Label: `fig:fold-variability`

Powinien byc po akapicie:

> Wynik ten można zestawić z projektem WithSeismic...

Powinien byc przed akapitem:

> Wyniki między foldami pokazują...

### `12_best_sequence_confusion_matrices.png`

Label: `fig:sequence-confusion`

Powinien byc zaraz po naglowku:

> \section{Macierze pomyłek}

Powinien byc przed akapitem:

> Macierze pomyłek pozwalają sprawdzić...

Uwagi:

- Jezeli wyglada zbyt nagle po naglowku, mozna dodac krotki akapit wprowadzajacy przed rysunkiem.

### `06_driver_feature_importance.png`

Label: `fig:feature-importance`

Powinien byc zaraz po naglowku:

> \section{Interpretacja cech}

Powinien byc przed akapitem:

> Najważniejsze cechy modelu interpretowalnego dotyczą...

Uwagi:

- Tu tez warto dodac jedno zdanie wprowadzajace przed rysunkiem, zeby nie zaczynac sekcji od samej figury.

## Rozdzial 7: Badanie 2

### `07_driver_vs_team_prediction.png`

Label: `fig:driver-vs-team`

Powinien byc zaraz po naglowku:

> \section{Predykcja kierowcy a predykcja zespołu}

Powinien byc przed akapitem:

> Wyniki pokazują, że zespół również ma wyraźny podpis telemetryczny.

Uwagi:

- Lepiej dodac krotkie zdanie przed wykresem, np. "Porównanie wyników przedstawiono na rysunku...".

### `08_hierarchical_team_aware_comparison.png`

Label: `fig:team-aware`

Powinien byc po liscie trzech strategii:

> model bezpośredni...
> model hierarchiczny...
> model team-aware...

Powinien byc przed akapitem:

> Modele wykorzystujące informację o zespole...

### `09_same_team_ham_lec_feature_importance.png`

Label: `fig:same-team`

Powinien byc po tabeli:

> `tab:same-team-tests` / `Testy rozróżniania kierowców w tym samym zespole`

Powinien byc przed akapitem:

> Przykład Ferrari 2025 pokazuje...

## Rozdzial 8: Badanie 3

### `19_driver_style_transfer_stability_summary.png`

Label: `fig:transfer-stability`

Powinien byc zaraz po naglowku:

> \section{Wyniki stabilności stylu}

Powinien byc przed tabela:

> `tab:transfer-cases`

Uwagi:

- Jezeli rysunek i tabela laduja bez tekstu jeden po drugim, mozna dodac krotki akapit interpretujacy po rysunku i dopiero potem dac tabele.

### `23_selected_driver_transfer_case_studies.png`

Label: `fig:selected-transfer`

Powinien byc po tabeli:

> `tab:transfer-cases`

Powinien byc przed akapitem:

> Wyniki sugerują, że u części kierowców...

### `22_thesis_research_arc.png`

Label: `fig:research-arc`

Powinien byc zaraz po naglowku:

> \section{Klamra interpretacyjna}

Powinien byc przed akapitem:

> Całość badań można podsumować jako przejście od klasyfikacji do interpretacji:

Uwagi:

- Tu warto dodac jedno zdanie przed rysunkiem, zeby nie zaczynac sekcji od samej grafiki.

## Sugestia techniczna dla Prisma

Jezeli celem jest zachowanie ukladu: tekst -> rysunek -> interpretacja, najprostsze rozwiazanie:

```tex
\usepackage{placeins}
```

I potem po logicznych blokach:

```tex
\FloatBarrier
```

Szczegolnie polecane miejsca na `\FloatBarrier`:

- po `fig:telemetry_overlay_example`;
- po `fig:theory-logistic`;
- po `fig:theory-tree-boosting`;
- po `fig:theory-cnn`;
- po `fig:theory-grouped-cv`;
- po trzech wykresach filtrowania danych;
- po `fig:training-curves` i `fig:epochs-early-stopping`;
- po `fig:sequence-confusion`;
- po `fig:team-aware`;
- po `fig:selected-transfer`.

Alternatywnie przy wybranych figurach mozna uzyc:

```tex
\begin{figure}[H]
```

ale niekoniecznie globalnie dla wszystkich, bo wtedy LaTeX moze zostawiac duze puste przestrzenie. Najlepiej wymuszac tylko te rysunki, ktore musza byc bezposrednio przy interpretacji.
