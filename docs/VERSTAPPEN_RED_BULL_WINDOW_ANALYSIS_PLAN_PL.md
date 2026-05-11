# Hipoteza: "auto pod Verstappena" i waskie okno pracy Red Bulla

## Punkt wyjscia

W dyskusji publicznej czesto pojawia sie teza, ze samochody Red Bulla w erze Verstappena sa bardzo trudne dla drugiego kierowcy, poniewaz wymagaja stylu jazdy z bardzo ostrym przodem, szybka reakcja auta i mala tolerancja na blad. Alex Albon opisywal to obrazowo jako jazde z "myszka na 100% sensitivity". Christian Horner rowniez wskazywal, ze Verstappen lubi bardzo pozytywny przod i ostry turn-in.

To jest ciekawy watek dla pracy, ale trzeba go traktowac ostroznie:

- nie mamy realnych ustawien samochodu,
- nie mamy pelnego steering angle,
- nie mamy danych aerodynamicznych ani setup sheets,
- publiczna telemetria nie pozwala udowodnic, ze samochod byl projektowany "pod Maxa".

Mozemy natomiast zbadac proxy tego zjawiska:

> Czy w danych telemetrycznych widac, ze Red Bull Verstappena wymaga profilu jazdy trudniejszego dla partnerow zespolowych oraz czy roznice miedzy Verstappenem a partnerami sa szczegolnie widoczne w cechach zwiazanych z kontrola auta, gazem, hamowaniem, minimalna predkoscia i dynamika sygnalow?

## Jak to mozna podpiac pod prace

Nie powinno to zastapic glownego tematu pracy. Najlepsze miejsce:

- rozdzial dyskusyjny,
- sekcja o biasie zespolowym,
- sekcja future work,
- ewentualnie krotkie case study: "czy modele moga wspierac analize dopasowania kierowca-samochod?".

Najlepsza narracja:

> Glowny model pokazuje, ze kierowca zostawia mierzalny podpis w telemetrii. Naturalnym rozszerzeniem jest pytanie, czy ten podpis mozna zestawic z charakterystyka samochodu i wykorzystac do analizy dopasowania kierowcy do auta.

## Dane lokalne: dostepnosc Red Bulla

W czystych kwalifikacjach 2018-2025 mamy liczbe reprezentatywnych okrazen:

- `VER, Red Bull Racing`: 144,
- `PER, Red Bull Racing`: 70,
- `ALB, Red Bull Racing`: 24,
- `GAS, Red Bull Racing`: 12,
- `RIC, Red Bull Racing`: 17,
- `TSU, Red Bull Racing`: 19,
- `LAW, Red Bull Racing`: 2.

To oznacza:

- najlepszy kandydat do pelniejszego porownania to `VER vs PER`,
- `VER vs ALB` i `VER vs GAS` sa ciekawe, ale male probkowo,
- mozna tez zrobic laczny zbior "teammates vs VER", ale trzeba uwazac, bo mieszamy kierowcow i sezony.

## Co mozemy sprawdzic bez nowych danych

### 1. Gap telemetryczny Verstappen vs partner zespolowy

Porownanie w ramach tych samych sesji:

- roznice cech telemetrycznych,
- roznice w lap time,
- roznice w minimalnej predkosci,
- roznice w throttle/brake dynamics,
- roznice w gear/RPM dynamics.

Najwazniejsze: porownywac tylko te sesje, gdzie obaj kierowcy maja czyste reprezentatywne okrazenie.

### 2. Czy partnerzy Red Bulla sa bardziej myleni / mniej stabilni

Mozna sprawdzic:

- recall Verstappena vs recall partnerow,
- czy model latwiej rozpoznaje Verstappena niz drugiego Red Bulla,
- czy drugi Red Bull jest bardziej "rozmyty" w przestrzeni cech.

### 3. Czy Red Bull ma bardziej ekstremalny podpis zespolowy

Z istniejacej analizy team-bias:

- Red Bull 2025 ma wysokie speed mean/min,
- wysoki full throttle,
- niski mid throttle,
- niska brake activity,
- mniej gear changes.

Interpretacja proxy:

- samochod, ktory pozwala utrzymac wysoka minimalna predkosc i szybko wracac na gaz, moze byc bardzo szybki,
- ale jesli wymaga agresywnego turn-in i stabilnosci kierowcy na granicy przyczepnosci, moze byc trudniejszy dla partnera.

### 4. Czy "okno" da sie zoperacjonalizowac liczbowo

Nie mamy setup window, ale mozemy zdefiniowac proxy:

- niska wariancja skutecznego stylu Verstappena: model widzi bardzo konsekwentny profil,
- duza roznica teammate-Verstappen w tej samej sesji,
- duzy spadek partnera w cechach wymagajacych precyzji: throttle transition, brake release, speed minimum, RPM/gear dynamics,
- wieksza liczba okrazen partnera odrzuconych przez filtry jakosciowe lub wieksza zmiennosc lap time, jesli dane to potwierdza.

## Co wymagaloby nowej pracy / dodatkowego skryptu

Najlepszy mini-eksperyment:

1. Wybrac wszystkie sesje Red Bulla 2018-2025, gdzie VER i teammate maja czyste okrazenia.
2. Wyciagnac telemetrie dla tych okrazen, jesli nie jest juz w merged telemetry.
3. Zbudowac cechy per lap analogiczne do obecnego pipeline'u.
4. Zrobic tabele `VER minus teammate` per session.
5. Zrobic wykresy po sezonach:
   - lap time gap,
   - speed_min / speed_mean gap,
   - throttle_full_frac gap,
   - throttle_diff_mean / throttle transition,
   - brake_active_frac / brake_on_count,
   - gear_change_count / RPM dynamics.
6. Sprawdzic, czy te roznice rosna/maleja w czasie.
7. Porownac do innych zespolow jako kontrola, np. Ferrari `LEC-SAI` lub Mercedes `HAM-RUS`.

## Czego nie wolno twierdzic

Nie wolno napisac:

- "Dane dowodza, ze Red Bull byl projektowany pod Verstappena."
- "Model wykryl ustawienia samochodu."
- "Znamy okno setupowe Red Bulla."

Mozna napisac:

- "Wyniki sa zgodne z hipoteza, ze styl Verstappena i charakterystyka Red Bulla sa silnie dopasowane."
- "Publiczna telemetria pozwala analizowac proxy dopasowania kierowca-samochod."
- "Do potwierdzenia zjawiska potrzebne bylyby dane setupowe, steering angle i pelniejsze dane inzynierskie."

## Czy warto dodawac to do pracy?

Tak, ale raczej jako krotkie case study lub future work, nie jako czwarty duzy filar badan.

Powod:

- temat jest bardzo ciekawy i dobrze laczy dane z rzeczywistoscia F1,
- ale bez steering angle i setup sheets latwo przesadzic z interpretacja,
- obecna praca juz ma wystarczajaco mocny glowny zakres.

Najlepsze uzycie:

> "Jednym z praktycznych zastosowan zaproponowanego podejscia moze byc analiza dopasowania kierowcy do charakterystyki samochodu. Przykladem jest publicznie dyskutowany przypadek Red Bulla i Verstappena, gdzie modele moglyby sluzyc do badania, czy partnerzy zespolowi odbiegaja od profilu telemetrycznego lidera w cechach zwiazanych z kontrola auta."

## Zrodla kontekstowe

- Motorsport.com, analiza zaleznosci Red Bulla od Verstappena i opis auta jako bardzo responsywnego/nieprzebaczajacego: https://www.motorsport.com/f1/news/red-bull-depend-max-verstappen/10709113/
- Formula1.com, Albon o uczeniu sie od Verstappena w Red Bullu: https://www.formula1.com/en/latest/article/albon-learning-from-verstappens-example-in-red-bull-briefings.3f69Ep6TIHyBEYEarKgVxq
- Formula1.com, Horner o sugestiach, ze RB19 jest dopasowany do Verstappena: https://www.formula1.com/en/latest/article.we-just-try-to-build-the-fastest-car-horner-hits-back-at-suggestions-rb19-is.4sVjNvy8lhmdmOhDnmlnBo.html
- Motorsport.com, Verstappen o koniecznosci adaptacji do samochodu: https://www.motorsport.com/f1/news/verstappen-adapt-car-red-bull/10564109/

