# Interpretacja stylu jazdy kierowców - szkic po polsku

## Po co jest ten plik

Ten szkic ma przelozyc wyniki modelu z poziomu "model rozpoznaje kierowce" na poziom bardziej merytoryczny, czyli: jakie wzorce jazdy byly dla modelu najbardziej charakterystyczne i co mozna ostroznie powiedziec o konkretnych kierowcach.

## Bardzo wazne zastrzezenie

Ponizsza interpretacja nie oznacza, ze dany kierowca "zawsze jezdzi w ten sposob" w absolutnym sensie. Wnioski pochodza z konkretnego, kontrolowanego setupu:

- kwalifikacje `2023-2025`,
- warunki suche,
- po jednym reprezentatywnym okrazeniu na kierowce na sesje,
- finalna piecioosobowa grupa: `ALB, SAI, VER, OCO, LEC`.

Dlatego w opisie nalezy uzywac sformulowan typu:

- `w badanym zbiorze`,
- `w porownaniu do pozostalych kierowcow z tej grupy`,
- `w tym setupie model najczesciej kojarzyl danego kierowce z...`.

## Co globalnie bylo najwazniejsze dla modelu

W finalnym, interpretowalnym modelu opartym na regresji logistycznej najwieksze znaczenie mialy przede wszystkim cechy zwiazane z:

- srednim uzyciem biegow (`gear_mean`),
- udzialem jazdy z czesciowo otwarta przepustnica (`throttle_mid_frac`),
- zmiennoscia sygnalu gazu (`throttle_diff_std`, `throttle_diff_abs_mean`, `throttle_std`),
- udzialem czasu bez gazu (`throttle_zero_frac`),
- dolnymi kwantylami przepustnicy (`throttle_p10`),
- dynamika zmian obrotow (`rpm_diff_std`, `rpm_diff_abs_mean`),
- aktywnoscia hamowania (`brake_on_count`, `brake_active_frac`, `brake_diff_std`),
- odchyleniem predkosci w trakcie okrazenia (`speed_std`).

To jest bardzo istotne metodologicznie, bo sugeruje, ze model rozroznial kierowcow glownie po sposobie operowania gazem, hamulcem, skrzynia biegow i dynamice przejazdu, a nie tylko po prostych statystykach typu sam czas okrazenia.

## Kierowcy najlepiej rozpoznawani przez model

W finalnym modelu najlepiej rozpoznawani byli:

- `VER` - recall ok. `0.93`,
- `LEC` - recall ok. `0.89`,
- `OCO` - recall ok. `0.87`.

Slabiej, ale nadal wyraznie ponad przypadek, rozpoznawani byli:

- `SAI` - recall ok. `0.83`,
- `ALB` - recall ok. `0.78`.

To oznacza, ze dla `VER`, `LEC` i `OCO` model znajdowal najbardziej stabilne i czytelne wzorce odrozniajace ich od pozostalej czworki.

## Interpretacja dla konkretnych kierowcow

### Max Verstappen (`VER`)

W badanym zbiorze `VER` byl kojarzony przede wszystkim z bardzo charakterystycznym profilem operowania gazem. Mial najwyzszy udzial jazdy z pelnym gazem (`throttle_full_frac ≈ 0.632`), a jednoczesnie najnizszy udzial jazdy na srednim otwarciu przepustnicy (`throttle_mid_frac ≈ 0.110`). To sugeruje styl bardziej zdecydowany: mniej czasu w "strefie przejsciowej", a wiecej wyraznego przechodzenia miedzy stanem bez gazu i stanem mocnego przyspieszania.

Jednoczesnie `VER` mial najwyzsza zmiennosc sygnalu gazu (`throttle_diff_std ≈ 17.99`, `throttle_diff_abs_mean ≈ 5.93`) oraz wysoki udzial czasu bez gazu (`throttle_zero_frac ≈ 0.174`). W praktyce mozna to interpretowac jako bardziej agresywne lub bardziej zdecydowane operowanie przepustnica: model widzial u niego mniej "utrzymywania sredniego gazu", a bardziej sekwencje wyraznego odjecia i mocniejszego powrotu do przyspieszania.

Po stronie hamowania `VER` wyroznial sie raczej nizsza aktywnoscia hamulca niz `OCO` czy `SAI`: mial najnizszy `brake_on_count` w grupie (`≈ 18.09`) oraz niska wartosc `brake_active_frac` (`≈ 0.170`). Ostrozna interpretacja jest taka, ze w tym setupie model kojarzyl go z bardziej ekonomicznym lub rzadszym inicjowaniem hamowania niz u kierowcow o bardziej "gestym" profilu pracy hamulcem.

### Charles Leclerc (`LEC`)

`LEC` wyroznial sie niemal odwrotnym profilem gazu niz `VER` w kilku kluczowych cechach. Mial zdecydowanie najnizszy udzial jazdy bez gazu (`throttle_zero_frac ≈ 0.068`) oraz najwyzszy dolny kwantyl przepustnicy (`throttle_p10 ≈ 4.33`). To oznacza, ze nawet w dolnych partiach rozkladu jego otwarcie przepustnicy rzadziej spadalo bardzo nisko. Innymi slowy: model widzial u niego bardziej ciagle podtrzymywanie minimalnego lub umiarkowanego napedu, zamiast czestego pelnego odjecia gazu.

Jednoczesnie `LEC` mial nizsza zmiennosc sygnalu przepustnicy niz `VER` czy `ALB` (`throttle_std ≈ 37.06`, `throttle_diff_std ≈ 16.00`) oraz wysoki udzial jazdy przy srednim gazie (`throttle_mid_frac ≈ 0.163`). To wspiera interpretacje, ze w badanym zbiorze jego przejazdy byly dla modelu bardziej "plynne" pod wzgledem modulacji gazu, z mniejsza liczba bardzo ostrych przejsc do zera.

Warto tez zauwazyc, ze `LEC` mial bardzo wysoka srednia predkosc i bardzo dobry czas okrazenia, ale najciekawsze interpretacyjnie sa tutaj nie same wartosci tempa, tylko sposob operowania przepustnica. Wlasnie ten profil - malo czasu bez gazu, wysokie minimum przepustnicy i bardziej ciagle utrzymywanie napedu - byl jednym z najsilniejszych wzorcow odrozniajacych go od reszty.

### Esteban Ocon (`OCO`)

Najbardziej charakterystyczna cecha `OCO` dotyczyla hamowania. Mial najwyzszy udzial aktywnego hamulca (`brake_active_frac ≈ 0.200`), najwyzsza srednia liczbe aktywacji hamulca (`brake_on_count ≈ 23.48`) oraz najwyzsze wartosci cech opisujacych zmiennosc sygnalu hamowania (`brake_diff_std ≈ 0.268`, `brake_diff_abs_mean ≈ 0.072`). To jest najmocniejszy przypadek, w ktorym mozna dosc konkretnie powiedziec, ze model rozpoznawal kierowce po sposobie hamowania.

Na tle pozostalych czterech kierowcow `OCO` wygladal wiec na kierowce o bardziej intensywnym, czesciej aktywowanym profilu pracy hamulcem. Nie oznacza to automatycznie "późniejszego hamowania" w sensie sportowym, ale oznacza, ze z perspektywy modelu telemetrycznego to hamowanie bylo jednym z najbardziej stabilnych i odrożniajacych go wzorcow.

Po stronie gazu `OCO` nie byl tak skrajny jak `VER` czy `LEC`, ale laczyl dosc wysoki udzial czasu bez gazu (`throttle_zero_frac ≈ 0.165`) z wysokimi wartosciami cech hamulcowych. Dlatego jego profil mozna opisac jako bardziej "hamulcowy" niz "przepustnicowy": model nie rozpoznawal go glownie po maksymalnym przyspieszaniu, tylko po sposobie wytracania predkosci i pracy na przejsciu hamowanie-przyspieszanie.

### Carlos Sainz (`SAI`)

`SAI` jest troche mniej skrajny niz `VER`, `LEC` i `OCO`, ale nadal ma wyrazny profil. W jego przypadku wazne byly przede wszystkim cechy zwiazane z dynamika gazu i obrotow, a nie same skrajne poziomy przepustnicy. Mial stosunkowo wysokie wartosci `rpm_diff_abs_max` i `rpm_diff_std`, a jednoczesnie nizsze niz u `VER` wartosci najbardziej agresywnych zmian gazu (`throttle_diff_abs_max` bylo u niego relatywnie niskie na tle grupy).

Mozna to ostroznie odczytac tak, ze `SAI` byl dla modelu mniej charakterystyczny przez pojedyncze skrajne przejscia gazu, a bardziej przez caly rytm zmian w trakcie okrazenia. Dodatkowo mial jedna z nizszych wartosci `gear_change_count` w grupie (`≈ 35.48`), bardzo zblizona do `VER`, co sugeruje, ze skrzynia biegow i sposob rozwijania obrotow tez byly czescia jego profilu.

W opisie tekstowym najlepiej nie nadawac mu jednego prostego hasla typu "kierowca gazu" albo "kierowca hamowania". Rozsadniej napisac, ze `SAI` byl rozpoznawany przez model na podstawie bardziej zrownowazonego zestawu cech zwiazanych z modulacja gazu, dynamika obrotow i rytmem przejazdu, ale jego wzorzec byl mniej skrajny niz u `VER`, `LEC` czy `OCO`.

### Alexander Albon (`ALB`)

`ALB` byl w tej grupie jednym z trudniejszych kierowcow do rozpoznania, ale mimo to model znajdowal u niego kilka stalych cech. Najbardziej rzuca sie w oczy wysoki udzial jazdy bez gazu (`throttle_zero_frac ≈ 0.174`, praktycznie tyle co `VER`), a jednoczesnie nizszy udzial jazdy z pelnym gazem (`throttle_full_frac ≈ 0.584`) i nizsza srednia przepustnica (`throttle_mean ≈ 70.38`), najnizsza w tej piecioosobowej grupie.

To sugeruje profil bardziej zachowawczy po stronie utrzymywania wysokiego napedu: model widzial u `ALB` sporo odjec gazu, ale nie laczyl tego z tak wysokim i czestym pelnym przyspieszeniem jak u `VER`. Dodatkowo `ALB` mial wysoki `rpm_max` oraz podwyzszona zmiennosc gazu (`throttle_std ≈ 40.30`), wiec jego styl nie byl po prostu "spokojny". Bardziej trafny opis jest taki, ze byl to profil z wieksza liczba odjec gazu i mniejsza dominacja pelnego przyspieszania niz u najszybszych i najbardziej zdecydowanych kierowcow z tej grupy.

To dobrze zgadza sie z faktem, ze `ALB` byl czesto mylony z `SAI`: obaj nie tworzyli tak skrajnego wzorca jak `VER` lub `LEC`, ale nadal byli rozroznialni dzieki kombinacji cech przepustnicy i pracy ukladu napedowego.

## Jak to mozna opisac zbiorczo w pracy

Najbezpieczniejszy i jednoczesnie merytorycznie mocny wniosek jest taki, ze model nie rozpoznawal kierowcow na podstawie pojedynczego "sekretnego" parametru, lecz na podstawie calych wzorcow operowania przepustnica, hamulcem, skrzynia biegow i dynamika obrotow. W badanej grupie szczegolnie wyrazne byly trzy typy charakterystyki:

- profil bardziej zdecydowanego przechodzenia miedzy odjeciem gazu a mocnym przyspieszaniem, dobrze widoczny u `VER`,
- profil bardziej ciaglego podtrzymywania napedu i rzadszego pelnego odjecia gazu, dobrze widoczny u `LEC`,
- profil bardziej charakterystyczny po stronie hamowania, szczegolnie czytelny u `OCO`.

`SAI` i `ALB` takze byly rozpoznawalne, ale ich wzorce mialy mniej skrajny charakter i byly bardziej rozlozone pomiedzy kilka cech jednoczesnie.

Szczegolnie wazna obserwacja dotyczy `VER` i `LEC`. W obu przypadkach interpretacja modelu nie jest tylko abstrakcyjnym opisem wspolczynnikow, ale daje sie zestawic z publicznie opisywanym stylem jazdy tych kierowcow. Dla `VER` model wychwycil bardziej zdecydowane przejscia w operowaniu gazem i wysoki udzial pelnego gazu, co pasuje do opisu kierowcy preferujacego bardzo czuly przod auta i szybki powrot do przyspieszania. Dla `LEC` model wskazal bardziej ciagle podtrzymywanie napedu i rzadsze pelne odjecie gazu, co jest spojne z obrazem kierowcy dobrze czujacego sie w bardziej nadsterownym, wymagajacym aucie. To pokazuje, ze przynajmniej dla czesci kierowcow model pozwala przejsc od samego rozpoznawania nazwiska do interpretacji rzeczywistych cech stylu jazdy.

## Co warto dopisac w samej pracy

W rozdziale wynikowym dobrze bedzie podkreslic, ze:

- sa to interpretacje relatywne, a nie absolutne opisy calego stylu kierowcy,
- odnosza sie do konkretnego setupu badawczego,
- najsilniej interpretowalny jest model regresji logistycznej na recznie zdefiniowanych cechach,
- modele sekwencyjne sa lepsze predykcyjnie, ale trudniejsze do bezposredniej interpretacji na poziomie pojedynczych cech.
