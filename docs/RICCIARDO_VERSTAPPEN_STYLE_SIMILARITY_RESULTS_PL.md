# Ricciardo vs Verstappen: analiza podobienstwa stylu

## Pytanie

Czy dane wspieraja popularna narracje, ze Daniel Ricciardo byl stylistycznie blizej Maxa Verstappena niz pozniejsi partnerzy Red Bulla?

## Najczystszy test

Najczystszy wariant to sezon 2018, czyli wspolne sesje Ricciardo i Verstappena w tym samym zespole i tym samym samochodzie.
Dostepne jest 16 wspolnych sesji VER-RIC w Red Bullu.

## Ranking podobienstwa partnerow Red Bulla do Verstappena

- GAS: mediana odleglosci stylu = 0.160, srednia = 0.192, n=12.
- RIC: mediana odleglosci stylu = 0.180, srednia = 0.305, n=16.
- ALB: mediana odleglosci stylu = 0.196, srednia = 0.275, n=23.
- PER: mediana odleglosci stylu = 0.197, srednia = 0.288, n=70.
- TSU: mediana odleglosci stylu = 0.215, srednia = 0.215, n=19.
- LAW: mediana odleglosci stylu = 0.284, srednia = 0.284, n=2.

## VER-RIC: cechy w tym samym samochodzie

- teammate_minus_ver_lap_time: mean=-2.5024, median=0.0770, n=16.
- speed_min_leader_minus_teammate: mean=-0.8125, median=0.0000, n=16.
- speed_mean_leader_minus_teammate: mean=-4.4161, median=0.0280, n=16.
- throttle_full_frac_leader_minus_teammate: mean=-0.0352, median=-0.0061, n=16.
- throttle_mid_frac_leader_minus_teammate: mean=0.0635, median=0.0485, n=16.
- throttle_diff_abs_mean_leader_minus_teammate: mean=0.0816, median=0.0595, n=16.
- brake_active_frac_leader_minus_teammate: mean=0.0096, median=0.0086, n=16.
- gear_change_count_leader_minus_teammate: mean=-0.6875, median=-1.0000, n=16.

## Interpretacja

- Ricciardo nie jest najblizszym partnerem Verstappena wedlug mediany prostej odleglosci stylu; blisko sa rowniez GAS i PER, ale probki sa nierowne.
- Jednoczesnie VER-RIC w 2018 ma bardzo mala mediane roznicy czasu okrazenia, co jest zgodne z narracja, ze Ricciardo najskuteczniej dotrzymywal tempa Verstappenowi.
- Wniosek powinien byc ostrozny: dane bardziej wspieraja teze o konkurencyjnym tempie Ricciardo w tym samym samochodzie niz jednoznaczna teze o identycznym stylu jazdy.
- Do mocniejszego wniosku o stylu potrzebne bylyby steering angle, dane setupowe albo porownanie zakret po zakrecie.
- Cosine similarity profilu RIC/Red Bull vs VER/Red Bull = 0.521; traktowac jako pomocnicze, bo profil oparty jest na agregatach cech.