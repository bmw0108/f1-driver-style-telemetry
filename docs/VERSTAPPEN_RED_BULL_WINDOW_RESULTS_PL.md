# Red Bull / Verstappen teammate mini-experiment

## Cel

Mini-eksperyment sprawdza proxy hipotezy o dopasowaniu kierowca-samochod dla Red Bulla i Verstappena.
Nie dowodzi, ze samochod byl projektowany pod konkretnego kierowce, bo nie mamy danych setupowych ani steering angle.

## Pokrycie Red Bulla

- VER vs PER: 70 wspolnych sesji, sezony 2021-2024.
- VER vs ALB: 23 wspolnych sesji, sezony 2019-2020.
- VER vs TSU: 19 wspolnych sesji, sezony 2025-2025.
- VER vs RIC: 16 wspolnych sesji, sezony 2018-2018.
- VER vs GAS: 12 wspolnych sesji, sezony 2019-2019.
- VER vs LAW: 2 wspolnych sesji, sezony 2025-2025.

## Srednia odleglosc stylu lider-partner

- Ferrari: mean=0.315, median=0.270, n=127.
- Red Bull Racing: mean=0.270, median=0.195, n=142.
- Mercedes: mean=0.232, median=0.211, n=121.

## Red Bull: czas okrazenia

- PER: partner - VER mean=0.507s, median=0.400s, n=70.
- ALB: partner - VER mean=2.121s, median=0.543s, n=23.
- TSU: partner - VER mean=0.790s, median=0.746s, n=19.
- RIC: partner - VER mean=-2.502s, median=0.077s, n=16.
- GAS: partner - VER mean=0.533s, median=0.486s, n=12.
- LAW: partner - VER mean=1.485s, median=1.485s, n=2.

## Trend sezonowy Red Bulla

Mediana straty partnera do Verstappena w tych samych sesjach kwalifikacyjnych:

- 2018, RIC: 0.077 s,
- 2019, ALB/GAS lacznie: ok. 0.546 s,
- 2020, ALB: 0.532 s,
- 2021, PER: 0.483 s,
- 2022, PER: 0.240 s,
- 2023, PER: 0.423 s,
- 2024, PER: 0.401 s,
- 2025, LAW/TSU lacznie: ok. 0.805 s.

Interpretacja:

- nie widac prostego monotonicznego trendu, w ktorym z roku na rok roznica stale rosnie,
- najbardziej stabilny i probkowo wiarygodny okres `VER vs PER` pokazuje stale dodatnia przewage Verstappena, ale z rokiem 2022 jako relatywnie najmniejsza roznica,
- 2025 wyglada wyraznie trudniej dla partnerow, ale porownanie jest slabsze metodologicznie, bo dotyczy innych kierowcow i mniejszej stabilnosci skladu,
- 2018 ma nietypowa srednia z powodu outlierow; mediana pokazuje raczej niewielka przewage Verstappena nad Ricciardo.

## Red Bull: proxy cech

- speed_min: VER - partner mean=1.1549, median=1.0000.
- speed_mean: VER - partner mean=2.7792, median=1.3139.
- throttle_full_frac: VER - partner mean=0.0045, median=0.0072.
- throttle_mid_frac: VER - partner mean=0.0029, median=0.0010.
- throttle_diff_abs_mean: VER - partner mean=0.1441, median=0.1077.
- brake_active_frac: VER - partner mean=-0.0021, median=0.0014.
- gear_change_count: VER - partner mean=-0.5282, median=-1.0000.

## Interpretacja ostrozna

- Wyniki moga wspierac dyskusje o dopasowaniu kierowca-samochod, ale nie sa dowodem na ustawienia samochodu pod Verstappena.
- Najsilniejszy material probkowy dotyczy pary VER-PER w latach 2021-2024.
- W pracy glownej najlepiej traktowac to jako case study albo future work.
- Dane bardziej wspieraja teze "telemtryczne proxy moga badac dopasowanie kierowca-samochod" niz teze "udowodniono, ze Red Bull zawęzal okno ustawien pod Verstappena".
- Warto pokazac to jako przyklad, ze model/cechy moga sluzyc do badania realnych narracji z motorsportu, ale trzeba jasno opisac ograniczenia.
