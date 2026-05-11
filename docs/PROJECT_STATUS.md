# Project Status

## Project

Praca magisterska dotyczy identyfikacji stylu jazdy kierowcow Formuly 1 na podstawie telemetrii.

Glowny cel:

- rozpoznac kierowce na podstawie przebiegu okrazenia,
- sprawdzic, czy w telemetrii widac stabilne wzorce stylu jazdy,
- porownac modele oparte na recznie zdefiniowanych cechach z modelami sekwencyjnymi i hybrydowymi.

Projekt nie jest projektem typu "predykcja zwyciezcy wyscigu". Nacisk jest na zachowanie kierowcy, nie na wynik sportowy.

## Zasady pracy

- Wnioski maja wynikac z danych i eksportow, nie z domyslow.
- Kazdy wazny etap powinien konczyc sie plikami CSV do niezaleznej weryfikacji.
- Najpierw pracujemy na danych mozliwie najczystszych, a dopiero potem przechodzimy do setupow trudniejszych i bardziej zaszumionych.
- W nowym chacie najpierw czytac ten plik oraz `METHODOLOGY_DECISIONS.md`, a dopiero potem proponowac zmiany.

## Aktualny stan projektu

Na obecnym etapie istnieja trzy glowne, porownywalne setupy badawcze:

1. Kwalifikacje 2023-2025, krotki horyzont, 5 kierowcow.
2. Kwalifikacje 2018-2025, dlugi horyzont, 5 kierowcow.
3. Wyscigi 2025, czyste okrazenia wyscigowe, 5 kierowcow.

Dla wszystkich trzech setupow zbudowano:

- filtracje i audyt danych,
- ekstrakcje telemetrii,
- recznie zdefiniowane cechy na poziomie okrazenia,
- baseline z regresja logistyczna,
- modele sekwencyjne `CNN`, `GRU`, `LSTM`,
- model hybrydowy `CNN + cechy tabularne`.

## Aktualna struktura repo

Repo zostalo uproszczone do pieciu glownych notebookow:

1. `01_data_collection_audit_eda.ipynb`
2. `02_short_horizon_qualifying_modeling.ipynb`
3. `03_long_horizon_qualifying_2018_2025.ipynb`
4. `04_race_setup_2025_clean_race_laps.ipynb`
5. `05_results_reporting_and_supervisor_materials.ipynb`

Starsze, rozdrobnione pliki nie zostaly usuniete. Zostaly przeniesione do:

- `archive_notebooks/`
- `archive_scripts/`
- `archive_reports/`

## Setup 1: kwalifikacje 2023-2025

Finalny podzbior:

- kierowcy: `ALB, SAI, VER, OCO, LEC`
- liczba okrazen: `273`
- finalny model regresji logistycznej:
  - konfiguracja: `compact_no_context_no_phase`
  - `57` cech
  - kara `l1`
  - `C = 2.0`

Najwazniejsze wyniki:

- regresja logistyczna: accuracy `0.8608`, macro F1 `0.8617`
- `CNN`: accuracy `0.8974`, macro F1 `0.8952`
- hybryda `CNN + tabular`: accuracy `0.9158`, macro F1 `0.9147`

Najwazniejsze pliki:

- `02_short_horizon_qualifying_modeling.ipynb`
- `05_results_reporting_and_supervisor_materials.ipynb`
- `exports/final_results_model_comparison.csv`
- `exports/final_model_config.csv`

## Setup 2: kwalifikacje 2018-2025

Finalny podzbior:

- kierowcy: `SAI, VER, LEC, OCO, HAM`
- liczba okrazen: `698`
- liczebnosc klas:
  - `LEC 145`
  - `HAM 144`
  - `SAI 144`
  - `VER 144`
  - `OCO 121`

Najwazniejsze wyniki:

- regresja logistyczna: accuracy `0.8281`, macro F1 `0.8267`
- `CNN`: accuracy `0.9040`, macro F1 `0.9012`
- hybryda: accuracy `0.8911`, macro F1 `0.8887`
- `GRU`: accuracy `0.2966`, macro F1 `0.2880`
- `LSTM`: accuracy `0.3181`, macro F1 `0.2998`

Najwazniejsze pliki:

- `03_long_horizon_qualifying_2018_2025.ipynb`
- `exports/long_horizon_baseline_best_models.csv`
- `exports/long_horizon_sequence_best_models.csv`

## Setup 3: wyscigi 2025, czyste okrazenia wyscigowe

Finalny podzbior:

- kierowcy: `SAI, VER, LEC, OCO, HAM`
- liczba okrazen: `4334`
- liczebnosc klas:
  - `OCO 911`
  - `VER 882`
  - `LEC 875`
  - `HAM 867`
  - `SAI 799`

Najwazniejsze wyniki:

- regresja logistyczna: accuracy `0.8177`, macro F1 `0.8177`
- `CNN`: accuracy `0.8479`, macro F1 `0.8466`
- hybryda: accuracy `0.8567`, macro F1 `0.8564`
- `GRU`: accuracy `0.5711`, macro F1 `0.5639`
- `LSTM`: accuracy `0.3648`, macro F1 `0.3216`

Najwazniejsze pliki:

- `04_race_setup_2025_clean_race_laps.ipynb`
- `exports/race_2025_baseline_best_models.csv`
- `exports/race_2025_sequence_best_models.csv`

## Najwazniejsze wnioski merytoryczne

- Identyfikacja kierowcy na podstawie telemetrii jest mozliwa we wszystkich trzech setupach.
- Regresja logistyczna jest najlepszym i najbardziej stabilnym modelem bazowym.
- `CNN` i model hybrydowy sa wyraznie silniejsze predykcyjnie od regresji logistycznej.
- `GRU` i `LSTM` sa slabymi architekturami w tym projekcie nawet po zwiekszeniu liczby okrazen.
- W setupie wyscigowym usuniecie bezposrednich cech czasowych i czesci cech kontekstowych prawie nie pogarsza wyniku regresji logistycznej, co wzmacnia teze, ze model nie opiera sie glownie na samym tempie okrazenia.
- W interpretacji stylu szczegolnie wazne sa przypadki `VER` i `LEC`: dla obu kierowcow cechy wykryte przez model sa zgodne z publicznie opisywanym sposobem prowadzenia auta. To jest mocny argument, ze projekt nie konczy sie na samej klasyfikacji, ale pozwala tez powiazac wyniki modelu z realnymi wzorcami stylu jazdy.
- Dodano pierwszy test biasu w strone zespolu. Zespol da sie przewidywac z telemetrii dość dobrze, co oznacza, ze w danych istnieje silny podpis samochodu/zespolu. Jednoczesnie testy wewnatrz jednego zespolu, szczegolnie `HAM` vs `LEC` w Ferrari 2025, pokazuja, ze sygnal kierowcy nie znika po kontroli zespolu.
- Sprawdzono model hierarchiczny `Team -> Driver` w rozszerzonej siatce modeli i wariantow cech. Najlepsza byla kombinacja `logistic_l2 -> logistic_l2`, ale nie poprawila wynikow wzgledem bezposredniej predykcji kierowcy. Sprawdzono tez model team-aware, gdzie prawdopodobienstwa zespolu sa dodatkowymi cechami dla modelu kierowcy; rowniez nie dal on stabilnej poprawy. Dlatego predykcja zespolu jest przede wszystkim analiza biasu i podpisu samochodu, a nie glowna sciezka modelowania kierowcy.

## Aktualny stan dokumentow i raportow

Glowny aktualny plik dla promotora:

- `37_supervisor_update_multisetup_2026-03-31.tex`

Powiazane skrypty do figur:

- `archive_scripts/36_supervisor_multisetup_figures.py`
- `archive_scripts/38_supervisor_data_eda_figures.py`

Najwazniejsze figury:

- `figures/supervisor_setup_size_comparison.png`
- `figures/supervisor_filter_funnel_comparison.png`
- `figures/supervisor_setup_model_comparison.png`
- `figures/supervisor_architecture_comparison.png`
- `figures/supervisor_race_event_coverage.png`

Notatki o biasie zespolowym:

- `TEAM_BIAS_ANALYSIS_NOTES_PL.md`
- `TEAM_SIGNATURE_REALITY_COMPARISON_PL.md`
- `HIERARCHICAL_TEAM_DRIVER_MODEL_NOTES_PL.md`
- `exports/team_bias_team_classification_summary.csv`
- `exports/team_bias_same_team_driver_summary.csv`
- `exports/team_bias_team_feature_importance.csv`
- `exports/team_bias_same_team_driver_feature_importance.csv`
- `exports/team_bias_group_feature_means.csv`
- `exports/hierarchical_team_driver_summary.csv`
- `exports/team_aware_driver_model_comparison.csv`
- `exports/team_aware_driver_model_best.csv`

Dalsze kierunki:

- `NEXT_RESEARCH_DIRECTIONS_PL.md`

Plan wykresow:

- `THESIS_FIGURE_PLAN_PL.md`
- `09_thesis_figure_pack.py`
- `figures/thesis/`

Aktualizacja 2026-05-10:

- podczas planowania figur stwierdzono, ze pelne historie epok sa zapisane tylko dla pierwszych modeli sekwencyjnych krotkiego horyzontu,
- dla dlugiego horyzontu kwalifikacyjnego i setupu wyscigowego pierwotnie zapisano glownie liczbe epok oraz najlepszy `val_loss`,
- dodano `10_sequence_full_history_rerun.py`, aby ponownie uruchomic modele sekwencyjne i zapisac pelne historie epok, predykcje OOF, macierze pomylek oraz metryki per kierowca,
- nowe pliki wynikowe sa zapisywane z sufiksem `sequence_full_rerun`, bez nadpisywania pierwotnych wynikow.
- rerun zakonczyl sie dla setupow `long_qualifying_top5` i `race_2025_top5`; najwazniejsze wyniki rerunu:
  - `long_qualifying_top5`: CNN `0.8447`, hybryda `0.9056`, GRU `0.3044`, LSTM `0.3285` macro F1,
  - `race_2025_top5`: CNN `0.8500`, hybryda `0.8524`, GRU `0.5864`, LSTM `0.3162` macro F1.
- rerunowe wyniki nalezy traktowac jako dodatkowa, pelniej udokumentowana weryfikacje modeli sekwencyjnych; w razie ujednolicania tabel trzeba jawnie zdecydowac, czy w pracy zostaja pierwotne wyniki, czy wyniki z rerunu.

Aktualizacja 2026-05-10, mini-eksperyment Verstappen / Red Bull:

- dodano `11_red_bull_verstappen_teammate_window.py`,
- dociagnieto i przetworzono 780 okrazen kwalifikacyjnych dla par lider-partner w zespolach Red Bull Racing, Ferrari i Mercedes,
- wszystkie docelowe okrazenia telemetryczne zostaly wyciagniete poprawnie (`780/780 ok`),
- wygenerowano CSV `red_bull_verstappen_teammate_*` oraz figury `13-15` w `figures/thesis/`,
- wyniki wspieraja wykorzystanie cech telemetrycznych jako proxy do analizy dopasowania kierowca-samochod, ale nie dowodza wprost, ze samochod byl projektowany pod Verstappena,
- nie widac prostego monotonicznego trendu "z roku na rok coraz wieksze okno trudnosci"; widac natomiast stabilnie dodatnia przewage Verstappena nad partnerami w Red Bullu, szczegolnie w latach 2021-2024 dla pary `VER-PER`.

Aktualizacja 2026-05-10, Ricciardo vs Verstappen:

- dodano `12_ricciardo_verstappen_style_similarity.py`,
- sprawdzono, czy dane wspieraja narracje, ze Daniel Ricciardo byl stylistycznie blizej Verstappena niz pozniejsi partnerzy Red Bulla,
- najczystszy wariant to sezon 2018: `16` wspolnych sesji `VER-RIC` w Red Bullu,
- wedlug mediany standaryzowanej odleglosci stylu `RIC` jest blisko Verstappena, ale nie jednoznacznie najblizej; ranking median: `GAS 0.160`, `RIC 0.180`, `ALB 0.196`, `PER 0.197`, `TSU 0.215`, `LAW 0.284`,
- jednoczesnie `VER-RIC` ma bardzo mala mediane roznicy czasu okrazenia (`0.077 s`), co wspiera narracje, ze Ricciardo skutecznie dotrzymywal tempa Verstappenowi,
- wniosek ostrozny: dane mocniej wspieraja teze o konkurencyjnym tempie i kompatybilnosci Ricciardo w tym samym samochodzie niz teze o identycznym stylu jazdy.

Aktualizacja 2026-05-10, stabilnosc stylu po zmianie zespolu:

- dodano `13_driver_style_transfer_stability.py`,
- wyciagnieto i przetworzono `979/979` okrazen kwalifikacyjnych dla kierowcow zmieniajacych zespoly: `RIC, SAI, HAM, ALO, BOT, GAS, OCO, VET`,
- cechy normalizowano wzgledem sesji, aby ograniczyc wplyw toru i warunkow,
- dla Ricciardo mediana podobienstwa profilu miedzy zespolami wyniosla `0.528`, srednia `0.452`,
- najbardziej podobne pary Ricciardo: `McLaren-Renault 0.651`, `AlphaTauri-RB 0.640`, `RB-Renault 0.623`,
- profil `Red Bull Racing 2018` Ricciardo jest slabo podobny do `Renault` (`0.201`) i prawie niepodobny do `McLaren` (`0.006`) wedlug tej metryki,
- wniosek: dane czesciowo wspieraja teze, ze kierowca zachowuje pewne powtarzalne cechy stylu mimo zmiany auta, ale pokazuja tez, ze samochod i kontekst mocno przesuwaja profil telemetryczny.

Aktualizacja 2026-05-10, klamra narracyjna pracy:

- dodano `14_thesis_narrative_case_study_figures.py`,
- dodano notatke `THESIS_FINAL_RESEARCH_ARC_PL.md`,
- wygenerowano figury:
  - `figures/thesis/22_thesis_research_arc.png`,
  - `figures/thesis/23_selected_driver_transfer_case_studies.png`,
- rekomendowana narracja finalna: od predykcji kierowcy z telemetrii, przez kontrole biasu zespolowego, po case studies stabilnosci stylu po zmianie samochodu,
- aby uniknac zarzutu cherry-pickingu, w pracy glownej pokazac wybrane case studies, ale pelna tabele wynikow transferu stylu zostawic w dodatku/repozytorium,
- proponowane case studies: `OCO`, `GAS`, `ALO` jako mocniejsze przyklady stabilnosci, `RIC` jako czesciowy i ciekawy motorsportowo przypadek, `SAI` i `BOT` jako kontrprzyklady.

Aktualizacja 2026-05-10, rozbudowa draftu pracy:

- rozbudowano `thesis_draft_main.tex` zgodnie z komentarzami uzytkownika,
- rozdzial danych/EDA ma teraz wiecej konkretow: surowe liczby okrazen, redukcje po filtrach, finalne liczebnosci klas, typy cech, missingness, dlugosci sekwencji, rozklady cech i korelacje,
- dodano skrypt `15_thesis_eda_figures.py`,
- wygenerowano figury:
  - `figures/thesis/24_eda_dataset_sizes.png`,
  - `figures/thesis/25_eda_class_balance.png`,
  - `figures/thesis/26_eda_missingness.png`,
  - `figures/thesis/27_eda_sequence_lengths.png`,
  - `figures/thesis/28_eda_feature_distributions.png`,
  - `figures/thesis/29_eda_feature_correlation_heatmap.png`,
- rozbudowano Badanie 1 tak, aby pokazac kolejno: regresje logistyczna, CNN, hybryde, GRU/LSTM i dopiero potem finalne porownanie,
- dodano wyjasnienie early stoppingu: sprawiedliwe jest uzycie tej samej procedury walidacji i zatrzymania, a nie wymuszanie identycznej liczby faktycznie wykonanych epok,
- dodano interpretacje `gear_mean`: jest to proxy profilu okrazenia i pracy ukladu napedowego, a nie bezposredni dowod, ze kierowca po prostu "uzywa wyzszego biegu",
- rozbudowano Badanie 2 o tabele predykcji zespolu, warianty hierarchiczne/team-aware i testy kierowcow w tym samym zespole.

Aktualizacja 2026-05-10, korekty po przegladzie draftu:

- usunieto z `thesis_draft_main.tex` wykres brakow danych `26_eda_missingness.png`, bo brakow w cechach modelowych praktycznie nie bylo i wystarczy opis tekstowy,
- zostawiono informacje, ze pojedyncze braki dotyczyly glownie `TyreLife`, a kluczowe cechy telemetryczne byly kompletne,
- rozbudowano komentarz pod macierza korelacji: cechy predkosci, gazu, obrotow i biegow sa naturalnie powiazane, wiec interpretacja powinna dotyczyc rodzin cech, a nie jednej zmiennej w izolacji,
- zwieto rozdzial metodyczny do jednej spojnej sekcji `Proces, modele, walidacja i metryki`, zeby uniknac zbyt krotkich, pustych podrozdzialow,
- poprawiono legende w `figures/thesis/02_model_progression.png`, przesuwajac ja nizej i ukladajac w jednym wierszu.

Aktualizacja 2026-05-10, kolejny przeglad draftu:

- wstep w `thesis_draft_main.tex` zostal scalony w jedna plynna sekcje bez podrozdzialow `Cel pracy`, `Pytania badawcze`, `Zakres pracy`,
- we wstepie dopisano, ze praca porownuje rozne modele uczenia maszynowego w analizie stylu jazdy: regresje logistyczna, modele sekwencyjne i hybryde,
- przerobiono wykres redukcji danych po filtrach: zamiast jednego ciasnego panelu `figures/thesis/01_filter_funnels.png` uzywane sa trzy osobne pliki `01a_filter_funnel_qualifying_2023_2025.png`, `01b_filter_funnel_qualifying_2018_2025.png` i `01c_filter_funnel_race_2025.png`,
- w EDA usunieto z glownej tresci wykres liczebnosci klas; pozniej usunieto tez tabele i zostawiono opis tekstowy z najwazniejszymi zakresami liczebnosci,
- usunieto z glownej tresci boxploty rozkladow cech; zostawiono opis tekstowy i macierz korelacji,
- tekst wokol EDA zostal przestawiony na styl: wprowadzenie zjawiska, rysunek/tabela, komentarz interpretacyjny pod spodem.

Aktualizacja 2026-05-10, poprzednia praca jako odniesienie stylu:

- uzytkownik przekazal poprzednia prace magisterska `C:\Users\bjbmw\Desktop\praca_magisterska (8).pdf`,
- przejrzano ja pod katem stylu, ukladu rozdzialow i sposobu prowadzenia narracji,
- dodano notatke `WRITING_STYLE_REFERENCE_PL.md`,
- wnioski stylowe: wstep raczej jako plynna narracja, teoria jako osobny blok z intuicja/model/wzor/komentarz, dane jako opis-zjawisko/wykres/wniosek, eksperymenty model po modelu i dopiero potem tabela zbiorcza,
- wazna preferencja: nie robic wykresow bez mocnego komentarza i nie mnozyc bardzo krotkich podrozdzialow.

Aktualizacja 2026-05-10, rozbudowa teorii:

- rozbudowano rozdzial `Podstawy teoretyczne` w `thesis_draft_main.tex`,
- usunieto robocze TODO z teorii i dodano opis: telemetrii, stylu jazdy, klasyfikacji nadzorowanej, regresji logistycznej, Random Forest/boostingu, CNN 1D, GRU, LSTM, modelu hybrydowego oraz walidacji i metryk,
- dodano skrypt `16_theory_figures.py`,
- wygenerowano figury:
  - `figures/thesis/30_theory_logistic_sigmoid.png`,
  - `figures/thesis/31_theory_1d_cnn_concept.png`,
  - `figures/thesis/32_theory_grouped_cv.png`,
- dodano robocza bibliografie bezposrednio w `thesis_draft_main.tex`; pozniej mozna przeniesc ja do `.bib` zgodnie z szablonem uczelni,
- sprawdzono, ze wszystkie `includegraphics` wskazuja na istniejace pliki oraz ze wszystkie `\cite{}` maja odpowiadajace pozycje bibliografii.

Aktualizacja 2026-05-10, przeglad literatury:

- rozbudowano podrozdzial `Telemetria w motorsporcie` o praktyczne zastosowanie telemetrii do porownywania kierowcow oraz ograniczenia publicznych danych F1,
- dodano podrozdzial `Przeglad pokrewnych badan`,
- opisano powiazane prace: Meiring/Myburgh review driving style analysis, Hallac et al. driver identification from a single turn, Wang et al. driver identification using vehicle telematics, Driver2vec, oraz przyklady blizsze F1 telemetry/style,
- dodano nowe pozycje bibliografii: `hallac2016`, `wang2017`, `driver2vec`, `f1_fda_thesis`, `withseismic2026`,
- zaktualizowana teoria mocniej pokazuje, na czym projekt buduje i co doklada: F1 telemetry, trzy setupy, porownanie tabular/sequential/hybrid, kontrola biasu zespolowego i stabilnosc stylu po zmianie auta.

Aktualizacja 2026-05-10, literatura w interpretacji wynikow:

- dodano odniesienia do literatury bezposrednio w rozdzialach badawczych,
- przy regresji logistycznej dopisano, ze wynik jest zgodny z ogolnym kierunkiem prac o identyfikacji kierowcy z CAN/telematics,
- przy CNN dopisano odniesienie do klasyfikacji szeregow czasowych i pracy o identyfikacji kierowcy z pojedynczego zakretu,
- przy zbiorczym porownaniu modeli dopisano ostrozne zestawienie z projektem F1 telemetry/style WithSeismic, z zaznaczeniem, ze eksperymenty nie sa bezposrednio porownywalne,
- przy interpretacji cech dopisano, ze cechy gazu, hamowania, predkosci i dynamiki sa zgodne z typowymi zmiennymi w driving style recognition,
- w rozdziale o biasie zespolowym dopisano, ze jest to element specyficzny dla F1 i odroznia problem od klasycznych badan na danych drogowych,
- test w tym samym zespole opisano jako kontrole zmiennej zaklocajacej.

Aktualizacja 2026-05-10, wybor kierowcow i liczebnosc klas:

- usunieto z glownej tresci `thesis_draft_main.tex` tabele liczebnosci klas, bo byla malo czytelna i nie wnosila wystarczajaco duzo wzgledem opisu tekstowego,
- liczebnosc kierowcow zostala opisana w prozie: krotkie kwalifikacje maja po 54--55 okrazen na kierowce, dlugi horyzont 121--145, a setup wyscigowy 799--911,
- dodano podrozdzial `Wybor kierowcow`, ktory tlumaczy, ze finalne grupy nie byly przypadkowe: najpierw analizowano szerszy zbior kierowcow, a potem zwezano go wedlug liczby okrazen, jakosci danych i czytelnosci roznic w telemetrii,
- wazne ujecie narracyjne: nie opisywac tego jako prostego cherry-pickingu najlepszych wynikow, tylko jako etap projektowania eksperymentu, w ktorym celem bylo uzyskanie stabilnego i interpretowalnego porownania stylow jazdy.

Aktualizacja 2026-05-10, rozbudowa uzasadnienia wyboru kierowcow:

- rozbudowano `Wybor kierowcow` o metodologiczne uzasadnienie, czym w tej pracy jest "styl jazdy": nie jedna cecha, lecz kombinacja wejscia w zakret, balansu auta, hamowania, redukcji biegow, predkosci minimalnej i powrotu na gaz,
- dodano ostrozny kontekst z analiz branzowych F1 dotyczacych oversteer/understeer, ksztaltu linii przejazdu oraz roznic w fazach hamowania i przyspieszania,
- wazne: wywiady i analizy branzowe nie sa traktowane jako dowod wynikow, tylko jako uzasadnienie, dlaczego takie roznice warto sprawdzic w danych telemetrycznych,
- dodano tymczasowe wpisy bibliograficzne `formula1_racing_id` i `autosport_driving_style`.

Aktualizacja 2026-05-10, styl cytowan:

- przejrzano cytowania w `thesis_draft_main.tex` i przeniesiono wiele z nich blizej autora/zrodla, zamiast zostawiac je jako dopisek na koncu zdania,
- preferowany styl na dalsza prace: `Meiring i Myburgh \cite{...} opisują...`, `Hallac i współautorzy \cite{...} pokazali...`, `Dokumentacja FastF1 \cite{...} wskazuje...`,
- cytowanie na koncu zdania zostawiac tylko wtedy, gdy odnosi sie do calej tezy, a nie do konkretnego autora lub nazwy zrodla.

Aktualizacja 2026-05-10, format rozdzialow:

- dodano `\usepackage{etoolbox}` oraz `\pretocmd{\section}{\clearpage}{}{}` po spisie tresci w `thesis_draft_main.tex`,
- od tego momentu kazdy glowny rozdzial `\section` zaczyna sie od nowej strony,
- podrozdzialy `\subsection` pozostaja bez wymuszonego lamania strony.

Aktualizacja 2026-05-10, korekty wykresow i koncowki EDA:

- poprawiono wykresy redukcji danych po filtrach: podpis osi X zmieniono na `Etapy filtrowania`, zmniejszono lokalnie rozmiary tekstu i zostawiono trzy osobne figury zamiast jednego panelu,
- przejrzano skrypty figur pod katem polskich znakow w tytulach i osiach; poprawiono m.in. `okrążenia`, `próbek`, `Długość`, `Rozkłady`, `Wyścigi`, `dokładność`, `strata`, `trening`, `walidacja`,
- ponownie wygenerowano figury z `09_thesis_figure_pack.py` i `15_thesis_eda_figures.py`,
- rozbudowano koniec rozdzialu danych o podrozdzial `Wnioski z eksploracji danych dla modelowania`, zeby EDA naturalnie przechodzila do metodyki i zeby po wymuszeniu nowych stron rozdzial nie konczyl sie zbyt pusto,
- rozbudowano komentarz po liscie ograniczen danych, podkreslajac, ze ograniczenia nie blokuja modelowania, ale zawężają interpretację wyników.

Aktualizacja 2026-05-10, rozbudowa zrodel danych:

- rozbudowano podrozdzial `Źródła danych` w `thesis_draft_main.tex`,
- dodano opis biblioteki `FastF1`: typy danych, obiekt sesji, tabela okrazen, kanaly telemetryczne i dane pozycyjne,
- dopisano uzasadnienie uzycia cache: szybsze ponowne uruchomienia i ograniczenie ryzyka przekroczenia limitow API,
- dopisano ograniczenia publicznej telemetrii: brak pelnego kata skretu kierownicy, ustawien samochodu, map silnika, sil na pedalach i szczegolowych danych aerodynamicznych,
- dopisano role Jolpica i OpenF1 jako zrodel pomocniczych/przyszlej walidacji,
- po dyskusji scalono dokumentacje `FastF1` do jednego wpisu bibliograficznego `fastf1_docs`, zamiast traktowac kazda podstrone jako osobne zrodlo,
- dokumentacja biblioteki jest traktowana jako zrodlo techniczne/metodyczne, a nie jako literatura naukowa; docelowo mozna ja wydzielic w bibliografii jako dokumentacje lub zrodlo internetowe,
- sprawdzono, ze wszystkie `\cite{}` maja odpowiadajace `\bibitem{}` i ze nie ma nieuzytych wpisow bibliograficznych.

Aktualizacja 2026-05-10, migracja do szablonu WSB:

- folder `wsb-latex-template` zostal dostosowany jako robocza wersja pracy w szablonie uczelni,
- przeniesiono tresc z `thesis_draft_main.tex` do `wsb-latex-template/main.tex`,
- stare glowne sekcje zostaly zamienione na `\chapter`, a dawne podrozdzialy na `\section`, zgodnie ze struktura klasy `mgr`,
- bibliografia zostala przeniesiona z `thebibliography` do `wsb-latex-template/bibliografia.bib` i podpinana jest przez `biblatex`,
- skopiowano figury do `wsb-latex-template/figures/thesis`,
- w `main.tex` pozostawiono robocze metadane strony tytulowej: autor, numer albumu, promotor, kierunek, specjalizacja i rok do pozniejszej recznej korekty,
- po prosbie uzytkownika nie uruchamiac juz kompilacji PDF bez wyraznej prosby; wystarczy robic statyczne kontrole plikow/cytowan/grafik,
- po jednorazowym tescie wykryto konflikt starej klasy `mgr` z tabela oparta na `tabularx`/kolumnach `p{...}`; tabela setupow w wersji szablonowej zostala uproszczona do zwyklego `tabular`.

Aktualizacja 2026-05-11, puste strony w szablonie WSB:

- klasa `mgr` z opcja `printmode` domyslnie ustawia tryb dwustronny i `openright`, czyli rozdzialy startuja na prawej stronie jak w wersji drukowanej,
- powodowalo to puste strony miedzy rozdzialami,
- sprawdzono, ze w wersji szablonowej nie ma juz naszego starego `\pretocmd{\section}{\clearpage}{}{}` ani innych recznych laman stron przed rozdzialami,
- ostatecznie zostawiono oryginalne zachowanie templatki: `\documentclass[printmode,pl]{mgr}`,
- jesli pojawiaja sie puste strony, wynikaja one z oryginalnego trybu drukowanego `openright`, a nie z duplikacji naszego mechanizmu,
- usunieto pusta mini-sekcje `Cel badania` w rozdziale 5; jej jednozdaniowa tresc zostala jako wstep do rozdzialu, wiec numeracja zaczyna sie teraz od `5.1 Punkt odniesienia: regresja logistyczna`,
- wykonano tylko statyczna kontrole grafik i cytowan, bez kompilacji PDF.

Aktualizacja 2026-05-11, rzeczy do sprawdzenia z promotorem/szablonem:

- cytowania w przypisach dolnych sa technicznie mozliwe, bo szablon korzysta z `biblatex`; oryginalna templatka miala nawet zakomentowany wariant `style=verbose-note,autocite=footnote,ibidtracker=constrict,citetracker=true`,
- aktualna wersja trzyma domyslny styl templatki `\usepackage[style=numeric-verb]{biblatex}` i `\printbibliography`, czyli cytowania numeryczne w tekscie plus bibliografia na koncu,
- jesli promotor/uczelnia wymaga przypisow dolnych, trzeba bedzie przejsc na `autocite=footnote` oraz prawdopodobnie zamienic `\cite{...}` na `\autocite{...}` albo `\footcite{...}`,
- numeracja stron jest zdefiniowana w `mgr.cls` w stylu `headings`; numer strony znajduje sie w naglowku, nie w stopce,
- pierwsze strony rozdzialow maja `\thispagestyle{empty}`, wiec moga nie pokazywac numeru strony; to jest zachowanie klasy, a nie nasza zmiana,
- nie zmieniac tych rzeczy bez decyzji uzytkownika/promotora, bo nadrzedny jest uklad templatki.

Aktualizacja 2026-05-11, lustrzane marginesy:

- sprawdzono `mgr.cls`: mimo trybu `printmode`/dwustronnego klasa ustawiala identyczne marginesy `oddsidemargin` i `evensidemargin`,
- w `wsb-latex-template/main.tex` dodano lokalne nadpisanie marginesow tresci, bez edycji `mgr.cls`,
- ustawienia: `\oddsidemargin=0.46cm`, `\evensidemargin=-0.54cm`, przy `\textwidth=16cm`,
- daje to uklad A4: strony nieparzyste 3 cm lewy / 2 cm prawy, strony parzyste 2 cm lewy / 3 cm prawy,
- cel: zachowac logike druku dwustronnego i wiekszy margines wewnetrzny pod oprawe.

Aktualizacja 2026-05-11, wpis bibliografii w spisie tresci:

- Prism potwierdzil problem z `biblatex`: mimo polskiego skladu tekstu bibliografia korzystala z angielskiej lokalizacji `english.lbx`, wiec w spisie moglo pojawiac sie `Bibliography`,
- w `mgr.cls` polskie `\bibname` jest ustawiane na `Literatura`, ale samo `\usepackage{polski}` nie lokalizuje automatycznie napisow `biblatex`,
- zgodnie z zasada trzymania sie templatki nie wymuszac nazwy `Bibliografia`,
- w `main.tex` i `wsb-latex-template/main.tex` dodano jawne tlumaczenie `\DefineBibliographyStrings{english}{bibliography={Literatura}}`,
- koncowka dokumentu uzywa teraz `\printbibliography[heading=bibintoc,title={Literatura}]`, dzieki czemu `biblatex` sam dodaje wpis do spisu tresci,
- nie dodawac recznego `\addcontentsline` ani `\phantomsection` przed bibliografia, jesli zostaje wariant `heading=bibintoc`,
- nie zmieniano samej klasy `mgr`.

## Najblizsze sensowne kroki

- uporzadkowac notebooki i skrypty do bardziej zwartej struktury,
- przygotowac wersje stricte "thesis-ready" do Overleaf,
- rozdzielic material na: dane i EDA, metodyke, wyniki, ograniczenia,
- zdecydowac, ktore eksperymenty zostaja w pracy glownej, a ktore trafiaja do dodatku,
- przygotowac stabilny prompt startowy do nowego chatu.

## Uwaga dla nowego chatu

Nowy chat nie powinien zgadywac stanu projektu. Najpierw nalezy przeczytac:

1. `PROJECT_STATUS.md`
2. `METHODOLOGY_DECISIONS.md`
3. `FILE_GUIDE.md`
4. `HANDOFF_PROMPT.md`

Jesli pojawia sie niezgodnosc miedzy rozmowa a eksportami CSV, za zrodlo prawdy uznac eksporty i pliki w `exports`.
