# File Guide

## Po co jest ten plik

Ten plik ma ulatwic dalsza prace, gdy projekt bedzie kontynuowany przez wiele tygodni i wiele chatow. Ma tez pomoc szybko zorientowac sie, ktore pliki sa teraz glownym interfejsem repo, a ktore zostaly zachowane jako archiwum robocze.

## Glowna logika projektu

Projekt rozwijal sie etapami:

1. zebranie danych i pierwsze EDA,
2. krotki horyzont kwalifikacyjny `2023-2025`,
3. rozszerzenie do dlugiego horyzontu `2018-2025`,
4. setup wyscigowy `2025`,
5. synteza wynikow i materialy do raportu,
6. analiza biasu zespolowego i modeli hierarchicznych,
7. studia przypadkow stabilnosci stylu,
8. generowanie figur i materialow do pracy.

## Aktualna mapa plikow

### Glowne notebooki

- `01_data_collection_audit_eda.ipynb`
- `02_short_horizon_qualifying_modeling.ipynb`
- `03_long_horizon_qualifying_2018_2025.ipynb`
- `04_race_setup_2025_clean_race_laps.ipynb`
- `05_results_reporting_and_supervisor_materials.ipynb`
- `06_team_bias_and_hierarchical_models.ipynb`
- `07_sequence_full_history_rerun.ipynb`
- `08_driver_style_case_studies.ipynb`
- `09_thesis_figures_and_reporting_assets.ipynb`

### Glowne dokumenty pomocnicze

- `PROJECT_STATUS.md`
- `METHODOLOGY_DECISIONS.md`
- `FILE_GUIDE.md`
- `NOTEBOOK_STRUCTURE.md`
- `HANDOFF_PROMPT.md`

### Glowny plik dla promotora

- `37_supervisor_update_multisetup_2026-03-31.tex`

### Materialy opisowe

- `15_thesis_methods_results_outline.md`

### Glówne skrypty zrodlowe

Najnowsze skrypty `.py` zostaly przepisane do notebookow `06`--`09`, ale pozostaja w katalogu glownym jako wersje zrodlowe i szybki sposob uruchomienia analizy z terminala.

- `06_team_bias_and_team_signature_analysis.py`
- `07_hierarchical_team_driver_model.py`
- `08_team_aware_driver_models.py`
- `09_thesis_figure_pack.py`
- `10_sequence_full_history_rerun.py`
- `11_red_bull_verstappen_teammate_window.py`
- `12_ricciardo_verstappen_style_similarity.py`
- `13_driver_style_transfer_stability.py`
- `14_thesis_narrative_case_study_figures.py`
- `15_thesis_eda_figures.py`
- `16_theory_figures.py`

## Archiwa

### Archiwum notebookow

- `archive_notebooks/`

Zawiera pierwotne, rozdrobnione notebooki z przebiegu pracy.

### Archiwum skryptow

- `archive_scripts/`

Zawiera skrypty, z ktorych zostaly zlozone notebooki `03`, `04` i `05`.

### Archiwum raportow

- `archive_reports/`

Zawiera starsze wersje raportow pomocniczych.

## Gdzie szukac wynikow

Glowny katalog eksportow:

- `exports/`

Przydatne grupy plikow:

- krotki horyzont:
  - `baseline_*`
  - `final_model_*`
  - `final_results_*`
- dlugi horyzont:
  - `long_horizon_*`
- wyscigi 2025:
  - `race_2025_*`
- tabele i artefakty do pracy:
  - `thesis_table_*`

## Minimalny zestaw do zrozumienia projektu

Jesli ktos ma bardzo malo czasu, to powinien przeczytac:

1. `PROJECT_STATUS.md`
2. `METHODOLOGY_DECISIONS.md`
3. `NOTEBOOK_STRUCTURE.md`
4. `01_data_collection_audit_eda.ipynb`
5. `02_short_horizon_qualifying_modeling.ipynb`
6. `03_long_horizon_qualifying_2018_2025.ipynb`
7. `04_race_setup_2025_clean_race_laps.ipynb`
8. `05_results_reporting_and_supervisor_materials.ipynb`
9. `06_team_bias_and_hierarchical_models.ipynb`
10. `07_sequence_full_history_rerun.ipynb`
11. `08_driver_style_case_studies.ipynb`
12. `09_thesis_figures_and_reporting_assets.ipynb`

## Minimalny zestaw do dalszej pracy w nowym chacie

- `PROJECT_STATUS.md`
- `METHODOLOGY_DECISIONS.md`
- `FILE_GUIDE.md`
- `HANDOFF_PROMPT.md`

## Uwaga praktyczna

Jesli jakis wynik opisany w rozmowie lub w pliku tekstowym nie zgadza sie z CSV w `exports`, za zrodlo prawdy uznawac:

1. `exports/`,
2. notebooki glowne i odpowiadajace im archiwa,
3. dopiero potem notatki opisowe.
