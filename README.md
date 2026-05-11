# Formula 1 driver style from telemetry

Projekt dotyczy identyfikacji stylu jazdy kierowców Formuły 1 na podstawie publicznie dostępnych danych telemetrycznych. Głównym celem nie jest przewidywanie wyniku wyścigu, lecz sprawdzenie, czy z przebiegu okrążenia można rozpoznać kierowcę oraz wskazać cechy opisujące jego sposób jazdy.

## Zakres badań

Analiza obejmuje trzy główne setupy eksperymentalne:

- kwalifikacje 2023--2025 jako najczystszy, krótki horyzont,
- kwalifikacje 2018--2025 jako dłuższy horyzont sezonów,
- czyste okrążenia wyścigowe 2025 jako większy, bardziej zaszumiony zbiór.

W projekcie porównywane są modele oparte na ręcznie zdefiniowanych cechach, modele sekwencyjne, modele hybrydowe oraz dodatkowe analizy kontrolujące wpływ zespołu i samochodu.

## Główne notebooki

Najlepiej czytać notebooki po kolei:

1. `01_data_collection_audit_eda.ipynb` - pobieranie danych, audyt i pierwsza EDA.
2. `02_short_horizon_qualifying_modeling.ipynb` - kwalifikacje 2023--2025 i pierwszy główny setup modelowy.
3. `03_long_horizon_qualifying_2018_2025.ipynb` - rozszerzenie kwalifikacji do lat 2018--2025.
4. `04_race_setup_2025_clean_race_laps.ipynb` - czyste okrążenia wyścigowe z sezonu 2025.
5. `05_results_reporting_and_supervisor_materials.ipynb` - synteza wyników i materiały raportowe.
6. `06_team_bias_and_hierarchical_models.ipynb` - bias zespołowy, modele hierarchiczne i team-aware.
7. `07_sequence_full_history_rerun.ipynb` - pełne historie uczenia modeli sekwencyjnych.
8. `08_driver_style_case_studies.ipynb` - studia przypadków stylu kierowcy i transferu między zespołami.
9. `09_thesis_figures_and_reporting_assets.ipynb` - figury EDA, wyniki i grafiki do pracy.

## Dane i wyniki

- `exports/` zawiera pliki CSV wygenerowane przez kolejne etapy analizy.
- `figures/thesis/` zawiera grafiki używane w pracy.
- `data/` i `f1_cache/` zawierają lokalne dane robocze oraz cache FastF1.
- `archive_notebooks/`, `archive_scripts/` i `archive_reports/` przechowują wcześniejsze, bardziej rozdrobnione wersje pracy.

## Przygotowanie środowiska

Podstawowe zależności znajdują się w pliku `requirements.txt`. Przykładowe uruchomienie:

```bash
python -m venv .venv
pip install -r requirements.txt
```

Notebooki korzystają z lokalnego cache FastF1. Katalog `f1_cache/` jest ignorowany przez Git, ponieważ może być duży i jest odtwarzalny przez ponowne pobranie danych.

## Skrypty źródłowe

Najnowsze skrypty `.py` zostały przeniesione logicznie do notebooków `06`--`09`, ale pozostają w folderze `scripts/` jako wersje źródłowe i szybki sposób uruchomienia z terminala. W samych notebookach wywołania `main()` są celowo zakomentowane, żeby przypadkowe `Run All` nie uruchamiało długich pobrań danych ani treningu modeli.

## Praca w LaTeX

Aktualna wersja kodu pracy znajduje się w `thesis_latex/`. Folder zawiera `main.tex`, klasę `mgr.cls`, bibliografię, logo oraz figury wymagane do kompilacji.

## Duże dane

Największe pliki telemetryczne nie są częścią tej paczki, ponieważ przekraczają praktyczne limity zwykłego repozytorium GitHub. Szczegóły znajdują się w `DATA_NOTES.md`.

## Dokumentacja pomocnicza

- `PROJECT_STATUS.md` - aktualny stan projektu i najważniejsze wyniki.
- `METHODOLOGY_DECISIONS.md` - decyzje metodyczne.
- `NOTEBOOK_STRUCTURE.md` - szczegółowa mapa notebooków.
- `FILE_GUIDE.md` - przewodnik po plikach.
- `HANDOFF_PROMPT.md` - skrót kontekstu do kontynuacji pracy w nowym czacie.

## Uwaga

Jeżeli opis w notatkach nie zgadza się z wygenerowanymi plikami CSV, za źródło prawdy należy traktować najpierw `exports/`, następnie główne notebooki, a dopiero potem pliki opisowe.
