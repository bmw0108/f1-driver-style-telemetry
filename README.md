# Formula 1 driver style from telemetry

Praca magisterska dotyczy identyfikacji stylu jazdy kierowców Formuły 1 na podstawie publicznie dostępnych danych telemetrycznych. Głównym celem jest sprawdzenie, czy z przebiegu okrążenia można rozpoznać kierowcę oraz wskazać cechy opisujące jego sposób jazdy.

## Zakres badań

Analiza obejmuje trzy główne setupy eksperymentalne:

- kwalifikacje 2023--2025 jako świeże dane z sesji odbywających się w "kontrolowanych warunkach",
- kwalifikacje 2018--2025 jako dłuższy horyzont poprzedniego okresu,
- czyste okrążenia wyścigowe 2025 jako większy, bardziej zaszumiony zbiór - więcej danych, większy procent odrzuconych okrążeń.

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
9. `09_thesis_figures_and_reporting_assets.ipynb` - wykresy EDA, wyniki i grafiki do pracy.

## Dane i wyniki

- `exports/` zawiera pliki CSV wygenerowane przez kolejne etapy analizy.
- `figures/` zawiera grafiki używane w notebookach i pracy.
- `scripts/` zawiera najnowsze skrypty Python użyte przy późniejszych eksperymentach.
- `thesis_latex/` zawiera aktualny kod pracy w LaTeX, bibliografię, klasę dokumentu, logo, wykresy oraz PDF poglądowy.

Największe surowe pliki telemetryczne nie są wrzucone do repozytorium, ponieważ są zbyt duże dla zwykłego repo GitHub i mogą zostać odtworzone lokalnie przez uruchomienie odpowiednich notebooków lub skryptów.

## Przygotowanie środowiska

Podstawowe zależności znajdują się w pliku `requirements.txt`. Przykładowe uruchomienie:

```bash
python -m venv .venv
pip install -r requirements.txt
```

## Praca w LaTeX

Aktualna wersja kodu pracy znajduje się w `thesis_latex/`. Główny plik to `thesis_latex/main.tex`.

PDF poglądowy znajduje się w `thesis_latex/Jaskolski_magisterka.pdf`.
