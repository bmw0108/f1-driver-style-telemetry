# Data notes

Folder `exports/` zawiera pliki wynikowe i pośrednie CSV mniejsze niż 50 MB. To wystarcza do przeglądania większości wyników, tabel, metryk i figur bez wrzucania największych surowych tabel telemetrycznych.

Największe pliki telemetryczne nie zostały skopiowane do paczki GitHub, ponieważ są zbyt duże na zwykły commit i powinny być trzymane lokalnie, odtwarzane przez notebooki albo obsługiwane przez Git LFS.

Pominięte duże pliki:

- `exports/race_2025_balanced_top5_telemetry_merged.csv` - około 448 MB
- `exports/best_laps_telemetry_merged.csv` - około 101 MB
- `exports/driver_style_transfer_telemetry_merged.csv` - około 86 MB
- `exports/balanced_top6_telemetry_merged_2018_2025_strict.csv` - około 81 MB
- `exports/red_bull_teammate_window_telemetry_merged.csv` - około 73 MB

Jeżeli repozytorium ma być w pełni odtwarzalne bez lokalnego cache, najlepszym dalszym krokiem jest Git LFS albo zewnętrzny link do paczki danych.
