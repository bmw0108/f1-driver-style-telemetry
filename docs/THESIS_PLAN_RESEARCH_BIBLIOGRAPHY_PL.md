# Plan pracy, research literatury i bibliografia robocza

## Ocena obecnego zakresu

Na obecnym etapie zakres badan jest wystarczajacy na prace magisterska, o ile zostanie dobrze opisany i uporzadkowany. Projekt nie ogranicza sie do jednego modelu ani jednego wyniku. Ma:

- pelny proces przetwarzania danych od pobrania do modelowania,
- trzy porownywalne setupy eksperymentalne,
- modele interpretowalne, sekwencyjne i hybrydowe,
- kontrole biasu zespolowego,
- analize kierowcow w tym samym zespole,
- eksporty CSV i wykresy pozwalajace odtworzyc wnioski.

Najmocniejsza narracja pracy:

> Czy styl jazdy kierowcy Formuly 1 jest widoczny w publicznie dostepnej telemetrii i czy modele uczenia maszynowego potrafia go rozpoznac oraz opisac?

Najwazniejszy wniosek:

> Tak, identyfikacja kierowcy na podstawie telemetrii jest mozliwa, ale wynik trzeba interpretowac ostroznie, bo czesc sygnalu pochodzi rowniez z charakterystyki zespolu/samochodu.

## Proponowana struktura pracy

### 1. Wstep

Cel rozdzialu:

- wprowadzic problem stylu jazdy w Formule 1,
- odroznic projekt od predykcji zwyciezcy lub wyniku sportowego,
- postawic pytania badawcze,
- opisac wklad pracy.

Proponowane pytania badawcze:

1. Czy na podstawie danych telemetrycznych mozna rozpoznac kierowce Formuly 1?
2. Czy modele sekwencyjne analizujace przebieg okrazenia daja lepsze wyniki niz modele oparte na recznie zdefiniowanych cechach?
3. Ktore cechy telemetrii najbardziej pomagaja rozrozniac kierowcow?
4. Na ile predykcja kierowcy moze byc zanieczyszczona biasem zespolowym?
5. Czy po kontroli zespolu nadal widoczny jest indywidualny sygnal kierowcy?
6. Czy elementy stylu kierowcy sa czesciowo stabilne po zmianie zespolu i samochodu?

### 2. Podstawy teoretyczne

Ten rozdzial powinien byc pisany po metodach faktycznie uzytych w pracy, a nie jako ogolny przeglad calego ML.

Sekcje:

- telemetria pojazdu i dane czasowe w motorsporcie,
- problem identyfikacji kierowcy i rozpoznawania stylu jazdy,
- klasyfikacja nadzorowana i metryki wieloklasowe,
- regresja logistyczna jako model interpretowalny,
- modele drzewiaste i boostingowe jako porownawcze baseline'y,
- walidacja krzyzowa i walidacja grupowana,
- szeregi czasowe i modele sekwencyjne,
- 1D CNN dla przebiegow telemetrycznych,
- GRU i LSTM jako modele rekurencyjne,
- model hybrydowy laczacy sekwencje i cechy tabularne,
- problem interpretowalnosci i biasu zespolowego.

### 3. Dane i eksploracyjna analiza danych

Cel:

- pokazac skad pochodza dane,
- pokazac jak wygladaja surowe dane,
- uzasadnic filtry,
- pokazac skale redukcji danych,
- opisac trzy setupy.

Sekcje:

- zrodla danych: FastF1, pomocniczo Jolpica/OpenF1,
- dostepne kanaly: `Speed`, `Throttle`, `Brake`, `RPM`, `nGear`, `DRS`, `X`, `Y`, `Z`,
- ograniczenia danych: brak idealnego czasowego wyrównania car/position w pierwszym wariancie, brak kierownicy/steering angle, booleanowy `Brake`,
- setup 1: kwalifikacje 2023-2025,
- setup 2: kwalifikacje 2018-2025,
- setup 3: czyste okrazenia wyscigowe 2025,
- filtracja danych i funnel,
- liczebnosc kierowcow, sesji i okrazen,
- rozklad dlugosci sekwencji telemetrycznych,
- brakujace dane i jakosc danych.

Figury pasujace tutaj:

- `figures/thesis/01a_filter_funnel_qualifying_2023_2025.png`,
- `figures/thesis/01b_filter_funnel_qualifying_2018_2025.png`,
- `figures/thesis/01c_filter_funnel_race_2025.png`,
- wykres rozmiarow setupow,
- wykres liczebnosci klas,
- rozklad dlugosci sekwencji,
- ewentualnie przykladowy przebieg telemetrii jednego okrazenia.

### 4. Metodyka eksperymentow

Cel:

- opisac dokladnie, jak przechodzimy od okrazenia do predykcji,
- pokazac, ze wyniki nie sa z losowego train/test splitu,
- rozdzielic modele tabularne, sekwencyjne i hybrydowe.

Sekcje:

- reprezentacja okrazenia jako wektora cech,
- reprezentacja okrazenia jako sekwencji,
- recznie zdefiniowane cechy telemetryczne,
- resampling sekwencji do stalej dlugosci,
- standaryzacja danych w ramach foldow,
- `StratifiedGroupKFold` po sesji,
- metryki: accuracy, balanced accuracy, macro F1, macierz pomylek,
- eksperymenty z cechami czasowymi i bez cech czasowych,
- kontrola przeuczenia: train-test gap, early stopping, krzywe uczenia,
- eksperyment biasu zespolowego,
- model hierarchiczny `Team -> Driver`,
- model team-aware.

### 5. Wyniki

Cel:

- najpierw pokazac glowne wyniki rozpoznawania kierowcy,
- potem interpretacje,
- potem kontrole biasu zespolowego.

Sekcje:

1. Wyniki setupu kwalifikacyjnego 2023-2025.
2. Wyniki setupu kwalifikacyjnego 2018-2025.
3. Wyniki setupu wyscigowego 2025.
4. Porownanie regresji logistycznej, CNN, hybrydy, GRU i LSTM.
5. Stabilnosc wynikow miedzy foldami.
6. Interpretacja cech kierowcow.
7. Bias zespolowy i predykcja zespolu.
8. Kierowcy w tym samym zespole: Ferrari 2025, HAM vs LEC.
9. Model hierarchiczny i team-aware.
10. Transfer stylu po zmianie zespolu jako case study.

Figury pasujace tutaj:

- `figures/thesis/02_model_progression.png`,
- `figures/thesis/10_training_curves_multisetup_hybrid.png`,
- `figures/thesis/11_sequence_fold_variability.png`,
- `figures/thesis/12_best_sequence_confusion_matrices.png`,
- `figures/thesis/06_driver_feature_importance.png`,
- `figures/thesis/07_driver_vs_team_prediction.png`,
- `figures/thesis/08_hierarchical_team_aware_comparison.png`,
- `figures/thesis/09_same_team_ham_lec_feature_importance.png`.
- `figures/thesis/22_thesis_research_arc.png`,
- `figures/thesis/23_selected_driver_transfer_case_studies.png`.

### 6. Dyskusja

Cel:

- wyjasnic, co wyniki znacza, a czego nie znacza,
- oddzielic styl kierowcy od samochodu,
- porownac obserwacje z literatura i publicznymi opisami kierowcow.

Watki:

- modele rozpoznaja kierowcow znacznie powyzej przypadku,
- CNN/hybryda sugeruja, ze przebieg czasowy telemetrii zawiera dodatkowa informacje wzgledem samych statystyk,
- regresja logistyczna jest slabsza predykcyjnie, ale wazniejsza interpretacyjnie,
- `GRU` i `LSTM` nie sprawdzily sie tak dobrze jak CNN,
- setup wyscigowy jest duzy, ale bardziej zaszumiony,
- bias zespolowy istnieje i musi byc jawnie opisany,
- test HAM vs LEC w Ferrari 2025 jest waznym argumentem, ze nie wszystko sprowadza sie do samochodu,
- obserwacje dla VER i LEC mozna zestawic z publicznymi opisami ich preferencji dotyczacych balansu auta.

### 7. Ograniczenia

Najwazniejsze ograniczenia:

- dane publiczne nie zawieraja wszystkich kanalow znanych zespolom, np. pelnego steering angle,
- `Brake` w FastF1 jest w praktyce sygnalem booleanowym, a nie pelnym cisnieniem hamowania,
- dane car/position wymagaja precyzyjniejszego wyrownania czasowego przed analiza zakret po zakrecie,
- kierowca i samochod nie sa w pelni separowalne,
- porownania miedzy sezonami sa utrudnione przez zmiany regulaminowe, samochody i zespoly,
- modele sekwencyjne sa mniej interpretowalne niz regresja logistyczna.

### 8. Podsumowanie i dalsze prace

Mozliwe dalsze kierunki:

- segmentacja okrazenia na zakrety i mini-sektory,
- time-aligned merge car/position telemetry,
- analiza transferu kierowcy miedzy zespolami,
- reprezentacje embeddingowe kierowcow,
- clustering podobienstwa stylu,
- porownanie z OpenF1 jako niezaleznym zrodlem,
- analiza tor po torze,
- dashboard do interpretacji stylu jazdy,
- wykorzystanie modelu jako narzedzia treningowego lub scoutingowego.

## Uzyte technologie

Warstwa danych:

- Python,
- FastF1,
- Pandas,
- NumPy,
- lokalny cache FastF1,
- CSV jako format eksportu wynikow.

Eksploracja i wizualizacja:

- Jupyter Notebook,
- Matplotlib,
- Seaborn,
- tabele CSV,
- LaTeX/Overleaf do raportowania.

Modele klasyczne:

- regresja logistyczna,
- Random Forest,
- HistGradientBoosting,
- XGBoost lub wariant boostingowy, jesli finalnie zostanie w pracy,
- standaryzacja cech,
- selekcja/porownanie rodzin cech.

Modele sekwencyjne:

- 1D CNN,
- GRU,
- LSTM,
- hybryda `CNN + cechy tabularne`,
- Adam,
- early stopping,
- resampling sekwencji telemetrycznej.

Walidacja i metryki:

- `StratifiedGroupKFold`,
- accuracy,
- balanced accuracy,
- macro F1,
- per-driver precision/recall/F1,
- macierze pomylek,
- train-test gap,
- krzywe uczenia.

## Czy warto robic jeszcze dodatkowy eksperyment?

Nie widze potrzeby dodawania kolejnego duzego, ciezkiego eksperymentu tylko po to, zeby "bylo wiecej". Obecny zakres jest juz szeroki. Jesli dodawac cos jeszcze, to raczej male, dobrze uzasadnione analizy wspierajace interpretacje.

Najbardziej sensowne opcjonalne dodatki:

1. Profil stylu per kierowca jako radar/heatmapa.
2. Heatmapa podpisu zespolu.
3. Porownanie najlepszych cech VER/LEC/HAM w jednym wykresie.
4. Krotka analiza tor po torze dla 2-3 najczestszych torow.
5. Appendix z wynikami rerunu modeli sekwencyjnych.

## Potencjalna uzytecznosc modelu poza praca

Model nie musi byc tylko akademickim klasyfikatorem. Mozliwe zastosowania:

- analiza porownawcza stylu kierowcow,
- narzedzie treningowe dla sim racingu lub juniorow,
- wykrywanie zmian stylu po zmianie zespolu/samochodu,
- analiza dopasowania kierowca-samochod,
- scouting kierowcow na podstawie telemetrycznych wzorcow,
- dashboard komentatorski/fanowski do interpretacji okrazen,
- wykrywanie anomalii w okrazeniu,
- porownywanie stylu na tym samym torze i w tym samym zespole,
- budowa embeddingow stylu jazdy zamiast samej klasyfikacji.

## Research: co juz istnieje w literaturze

### Najblizsza literatura do naszego problemu

Najblizsze prace nie dotycza zwykle Formuly 1, ale identyfikacji kierowcy na podstawie danych z pojazdu. To jest bardzo dobra baza teoretyczna, bo problem jest analogiczny: kierowca zostawia w sygnalach pojazdu pewien "podpis" zachowania.

W literaturze pojawiaja sie:

- CAN-BUS / OBD-II jako odpowiednik naszych kanalow telemetrycznych,
- klasyfikacja kierowcy jako zadanie nadzorowane,
- wykorzystanie cech statystycznych i sekwencji,
- modele Random Forest, SVM, ANN, CNN, LSTM/GRU,
- problem doboru cech i interpretowalnosci,
- zastosowania w bezpieczenstwie, personalizacji, ubezpieczeniach, monitoringu floty.

Wazna luka:

- nie znalazlem wielu prac stricte o identyfikacji stylu kierowcy Formuly 1 z publicznej telemetrii FastF1,
- istnieja natomiast prace o F1 analytics, strategii, oponach, racing line i lap time,
- dlatego wkład pracy mozna opisac jako adaptacje metod driver identification do publicznych danych telemetrycznych Formuly 1.

### Prace F1 / motorsport

- FastF1 jest juz wykorzystywane w nowszych pracach F1 analytics, np. w modelowaniu degradacji opon.
- Publiczna telemetria F1 jest wystarczajaca do analiz lap-level i sequence-level, ale ma ograniczenia wzgledem danych zespolowych.
- Nowe prace F1 czesciej koncentruja sie na strategii, oponach, racing line i lap time prediction niz na stylu kierowcy.

## Bibliografia robocza

### Zrodla danych i F1

1. FastF1 documentation. `FastF1` daje dostep do timing data, telemetrii, pozycji, opon, pogody i wynikow sesji. Link: https://docs.fastf1.dev/
2. FastF1 telemetry documentation. Opisuje kanaly `Speed`, `RPM`, `nGear`, `Throttle`, `Brake`, `DRS`, `X`, `Y`, `Z` oraz kwestie laczenia/resamplingu telemetrii. Link: https://docs.fastf1.dev/api_reference/telemetry.html
3. OpenF1 documentation. Alternatywne otwarte API z danymi F1 w JSON/CSV, historycznie od 2023. Link: https://openf1.org/docs/
4. Cappello, C., Hoegh, A. (2026). *A state-space approach to modeling tire degradation in Formula 1 racing*. Uzywa FastF1 do modelowania F1 race data. Link: https://journals.sagepub.com/doi/full/10.1177/22150218261446170
5. Curvature-Based Geometric Difficulty Analysis of Formula 1 Racing Lines (2026). Praca o analizie racing line z publicznej telemetrii F1. Link: https://www.mdpi.com/2076-3417/16/3/1596
6. Motorsport Data Acquisition System and Live Telemetry using FPGA based CAN controller (2022). Kontekst techniczny telemetryki motorsportowej i CAN. Link: https://researcher.manipal.edu/en/publications/motorsport-data-acquisition-system-and-live-telemetry-using-fpga-/

### Identyfikacja kierowcy i styl jazdy

7. Enev et al. (2016/2018). *Who is behind the wheel? Driver identification and fingerprinting*. Pokazuje, ze kierowce mozna identyfikowac z danych sensorowych pojazdu. Link: https://link.springer.com/article/10.1186/s40537-018-0118-7
8. Luo, D., Lu, J., Guo, G. (2018). *Driver Identification Using Multivariate In-vehicle Time Series Data*. SAE Technical Paper. Link: https://saemobilus.sae.org/papers/driver-identification-using-multivariate-vehicle-time-series-data-2018-01-1198
9. Ullah, S., Kim, D.-H. (2020). *Lightweight Driver Behavior Identification Model with Sparse Learning on In-Vehicle CAN-BUS Sensor Data*. Sensors. Link: https://www.mdpi.com/1424-8220/20/18/5030
10. Choi et al. (2019). *A Deep Learning Framework for Driving Behavior Identification on In-Vehicle CAN-BUS Sensor Data*. Sensors. Link: https://www.mdpi.com/1424-8220/19/6/1356
11. Espino-Salinas et al. (2023). *Driver Identification Using Statistical Features of Motor Activity and Genetic Algorithms*. Sensors. Link: https://www.mdpi.com/1424-8220/23/2/784
12. Carvalho et al. (2020). *A Systematic Methodology to Evaluate Prediction Models for Driving Style Classification*. Sensors. Link: https://www.mdpi.com/1424-8220/20/6/1692
13. Driver2vec (2021). Reprezentacje/embeddingi kierowcow z danych motoryzacyjnych. Link: https://arxiv.org/abs/2102.05234
14. *Driver Identification Using Vehicle Telematics Data* (2017). SAE Technical Paper. Link: https://saemobilus.sae.org/papers/driver-identification-using-vehicle-telematics-data-2017-01-1372
15. *Driver Identification Using Automobile Sensor Data from a Single Turn* (2017). Pokazuje identyfikacje kierowcy nawet z krotkich fragmentow jazdy. Link: https://arxiv.org/abs/1708.04636

### Modele, walidacja, time series

16. Hastie, Tibshirani, Friedman. *The Elements of Statistical Learning*. Podstawy regresji logistycznej, regularyzacji, klasyfikacji i metod drzewiastych. Link: https://link.springer.com/book/10.1007/978-0-387-84858-7
17. Breiman, L. (2001). *Random Forests*. Klasyczna praca o lasach losowych. Link: https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf
18. Chen, T., Guestrin, C. (2016). *XGBoost: A Scalable Tree Boosting System*. Link: https://arxiv.org/abs/1603.02754
19. Goodfellow, Bengio, Courville. *Deep Learning*. Podstawy sieci neuronowych, regularyzacji, CNN i modeli sekwencyjnych. Link: https://www.deeplearningbook.org/
20. Fawaz et al. (2019). *Deep learning for time series classification: a review*. Link: https://arxiv.org/abs/1809.04356
21. Kiranyaz et al. (2021). *1D convolutional neural networks and applications: A survey*. Link: https://www.sciencedirect.com/science/article/pii/S0888327020307846
22. Hochreiter, S., Schmidhuber, J. (1997). *Long Short-Term Memory*. Link: https://doi.org/10.1162/neco.1997.9.8.1735
23. Cho et al. (2014). *Learning Phrase Representations using RNN Encoder-Decoder for Statistical Machine Translation*. Wprowadzenie GRU/RNN Encoder-Decoder. Link: https://arxiv.org/abs/1406.1078
24. Kingma, D. P., Ba, J. (2014). *Adam: A Method for Stochastic Optimization*. Link: https://arxiv.org/abs/1412.6980
25. scikit-learn documentation: `StratifiedGroupKFold`. Uzasadnienie grupowanej walidacji z zachowaniem proporcji klas. Link: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html

### Zrodla kontekstowe do interpretacji stylu kierowcow

Te zrodla nie sa publikacjami naukowymi. Nadaja sie do dyskusji i ostroznego porownania obserwacji z powszechnie opisywanymi charakterystykami kierowcow.

26. Formula1.com o stylu Leclerca i agresji/set-upie po GP Francji 2022. Link: https://www.formula1.com/en/latest/article/leclerc-says-france-crash-wont-change-his-driving-style-thats-what-gave-me.7rZKOErcfIT3kmjL72e0nn
27. The Race o preferencji Verstappena do "pointy front end". Link: https://www.the-race.com/formula-1/what-is-a-pointy-front-end-max-verstappen-f1-preference/
28. Autosport o technikach Verstappena i agresywnym przodzie auta. Link: https://www.autosport.com/f1/news/the-verstappen-techniques-that-have-made-him-f1s-benchmark-driver/10517761/

## Jak te zrodla wykorzystac w pracy

Wstep:

- zrodla o F1 i telemetryce,
- FastF1/OpenF1 jako uzasadnienie dostepnosci danych.

Teoria:

- driver identification / driving style recognition,
- modele ML,
- time series classification,
- walidacja grupowana.

Dane:

- FastF1 docs,
- OpenF1 jako zrodlo walidacyjne/pomocnicze,
- ograniczenia telemetryczne.

Metody:

- `StratifiedGroupKFold`,
- logistic regression,
- Random Forest / XGBoost,
- CNN / GRU / LSTM / Adam.

Dyskusja:

- porownanie z driver identification literature,
- publiczne zrodla o VER/LEC tylko jako kontekst, nie jako twardy dowod naukowy.

## Co warto przygotowac przed pisaniem

1. Ujednolicic, czy w tabelach finalnych uzywamy pierwotnych wynikow modeli sekwencyjnych, czy wynikow z rerunu `sequence_full_rerun`.
2. Wybrac 8-12 najwazniejszych figur do glownej pracy.
3. Reszte figur i tabel przeniesc do dodatku.
4. Przygotowac plik `.bib` z bibliografia.
5. Przygotowac finalny spis notebookow/skryptow do GitHuba.
6. Dopisac w kazdym glownym notebooku krotki opis: cel, wejscia, wyjscia, najwazniejsze CSV.

## Dodatkowy research: inne serie wyscigowe i motorsport

Te zrodla sa bardziej kontekstowe niz bezposrednio porownawcze. Nie zawsze dotycza klasyfikacji kierowcy, ale pokazuja, ze telemetria motorsportowa jest uzywana do oceny kierowcy, samochodu, strategii i decyzji inzynierskich.

### Formula SAE / Formula Student

**Ashford, Mitra (2020), Formula SAE Data Acquisition and Detailed Analysis of a Lap**

- Seria/obszar: Formula SAE.
- Glowny temat: akwizycja danych i szczegolowa analiza okrazenia.
- Dlaczego przydatne: autorzy wprost lacza dane telemetryczne z ocena zachowania kierowcy i mozliwosci samochodu. To jest bardzo bliskie naszej narracji, bo zamiast patrzec tylko na czas okrazenia, analizuja komponenty jazdy w roznych czesciach toru.
- Jak wykorzystac: w rozdziale o danych/telemetrii i w dyskusji, ze w motorsporcie dane okrazenia sluza nie tylko do rankingu czasow, ale tez do diagnozy stylu i slabosci kierowcy.
- Link: https://saemobilus.sae.org/content/2020-01-0544

**Telemetry system developing for Formula Student racecar (2021)**

- Seria/obszar: Formula Student.
- Glowny temat: budowa systemu telemetrycznego dla zespolu Formula Student.
- Dlaczego przydatne: pokazuje praktyczny aspekt motorsport telemetry, czyli zbieranie danych z samochodu jako element ciaglego rozwoju konstrukcji.
- Jak wykorzystac: raczej w tle, jako przyklad technicznego znaczenia telemetrii w seriach juniorskich/studenckich.
- Link: https://doi.org/10.35925/j.multi.2021.3.1

**Low Cost Data Acquisition for Racing Applications (2004)**

- Seria/obszar: Formula SAE.
- Glowny temat: tani system akwizycji danych dla samochodu wyścigowego.
- Dlaczego przydatne: historycznie pokazuje, ze nawet poza profesjonalnym F1 dane telemetryczne sa kluczowym narzedziem poprawy performance.
- Jak wykorzystac: opcjonalnie, w krotkim wprowadzeniu do akwizycji danych w motorsporcie.
- Link: https://saemobilus.sae.org/papers/low-cost-data-acquisition-racing-applications-2004-01-3531

### Motocykle / Moto racing

**Mine4Race (2025), user-friendly toolset for racing telemetry analysis and visualization**

- Seria/obszar: motocyklowy zespol wyscigowy.
- Glowny temat: webowy system do eksploracji telemetrii, porownywania okrazen i wspierania komunikacji inzynier-kierowca/zawodnik.
- Dlaczego przydatne: bardzo dobrze pasuje do naszej czesci o uzytecznosci. Autorzy opisuja telemetrie jako srodowisko do wizualizacji, porownywania okrazen i przyszlego wdrazania modeli predykcyjnych.
- Jak wykorzystac: w future work, dashboardach, interpretacji wynikow i potencjalnych zastosowaniach modelu.
- Link: https://www.sciencedirect.com/science/article/pii/S2590123025049084

**Real-Time Visual Anomaly Detection in High-Speed Motorsport (2026)**

- Seria/obszar: premier-class motorcycle racing / MotoGP context.
- Glowny temat: wykrywanie anomalii wizualnych przy wysokiej predkosci z uwzglednieniem telemetrii i ograniczen opoznienia.
- Dlaczego przydatne: mniej zwiazane ze stylem jazdy, ale ciekawe jako przyklad laczenia danych motorsportowych, obrazu, telemetrii i modeli AI.
- Jak wykorzystac: tylko jako dodatkowy kontekst future work, np. multimodalnosc telemetry + video.
- Link: https://www.mdpi.com/2313-433X/12/2/60

### Profesjonalna telemetria motorsportowa

**Spence, van Manen, Centonze (2000), Fast Performance Analysis Using Multi-Burst Telemetry**

- Seria/obszar: Formula 1 i profesjonalny motorsport.
- Glowny temat: system ATLAS V7 do analizy danych telemetrycznych w czasie rzeczywistym i po okrazeniach.
- Dlaczego przydatne: pokazuje, ze telemetry analysis jest fundamentalna w profesjonalnym motorsporcie i historycznie zwiazana z F1.
- Jak wykorzystac: jako kontekst we wstepie do telemetrii i narzedzi inzynierskich.
- Link: https://doi.org/10.4271/2000-01-3567

**High Speed Wireless Optical System for Motorsport Data Loggers (2019)**

- Seria/obszar: motorsport ogolnie, wymieniane m.in. F1, WEC, WTCC i rally.
- Glowny temat: transmisja danych telemetrycznych w motorsporcie.
- Dlaczego przydatne: daje techniczne tlo do tego, czym jest telemetria i po co zbiera sie wiele kanalow z samochodu.
- Jak wykorzystac: rozdzial o danych i telemetrii, zwlaszcza przy wyjasnieniu, ze telemetria sluzy do oceny powertrain, handling, temperatur, zawieszenia itd.
- Link: https://www.mdpi.com/2079-9292/8/8/873

**Analysis Techniques for Racecar Data Acquisition, Jorge Segers**

- Obszar: praktyczna analiza danych z samochodu wyscigowego.
- Glowny temat: ksiazka/opracowanie SAE o analizie danych akwizycji w racecar engineering.
- Dlaczego przydatne: moze byc bardzo dobrym zrodlem "inzynierskim" do opisu telemetrii, okrazenia, zachowania samochodu i kierowcy.
- Jak wykorzystac: jesli masz dostep przez uczelnie, warto uzyc jako zrodla podstawowego do rozdzialu o telemetrii.
- Link: https://saemobilus.sae.org/books/analysis-techniques-racecar-data-acquisition-r-367

### Autonomous racing / racing RL

**Formula RL: Deep Reinforcement Learning for Autonomous Racing using Telemetry Data**

- Seria/obszar: autonomous racing / symulacja.
- Glowny temat: reinforcement learning z wejściem w postaci wielowymiarowej telemetrii.
- Dlaczego przydatne: nie jest o identyfikacji kierowcy, ale pokazuje, ze telemetryczne szeregi czasowe sa naturalnym wejsciem dla modeli uczacych sie zachowania pojazdu.
- Jak wykorzystac: future work, zwlaszcza gdyby pisac o modelach generujacych/oceniajacych zachowanie, a nie tylko klasyfikujacych.
- Link: https://arxiv.org/abs/2104.11106

## Teoretyczne zrodla "wypelniajace" bibliografie

To sa zrodla, ktore warto miec w bibliografii nie dlatego, ze sa najblizsze F1, tylko dlatego, ze opisujemy uzyte modele i potrzebujemy podparcia teoretycznego.

### Ogolne uczenie maszynowe i klasyfikacja

**Bishop (2006), Pattern Recognition and Machine Learning**

- Do czego uzyc: klasyfikacja, regresja logistyczna, probabilistyczna interpretacja modeli, overfitting, model selection.
- Miejsce w pracy: rozdzial teoretyczny o klasyfikacji nadzorowanej.
- Link: https://link.springer.com/book/10.1007/978-0-387-45528-0

**Hastie, Tibshirani, Friedman (2009), The Elements of Statistical Learning**

- Do czego uzyc: regresja logistyczna, regularyzacja, metody drzewiaste, random forest, boosting, walidacja.
- Miejsce w pracy: podstawy klasycznych modeli ML i interpretacja regularizacji.
- Link: https://hastie.su.domains/ElemStatLearn/

**Murphy (2012), Machine Learning: A Probabilistic Perspective**

- Do czego uzyc: probabilistyczne podstawy ML, klasyfikacja, modele generatywne/dyskryminacyjne.
- Miejsce w pracy: ogolna teoria ML, jesli potrzeba bardziej akademickiego zrodla.
- Link: https://mitpress.mit.edu/9780262018029/machine-learning/

**Pedregosa et al. (2011), Scikit-learn: Machine Learning in Python**

- Do czego uzyc: uzasadnienie narzedzia `scikit-learn`, klasyczne algorytmy ML, pipeline'y i implementacja eksperymentow.
- Miejsce w pracy: sekcja narzedziowa/metodyczna.
- Link: https://www.jmlr.org/papers/v12/pedregosa11a.html

### Regresja logistyczna, drzewa, boosting

**scikit-learn LogisticRegression documentation**

- Do czego uzyc: praktyczne parametry regresji logistycznej, `penalty`, `C`, solvery, multiclass.
- Miejsce w pracy: opis implementacji, nie jako glowne zrodlo teoretyczne.
- Link: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html

**Breiman (2001), Random Forests**

- Do czego uzyc: opis Random Forest jako modelu porownawczego.
- Miejsce w pracy: modele klasyczne.
- Link: https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf

**Chen, Guestrin (2016), XGBoost**

- Do czego uzyc: opis gradient boosting / XGBoost, jesli zostanie w pracy jako porownawczy model.
- Miejsce w pracy: modele klasyczne / boostingowe.
- Link: https://arxiv.org/abs/1603.02754

### Deep learning, CNN, modele sekwencyjne

**Goodfellow, Bengio, Courville (2016), Deep Learning**

- Do czego uzyc: sieci neuronowe, backpropagation, regularyzacja, CNN, RNN.
- Miejsce w pracy: glowny "podrecznikowy" fundament deep learningu.
- Link: https://www.deeplearningbook.org/

**LeCun, Bengio, Hinton (2015), Deep learning**

- Do czego uzyc: krotkie, prestizowe zrodlo o deep learningu, CNN i RNN.
- Miejsce w pracy: wprowadzenie do modeli glebokich.
- Link: https://www.nature.com/articles/nature14539

**LeCun, Bottou, Bengio, Haffner (1998), Gradient-Based Learning Applied to Document Recognition**

- Do czego uzyc: klasyczne zrodlo CNN/LeNet.
- Miejsce w pracy: opis idei konwolucji i lokalnych wzorcow.
- Link: https://bottou.org/papers/lecun-98h

**Krizhevsky, Sutskever, Hinton (2012), ImageNet Classification with Deep Convolutional Neural Networks**

- Do czego uzyc: historyczne znaczenie glebokich CNN.
- Miejsce w pracy: jesli chcesz pokazac, dlaczego CNN staly sie standardem w deep learningu.
- Link: https://papers.nips.cc/paper/4824-imagenet-classification-with-deep-convolutional-neural-networks

**Hochreiter, Schmidhuber (1997), Long Short-Term Memory**

- Do czego uzyc: LSTM, problem zanikajacego gradientu, dlugoterminowa pamiec w RNN.
- Miejsce w pracy: opis modelu LSTM.
- Link: https://doi.org/10.1162/neco.1997.9.8.1735

**Cho et al. (2014), Learning Phrase Representations using RNN Encoder-Decoder**

- Do czego uzyc: GRU/RNN Encoder-Decoder, bramkowana architektura rekurencyjna.
- Miejsce w pracy: opis modelu GRU.
- Link: https://arxiv.org/abs/1406.1078

**Srivastava et al. (2014), Dropout**

- Do czego uzyc: dropout jako regularyzacja sieci neuronowych i sposob ograniczania przeuczenia.
- Miejsce w pracy: metodyka treningu modeli sekwencyjnych/hybrydowych.
- Link: https://www.jmlr.org/papers/v15/srivastava14a.html

**Kingma, Ba (2014), Adam**

- Do czego uzyc: optymalizator Adam w treningu sieci neuronowych.
- Miejsce w pracy: opis treningu CNN/GRU/LSTM/hybrydy.
- Link: https://arxiv.org/abs/1412.6980

### Klasyfikacja szeregow czasowych

**Fawaz et al. (2019), Deep learning for time series classification: a review**

- Do czego uzyc: bardzo dobre zrodlo laczace deep learning i klasyfikacje szeregow czasowych.
- Miejsce w pracy: uzasadnienie uzycia CNN/RNN dla przebiegu okrazenia.
- Link: https://doi.org/10.1007/s10618-019-00619-1

**Bagnall et al. (2017), The great time series classification bake off**

- Do czego uzyc: klasyczne porownanie metod time series classification.
- Miejsce w pracy: przeglad klasyfikacji szeregow czasowych.
- Link: https://doi.org/10.1007/s10618-016-0483-9

**InceptionTime (2019), Finding AlexNet for Time Series Classification**

- Do czego uzyc: nowoczesne CNN dla time series classification.
- Miejsce w pracy: opcjonalnie jako inspiracja/future work, jesli nie chcemy rozbudowywac teorii za bardzo.
- Link: https://arxiv.org/abs/1909.04939

**ROCKET (2020), random convolutional kernels**

- Do czego uzyc: alternatywne podejscie do time series classification oparte na losowych konwolucjach.
- Miejsce w pracy: future work, ewentualny kolejny model do sprawdzenia.
- Link: https://arxiv.org/abs/1910.13051

### Narzedzia deep learning / implementacja

**TensorFlow white paper**

- Do czego uzyc: formalne zrodlo dla TensorFlow jako frameworka obliczeniowego.
- Miejsce w pracy: narzedzia implementacyjne.
- Link: https://arxiv.org/abs/1603.04467

**Keras**

- Do czego uzyc: jesli w pracy jawnie wymieniamy Keras jako API do budowy sieci.
- Miejsce w pracy: narzedzia implementacyjne, raczej nie teoria.
- Link: https://github.com/keras-team/keras

## Ktore zrodla sa "must have"

Gdybym mial wybrac minimalny, sensowny zestaw do teorii, dalbym:

1. Bishop albo Hastie/Tibshirani/Friedman jako ogolne ML.
2. Pedregosa et al. dla scikit-learn.
3. Breiman dla Random Forest.
4. Chen i Guestrin dla XGBoost, jesli zostaje w pracy.
5. Goodfellow/Bengio/Courville jako deep learning.
6. LeCun/Bengio/Hinton jako prestizowy przeglad deep learning.
7. LeCun et al. 1998 albo Fawaz et al. 2019 dla CNN/time series.
8. Hochreiter/Schmidhuber dla LSTM.
9. Cho et al. dla GRU.
10. Kingma/Ba dla Adam.
11. Srivastava et al. dla Dropout.
12. Fawaz et al. dla deep learning time series classification.
13. FastF1 docs dla danych.
14. 2-4 prace driver identification / CAN-BUS.
15. 1-3 prace motorsport telemetry / Formula SAE / Mine4Race.

Taki zestaw spokojnie daje akademicki fundament pod rozdzial teoretyczny i metodyczny.
