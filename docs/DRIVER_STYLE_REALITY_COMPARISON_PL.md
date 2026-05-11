# Porownanie interpretacji modelu z publicznie opisywanym stylem kierowcow

## Jak to rozumiec

To porownanie nie jest "walidacja absolutna". To jest walidacja jakosciowa:

- z jednej strony mamy wzorce wyuczone przez model na danych telemetrycznych,
- z drugiej strony mamy publicznie opisywane preferencje i cechy stylu kierowcow,
- sprawdzamy, czy oba obrazy sa ze soba zgodne przynajmniej na poziomie kierunku interpretacji.

W pracy najlepiej przedstawic to jako triangulacje:

- dane telemetryczne,
- interpretacja modelu,
- zewnetrzny opis ekspercki lub wypowiedzi kierowcow / analitykow.

## Ogolny wniosek

Na tym etapie najsilniejsza zgodnosc jakosciowa wystepuje dla:

- `VER`,
- `LEC`,
- w mniejszym stopniu `SAI` i `ALB`.

Dla `OCO` model daje bardzo wyrazny profil hamowania, ale publicznie dostepne zrodla, ktore znalezlismy, sa na razie zbyt slabe lub zbyt posrednie, zeby traktowac to jako mocne niezalezne potwierdzenie.

## Obserwacja do zapamietania

Jednym z wazniejszych celow projektu bylo nie tylko sprawdzenie, czy model potrafi rozpoznac kierowce, ale tez czy rozpoznane przez niego cechy da sie powiazac z realnie opisywanym stylem jazdy. Dla `VER` i `LEC` mamy wlasnie taki przypadek: interpretacja modelu jest zgodna z publicznymi opisami ich preferencji i sposobu prowadzenia auta.

W przypadku `VER` model wskazuje wzorzec bardzo zdecydowanego operowania gazem: wysoki udzial pelnego gazu, niski udzial sredniego otwarcia przepustnicy i duza dynamike zmian sygnalu gazu. To dobrze pasuje do publicznego opisu Verstappena jako kierowcy lubiacego bardzo czuly przod auta, szybkie ustawienie samochodu i mocny, wczesny powrot do gazu.

W przypadku `LEC` model wskazuje inny, ale rownie czytelny wzorzec: mniej pelnego odjecia gazu, wyzsze minimalne wartosci przepustnicy i bardziej ciagle podtrzymywanie napedu. To jest spojne z opisami Leclerca jako kierowcy dobrze czujacego sie w aucie bardziej nadsterownym i wymagajacym, ktore pozwala mu utrzymywac agresywna, ale plynna kontrole samochodu.

Ta obserwacja jest wazna, bo pokazuje, ze model nie tylko osiaga dobry wynik klasyfikacji, ale w przynajmniej kilku przypadkach wykrywa wzorce, ktore maja sens motorsportowy i daja sie zestawic z wiedza ekspercka oraz wypowiedziami kierowcow. Jednoczesnie nie trzeba oczekiwac takiej zgodnosci dla kazdego kierowcy. Wnioskiem moze byc wlasnie to, ze u czesci kierowcow styl jest wystarczajaco charakterystyczny, aby model wykryl go i aby dalo sie go porownac z opisami zewnetrznymi.

## 1. Max Verstappen (`VER`)

### Co mowia zrodla zewnetrzne

Publiczne opisy stylu Verstappena sa wyjatkowo spojne. Zrodla eksperckie i wypowiedzi innych kierowcow opisuja go jako zawodnika preferujacego bardzo "pointy" przod auta, czyli bardzo czuly i bezposredni przod, pozwalajacy szybciej ustawic samochod do wyjscia z zakretu i wczesniej wracac do gazu. Jednoczesnie taka charakterystyka wymaga tolerowania nerwowego tylu auta.

### Co wyszlo w naszym modelu

W naszym zbiorze `VER` mial:

- najwyzszy udzial jazdy z pelnym gazem,
- bardzo niski udzial jazdy na srednim gazie,
- wysoka zmiennosc sygnalu przepustnicy,
- niski poziom aktywnosci hamulca na tle grupy.

### Ocena zgodnosci

To jest mocna zgodnosc jakosciowa. Publiczny opis "bardzo czuly przod, szybkie ustawienie auta, wczesniejszy i mocniejszy powrot do gazu" dobrze pasuje do telemetrycznego obrazu, w ktorym `VER` czesciej jedzie na pelnym gazie, rzadziej "wisi" w strefie sredniego otwarcia przepustnicy i ma bardziej zdecydowane przejscia w operowaniu gazem.

## 2. Charles Leclerc (`LEC`)

### Co mowia zrodla zewnetrzne

W przypadku `LEC` mamy dwa wazne typy sygnalow z zewnatrz. Po pierwsze, sam Leclerc mowil, ze bardziej nadsterowna charakterystyka auta daje mu przewage, nawet jesli jest trudniejsza w prowadzeniu. Po drugie, `SAI` opisywal jego sposob prowadzenia Ferrari jako bardzo szybki i na poczatku trudny do uwierzenia po analizie danych.

### Co wyszlo w naszym modelu

W naszym zbiorze `LEC` wyroznial sie przez:

- bardzo niski udzial jazdy bez gazu,
- najwyzszy dolny kwantyl przepustnicy,
- stosunkowo plynny profil gazu,
- wyzszy udzial jazdy przy srednim gazie niz u `VER`.

### Ocena zgodnosci

To jest zgodnosc czesciowa, ale przekonujaca. Zrodla zewnetrzne nie mowia wprost "Leclerc utrzymuje wyzsze minimalne otwarcie gazu", ale mowia, ze dobrze czuje sie z bardziej wymagajacym, nadsterownym autem i ze jego styl byl dla `SAI` telemetrycznie bardzo charakterystyczny. Nasze wyniki wspieraja obraz kierowcy, ktory rzadziej calkowicie odpuszcza przepustnice i bardziej ciagle podtrzymuje naped.

## 3. Carlos Sainz (`SAI`)

### Co mowia zrodla zewnetrzne

Publiczny obraz `SAI` jest bardziej "smooth" niz "aggressive". Trzeba jednak uwazac, bo sama etykieta "Smooth Operator" jest czesciowo memem i nie powinna byc glownym argumentem naukowym. Dużo lepsze sa dwa inne tropy:

- oficjalna analiza Formula1.com z czerwca 2022 wskazywala, ze bardzo "pointy" przod Ferrari F1-75 nie pasowal do jego naturalnego stylu,
- w materiale Motorsport z grudnia 2021 Leclerc wskazywal, ze mocna strona `SAI` to zarzadzanie wyscigiem i oponami.

### Co wyszlo w naszym modelu

W naszym zbiorze `SAI` nie byl skrajny ani po stronie gazu, ani po stronie hamulca. Jego profil byl bardziej zrownowazony:

- mniej ekstremalny niz `VER` i `LEC`,
- oparty bardziej na rytmie zmian gazu i obrotow,
- bez bardzo wyraznego jednego dominujacego wzorca.

### Ocena zgodnosci

To jest zgodnosc umiarkowana. Zewnetrzny obraz `SAI` jako kierowcy mniej naturalnie zgranego z bardzo ostrym przodem i bardziej "zarzadzajacego" przebiegiem przejazdu dobrze pasuje do tego, ze nasz model nie wykryl u niego tak skrajnego profilu jak u `VER`, `LEC` czy `OCO`.

## 4. Alexander Albon (`ALB`)

### Co mowia zrodla zewnetrzne

W grudniu 2023 Formula1.com cytowalo Albona, ktory mowil wprost, ze jego styl jest raczej po gladkiej, plynnej stronie, chociaz rownoczesnie lubi auto z dobrym, ostrym przodem. W tym samym materiale podkreslal, ze styl Verstappena jest pod tym wzgledem jeszcze bardziej ekstremalny.

### Co wyszlo w naszym modelu

W naszym zbiorze `ALB` mial:

- wysoki udzial jazdy bez gazu,
- nizszy udzial jazdy z pelnym gazem niz `VER` i `LEC`,
- nizsza srednia przepustnice,
- profil mniej dominujacy i slabiej rozroznialny niz u `VER`, `LEC` i `OCO`.

### Ocena zgodnosci

To jest zgodnosc czesciowa i ostrozna. Z jednej strony nie widzimy u `ALB` tak agresywnego profilu pelnego gazu jak u `VER`, co pasuje do bardziej gladkiego obrazu z wypowiedzi publicznych. Z drugiej strony `ALB` byl w naszej finalnej grupie jednym z trudniejszych kierowcow do rozpoznania, wiec te interpretacje trzeba prezentowac ostrozniej.

## 5. Esteban Ocon (`OCO`)

### Co mowia zrodla zewnetrzne

Na razie nie znalezlismy rownie mocnego, prostego i wiarygodnego publicznego opisu stylu `OCO`, jak w przypadku `VER` lub `ALB`. Sa jedynie posrednie tropy:

- w materiale Motorsport z czerwca 2021 `OCO` mowil, ze wspolczesna Formula 1 coraz mocniej "robi czas na hamowaniu",
- w zapowiedziach i analizach bywa opisywany jako kierowca dobrze odnajdujacy sie w trudnych pojedynkach i przy poznych fazach hamowania, ale nie mamy na razie jednego zrodla, ktore nadawaloby sie do mocnej walidacji akademickiej.

### Co wyszlo w naszym modelu

W naszym zbiorze `OCO` wyroznial sie najmocniej po stronie hamowania:

- najwyzszy `brake_active_frac`,
- najwyzszy `brake_on_count`,
- wysoka zmiennosc sygnalu hamulca,
- profil bardziej "hamulcowy" niz "gazowy".

### Ocena zgodnosci

Na razie to jest raczej hipoteza niz mocne porownanie z rzeczywistoscia. Model bardzo wyraznie widzi charakterystyczny podpis hamowania u `OCO`, ale zewnetrzne zrodla, ktore mamy, sa za slabe, by napisac, ze zostalo to niezaleznie potwierdzone.

## Jak to najlepiej napisac w pracy

Najbezpieczniejsza forma bedzie taka:

1. Najpierw opisac, jakie cechy byly najwazniejsze dla modelu.
2. Potem pokazac profile 3-5 kierowcow.
3. Na koniec dodac podrozdzial "Porownanie z publicznie opisywanym stylem jazdy", ale wyraznie zaznaczyc, ze jest to walidacja jakosciowa.

Przykladowa formulacja:

"W przypadku czesci kierowcow interpretacja uzyskana z danych telemetrycznych jest zgodna z publicznie opisywanymi preferencjami stylu jazdy. Najmocniej widac to dla Maxa Verstappena, ktory w zrodlach eksperckich opisywany jest jako kierowca preferujacy bardzo czuly przod auta i zdolny do wczesnego, zdecydowanego powrotu do gazu. W naszym modelu odpowiada temu wysoki udzial jazdy z pelnym gazem, niski udzial jazdy na srednim otwarciu przepustnicy oraz wysoka dynamika zmian sygnalu gazu. Zgodnosc ta ma charakter jakosciowy, ale wzmacnia interpretacje, ze model wychwycil nie przypadkowe roznice, lecz rzeczywiste wzorce stylu jazdy."

## Zrodla

- Formula1.com, 4 grudnia 2023, o stylu Verstappena i wypowiedzi Albona:
  - https://www.formula1.com/en/latest/article/its-eye-watering-albon-shares-the-secrets-of-verstappens-unique-driving.3Dlce2QkRGzUDLMtDf3dOs
- The Race, 6 stycznia 2025, o "pointy front end" Verstappena:
  - https://www.the-race.com/formula-1/what-is-a-pointy-front-end-max-verstappen-f1-preference/
- Motorsport, 6 lutego 2023, o preferencji Verstappena do bardziej nadsterownego, zwinnego przodu:
  - https://www.motorsport.com/f1/news/verstappen-an-understeery-f1-car-will-never-be-quick/10419462/
- Formula1.com, 21 czerwca 2022, o tym, ze "pointy front end" Ferrari nie pasowal Sainzowi:
  - https://www.formula1.com/en/latest/article/why-smart-capable-sainz-can-still-be-a-factor-in-the-2022-title-fight.22F1Sj2iX6EmbUOBqhry0o
- Formula1.com, 29 lipca 2022, o tym, ze Leclerc dobrze czuje sie z bardziej nadsterownym autem:
  - https://www.formula1.com/en/latest/article/leclerc-says-france-crash-wont-change-his-driving-style-thats-what-gave-me.7rZKOErcfIT3kmjL72e0nn
- Motorsport, 22 grudnia 2021, o wypowiedzi Sainza na temat bardzo charakterystycznego stylu Leclerca:
  - https://www.motorsport.com/f1/news/sainz-hard-to-believe-leclercs-crazy-quick-ferrari-driving-style/6926257/
- Formula1.com, 10 maja 2019, obserwacja trackside dotyczaca Sainza:
  - https://www.formula1.com/en/latest/article/trackside-performance-analysis-comparing-the-teams-at-barcelona.DrYv8O364XB6MFoxZ2Pgg
