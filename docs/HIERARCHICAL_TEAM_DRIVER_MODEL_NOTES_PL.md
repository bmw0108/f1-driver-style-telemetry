# Model hierarchiczny zespol -> kierowca

## Pytanie

Po potwierdzeniu, ze w telemetrii istnieje podpis zespolu/samochodu, pojawilo sie naturalne pytanie:

Czy lepsza strategia modelowania moglaby wygladac tak:

1. najpierw przewidziec zespol,
2. dopiero potem przewidziec kierowce wewnatrz przewidzianego zespolu?

To bylby model hierarchiczny: `Team -> Driver`.

## Dlaczego to ma sens metodologicznie

Taka architektura jest sensowna jako eksperyment kontrolny, bo:

- Formula 1 ma silny komponent zespolowy,
- samochod zostawia podpis w telemetrii,
- czesc kierowcow jest mocno powiazana z jednym zespolem,
- bezposredni model kierowcy mogl niejawnie korzystac z informacji o zespole.

Z drugiej strony model hierarchiczny ma tez ryzyko:

- blad w predykcji zespolu przenosi sie na predykcje kierowcy,
- jesli zespół ma w treningu tylko jednego kierowce, model moze sztucznie sprowadzac zadanie do rozpoznawania zespolu,
- w dlugim horyzoncie kierowcy zmieniaja zespoly, wiec hierarchia nie zawsze odpowiada stabilnej strukturze problemu.

## Co sprawdzono

Dodano skrypt:

- `07_hierarchical_team_driver_model.py`

Eksporty:

- `exports/hierarchical_team_driver_summary.csv`
- `exports/hierarchical_team_driver_coverage.csv`

Porownano:

- bezposredni model kierowcy,
- bezposredni model zespolu,
- model hierarchiczny `Team -> Driver`.

Wszystkie warianty uzywaly rdzenia cech bez bezposrednich czasow okrazen i bez kontekstu typu zespol jako cecha wejsciowa.

## Wyniki

### Pierwszy test kontrolny

| Setup | Direct Driver Macro F1 | Team Macro F1 | Hierarchical Driver Macro F1 |
|---|---:|---:|---:|
| Kwalifikacje 2023-2025 top5 | 0.845 | 0.844 | 0.841 |
| Kwalifikacje 2018-2025 top5 | 0.806 | 0.535 | 0.789 |
| Wyscigi 2025 top5 | 0.797 | 0.823 | 0.782 |

### Rozszerzona siatka modeli

Nastepnie sprawdzono szersza, ale praktyczna siatke:

- direct driver: `logistic_l2`, `random_forest_regularized`, `hist_gradient_boosting_regularized`,
- direct team: te same modele,
- hierarchical `Team -> Driver`: kilka kombinacji modeli dla etapu zespolu i etapu kierowcy,
- warianty cech:
  - `all_telemetry_features`,
  - `no_time_features`,
  - `style_core_no_time_context`.

Najlepsze wyniki direct driver:

| Setup | Najlepszy model | Cechy | Macro F1 |
|---|---|---|---:|
| Kwalifikacje 2023-2025 top5 | logistic_l2 | no_time_features | 0.849 |
| Kwalifikacje 2018-2025 top5 | logistic_l2 | no_time_features | 0.810 |
| Wyscigi 2025 top5 | logistic_l2 | style_core_no_time_context | 0.797 |

Najlepsze wyniki hierarchical driver:

| Setup | Team model | Driver model | Cechy | Macro F1 |
|---|---|---|---|---:|
| Kwalifikacje 2023-2025 top5 | logistic_l2 | logistic_l2 | style_core_no_time_context | 0.841 |
| Kwalifikacje 2018-2025 top5 | logistic_l2 | logistic_l2 | style_core_no_time_context | 0.789 |
| Wyscigi 2025 top5 | logistic_l2 | logistic_l2 | style_core_no_time_context | 0.782 |

W rozszerzonej siatce modele drzewiaste i boostingowe nie poprawily wariantu hierarchicznego. Najlepsza pozostala prosta kombinacja `logistic_l2 -> logistic_l2`.

## Interpretacja

Model hierarchiczny dziala, ale nie poprawia wynikow wzgledem bezposredniej predykcji kierowcy.

To sugeruje, ze:

- informacja o zespole faktycznie pomaga i jest obecna w telemetrii,
- ale wymuszanie przejscia przez etap predykcji zespolu nie jest optymalna droga do predykcji kierowcy,
- bezposredni model kierowcy prawdopodobnie korzysta jednoczesnie z cech samochodu i cech kierowcy, zamiast najpierw "decydowac o zespole", a potem o kierowcy.
- w tym problemie twarde rozbicie na dwa etapy dodaje blad propagowany z pierwszego etapu, a nie pomaga modelowi lepiej uchwycic styl kierowcy.

Najbardziej widac to w setupie wyscigowym 2025:

- zespol jest przewidywany dobrze (`Team` macro F1 ok. `0.823`),
- ale model hierarchiczny kierowcy jest slabszy (`0.782`) niz bezposredni model kierowcy (`0.797`).

Oznacza to, ze dobra predykcja zespolu nie wystarcza, aby poprawic predykcje kierowcy.

Rozszerzony eksperyment wzmacnia ten wniosek: nawet po sprawdzeniu kilku rodzin modeli i wariantow cech model hierarchiczny nie stal sie lepszy od bezposredniego modelu kierowcy.

## Ile poprzednie wyniki mogly korzystac z biasu zespolowego

Na podstawie dotychczasowych testow mozna powiedziec:

- bias zespolowy istnieje i na pewno byl czescia informacji dostepnej dla modelu,
- szczegolnie tam, gdzie kierowca jest silnie powiazany z jednym zespolem,
- jednak nie caly wynik predykcji kierowcy mozna wyjasnic zespolem.

Najmocniejszy argument przeciwko tezie "model rozpoznaje tylko zespol":

- test Ferrari 2025: `HAM` vs `LEC`,
- ten sam zespol i sezon,
- `1742` okrazenia,
- macro F1 ok. `0.882`.

To pokazuje, ze nawet po kontroli zespolu zostaje silny sygnal kierowcy.

## Wniosek do pracy

Najlepsza interpretacja jest nastepujaca:

1. Bezposredni model kierowcy jest nadal najlepszym glownym modelem predykcyjnym.
2. Model hierarchiczny `Team -> Driver` jest ciekawym wariantem kontrolnym, ale nie poprawia wynikow.
3. Predykcja zespolu powinna zostac opisana jako analiza biasu i podpisu samochodu, a nie jako glowna metoda identyfikacji kierowcy.
4. W pracy trzeba jasno napisac, ze model kierowcy mogl czesciowo korzystac z cech zespolu/samochodu.
5. Jednoczesnie testy wewnatrz tego samego zespolu potwierdzaja, ze istnieje rowniez niezalezny sygnal kierowcy.

## Proponowane zdanie do wykorzystania pozniej

"Poniewaz w telemetrii wykryto silny podpis zespolu, sprawdzono rowniez wariant hierarchiczny, w ktorym model najpierw przewidywal zespol, a nastepnie kierowce wewnatrz przewidzianego zespolu. Taka strategia okazala sie metodologicznie interesujaca, ale nie poprawila wyniku wzgledem bezposredniej predykcji kierowcy. Oznacza to, ze informacja o zespole jest waznym zrodlem kontekstu i potencjalnego biasu, ale najlepszy model kierowcy nie sprowadza sie do prostej dekompozycji 'najpierw zespol, potem kierowca'."

## Co warto zrobic dalej

- Zrobic confusion matrix dla modelu hierarchicznego.
- Porownac bledy bezposredniego modelu kierowcy i modelu hierarchicznego.
- Sprawdzic wariant "team-aware", w ktorym predykcja zespolu jest dodatkowa cecha pomocnicza, ale nie twardym pierwszym etapem.
- Sprawdzic transfer kierowcow zmieniajacych zespoly: trenowanie na jednym zespole, test na innym, jesli liczba danych bedzie wystarczajaca.

## Co mozna uznac za zamkniete

Na ten moment model hierarchiczny warto traktowac jako:

- wazny eksperyment kontrolny,
- dowod, ze bias zespolowy trzeba raportowac,
- dodatkowy wariant metodologiczny,
- ale nie jako najlepsza finalna architekture predykcji kierowcy.

Do glownej narracji pracy najlepiej zostawic:

1. bezposrednia predykcje kierowcy jako glowny problem,
2. predykcje zespolu jako analize biasu i podpisu samochodu,
3. model hierarchiczny jako sprawdzona, ale slabsza alternatywe.

## Aktualizacja: model team-aware

Sprawdzono rowniez wariant posredni:

- najpierw model przewiduje prawdopodobienstwa zespolow,
- te prawdopodobienstwa sa dodawane jako dodatkowe cechy do modelu kierowcy,
- nie jest to twarda hierarchia, tylko "miekki" kontekst zespolowy.

Skrypt:

- `08_team_aware_driver_models.py`

Eksporty:

- `exports/team_aware_driver_model_comparison.csv`
- `exports/team_aware_driver_model_best.csv`

Wyniki macro F1:

| Setup | Direct tabular | Team-aware tabular | Najlepszy CNN/hybrid |
|---|---:|---:|---:|
| Kwalifikacje 2023-2025 top5 | 0.845 | 0.838 | 0.915 |
| Kwalifikacje 2018-2025 top5 | 0.806 | 0.809 | 0.901 |
| Wyscigi 2025 top5 | 0.797 | 0.779 | 0.856 |

Wniosek:

- team-aware pomaga minimalnie tylko w dlugim horyzoncie kwalifikacyjnym,
- w krotkim horyzoncie i setupie wyscigowym pogarsza wynik,
- hybrydy/sekwencje pozostaja wyraznie lepsze niz warianty tabularne z informacja o zespole.

To wzmacnia interpretacje, ze predykcja zespolu jest cenna jako analiza biasu, ale nie jako glowny sposob poprawiania modelu kierowcy.
