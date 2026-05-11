# Notebook Structure

## Cel

Ten plik opisuje aktualny, uproszczony uklad repo po porzadkach. Celem nie bylo "upiększanie" notebookow, tylko zmniejszenie ich liczby i zostawienie kilku glownych zeszytow roboczych, ktore da sie sensownie pokazac na GitHubie.

## Glowny uklad

W katalogu glownym znajduje sie dziewiec glownych notebookow:

1. `01_data_collection_audit_eda.ipynb`
2. `02_short_horizon_qualifying_modeling.ipynb`
3. `03_long_horizon_qualifying_2018_2025.ipynb`
4. `04_race_setup_2025_clean_race_laps.ipynb`
5. `05_results_reporting_and_supervisor_materials.ipynb`
6. `06_team_bias_and_hierarchical_models.ipynb`
7. `07_sequence_full_history_rerun.ipynb`
8. `08_driver_style_case_studies.ipynb`
9. `09_thesis_figures_and_reporting_assets.ipynb`

To jest teraz podstawowy zestaw do czytania i przegladania projektu. Notebooki `01`--`05` zawieraja glowny pipeline danych i modeli, a notebooki `06`--`09` dopinaja pozniejsze badania, kontrole biasu zespolowego, case studies oraz generowanie figur do pracy.

## Co zawieraja

### `01_data_collection_audit_eda.ipynb`

- pierwsze przygotowanie danych,
- audyt sesji i pokrycia,
- pierwsze EDA,
- wstepne rozpoznanie potencjalnych zbiorow.

Powstal z polaczenia:

- `archive_notebooks/01_setup.ipynb`
- `archive_notebooks/02_looking_for_potential_sets.ipynb`
- `archive_notebooks/03_got_the_data.ipynb`

### `02_short_horizon_qualifying_modeling.ipynb`

- baseline dla kwalifikacji `2023-2025`,
- walidacja grupowana,
- redukcja do bardziej rozroznialnych kierowcow,
- strojenie regresji logistycznej,
- interpretacja i pierwsze modele sekwencyjne.

Powstal z polaczenia:

- `archive_notebooks/05_baseline_driver_classification.ipynb`
- `archive_notebooks/06_grouped_driver_classification_validation.ipynb`
- `archive_notebooks/07_driver_subset_same_track_experiments.ipynb`
- `archive_notebooks/08_tuned_logistic_regression_distinctive_subsets.ipynb`
- `archive_notebooks/09_feature_family_ablation.ipynb`
- `archive_notebooks/10_compact_model_comparison.ipynb`
- `archive_notebooks/11_final_compact_model_interpretation.ipynb`
- `archive_notebooks/12_sequence_model_baseline.ipynb`

### `03_long_horizon_qualifying_2018_2025.ipynb`

- uzupelnienie danych historycznych,
- audyt pokrycia kierowcow i sezonow,
- selekcja kierowcow do dlugiego horyzontu,
- filtracja, ekstrakcja telemetrii, cechy i modele dla `2018-2025`.

Powstal z polaczenia skryptow:

- `archive_scripts/18_backfill_qualifying_2018_2022.py`
- `archive_scripts/19_backfill_qr_2018_2022.py`
- `archive_scripts/20_historical_qr_driver_audit.py`
- `archive_scripts/21_historical_driver_set_candidates.py`
- `archive_scripts/22_build_2018_2025_driver_selection_pool.py`
- `archive_scripts/23_select_2018_2025_provisional_top5.py`
- `archive_scripts/24_build_long_horizon_strict_qualifying.py`
- `archive_scripts/25_extract_long_horizon_telemetry.py`
- `archive_scripts/26_build_long_horizon_features.py`
- `archive_scripts/27_long_horizon_baseline.py`
- `archive_scripts/28_long_horizon_sequence_models.py`

### `04_race_setup_2025_clean_race_laps.ipynb`

- audyt okrazen wyscigowych sezonu `2025`,
- definicja czystych okrazen wyscigowych,
- telemetria, cechy i modele dla setupu wyscigowego.

Powstal z polaczenia skryptow:

- `archive_scripts/29_fetch_audit_2025_race_laps.py`
- `archive_scripts/30_prepare_2025_race_top5_targets.py`
- `archive_scripts/31_extract_race_2025_top5_telemetry.py`
- `archive_scripts/32_summarize_race_2025_telemetry.py`
- `archive_scripts/33_build_race_2025_features.py`
- `archive_scripts/34_race_2025_baseline.py`
- `archive_scripts/35_race_2025_sequence_models.py`

### `05_results_reporting_and_supervisor_materials.ipynb`

- porownanie architektur,
- synteza wynikow,
- przygotowanie tabel i figur,
- materialy pomocnicze do raportow i pracy.

Powstal z polaczenia skryptow:

- `archive_scripts/13_sequence_architecture_comparison.py`
- `archive_scripts/14_final_results_synthesis.py`
- `archive_scripts/15_thesis_artifacts.py`
- `archive_scripts/17_supervisor_figures.py`
- `archive_scripts/36_supervisor_multisetup_figures.py`
- `archive_scripts/38_supervisor_data_eda_figures.py`

### `06_team_bias_and_hierarchical_models.ipynb`

- analiza biasu zespolowego,
- predykcja zespolu na podstawie cech telemetrycznych,
- testy rozrozniania kierowcow w tym samym zespole,
- model hierarchiczny `team -> driver`,
- model team-aware z prawdopodobienstwami zespolu jako dodatkowymi cechami.

Powstal z polaczenia skryptow:

- `06_team_bias_and_team_signature_analysis.py`
- `07_hierarchical_team_driver_model.py`
- `08_team_aware_driver_models.py`

### `07_sequence_full_history_rerun.ipynb`

- ponowne uruchomienie modeli sekwencyjnych dla brakujacych historii uczenia,
- zapis metryk foldow, historii epok, predykcji OOF i macierzy pomylek,
- material pod wykresy krzywych uczenia w pracy.

Powstal z:

- `10_sequence_full_history_rerun.py`

### `08_driver_style_case_studies.ipynb`

- dodatkowe studia przypadkow zwiazane ze stylem kierowcy,
- mini-eksperyment Verstappen/Red Bull,
- analiza podobienstwa Ricciardo-Verstappen,
- finalna analiza stabilnosci profilu kierowcy po zmianie zespolu.

Powstal z polaczenia skryptow:

- `11_red_bull_verstappen_teammate_window.py`
- `12_ricciardo_verstappen_style_similarity.py`
- `13_driver_style_transfer_stability.py`

### `09_thesis_figures_and_reporting_assets.ipynb`

- generowanie figur EDA,
- generowanie figur teoretycznych,
- generowanie figur wynikowych do pracy,
- generowanie figur narracyjnych i case studies.

Powstal z polaczenia skryptow:

- `09_thesis_figure_pack.py`
- `14_thesis_narrative_case_study_figures.py`
- `15_thesis_eda_figures.py`
- `16_theory_figures.py`

## Archiwa

Stare, rozdrobnione pliki nie zostaly usuniete.

Notebooki archiwalne:

- `archive_notebooks/`

Skrypty archiwalne:

- `archive_scripts/`

Starsze raporty pomocnicze:

- `archive_reports/`

## Jak to czytac

Jesli ktos chce szybko zrozumiec projekt, najlepiej czytac notebooki po kolei od `01` do `09`.

Minimalna sciezka badawcza:

1. `01_data_collection_audit_eda.ipynb`
2. `02_short_horizon_qualifying_modeling.ipynb`
3. `03_long_horizon_qualifying_2018_2025.ipynb`
4. `04_race_setup_2025_clean_race_laps.ipynb`
5. `05_results_reporting_and_supervisor_materials.ipynb`

Rozszerzenia do rozdzialow badawczych i pracy:

1. `06_team_bias_and_hierarchical_models.ipynb`
2. `07_sequence_full_history_rerun.ipynb`
3. `08_driver_style_case_studies.ipynb`
4. `09_thesis_figures_and_reporting_assets.ipynb`

Jesli potrzebna jest pelna historia badania, wtedy siegac do:

- `archive_notebooks/`
- `archive_scripts/`

## Co dalej mozna jeszcze poprawic

Jesli bedziemy chcieli zrobic repo jeszcze czystsze, to nastepny krok to:

- wydzielenie `reports/`,
- wydzielenie `notebooks/`,
- wydzielenie `src/` albo `scripts/`,
- ewentualne przeniesienie najnowszych skryptow `.py` do `scripts/`, jesli uznamy, ze katalog glowny powinien zostac jeszcze bardziej odchudzony.
