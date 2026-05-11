# Writing Style Reference

Ten plik opisuje styl poprzedniej pracy magisterskiej uzytkownika (`praca_magisterska (8).pdf`) i ma sluzyc jako punkt odniesienia przy dalszej redakcji obecnej pracy o Formule 1.

## Ogolny uklad

- Wstep jest pisany jako plynna narracja, a nie jako wiele krotkich podsekcji.
- Najpierw pojawia sie kontekst problemu, potem krotkie wyjasnienie uzywanych metod, a na koncu opis tego, co bedzie w kolejnych czesciach pracy.
- Teoria jest osobnym duzym rozdzialem przed danymi i eksperymentami.
- Rozdzial teoretyczny opisuje modele po kolei: intuicja, prosty opis, czasem wzor, czasem rysunek, potem komentarz praktyczny.
- Rozdzial danych zaczyna sie od prostego uzasadnienia, ze przed analiza trzeba dane opisac, zrozumiec i przygotowac.
- Czesc eksperymentalna idzie modelem po modelu, a nie od razu przez jedna wielka tabele wynikow.

## Ton i sposob pisania

- Styl jest raczej prosty i bezposredni, bez nadmiernie akademickiego tonu.
- Dobrze dziala forma "w tej pracy sprawdzono/uzyto", ale mozna tez stosowac pierwsza osobe liczby mnogiej w roboczym draftcie.
- Zdania powinny byc zrozumiale i praktyczne: najpierw po co cos robimy, potem jak, potem co z tego wynika.
- Unikac zbyt wielu malych podrozdzialow, jesli kazdy ma tylko kilka zdan.
- Lepiej miec mniej sekcji, ale kazda powinna prowadzic czytelnika przez konkretny temat.

## Styl rozdzialow teoretycznych

Dla kazdego modelu dobrze trzymac schemat:

1. Krotkie wyjasnienie, do czego model sluzy.
2. Intuicyjny opis dzialania.
3. Wzor lub schemat, jesli faktycznie pomaga.
4. Informacja, dlaczego model jest uzywany w tej pracy.
5. Potencjalne ograniczenia, np. przeuczenie, wrazliwosc na outliery, trudniejsza interpretacja.

W obecnej pracy szczegolnie warto tak opisac:

- regresje logistyczna,
- Random Forest / boosting jako modele porownawcze,
- CNN 1D,
- GRU,
- LSTM,
- model hybrydowy CNN + cechy tabularne,
- walidacje krzyzowa i macro F1.

## Styl rozdzialu danych

Dla danych dobrze trzymac schemat:

1. Krotko opisac zrodlo danych.
2. Pokazac, ile danych bylo na starcie.
3. Wyjasnic, czemu dane trzeba filtrowac.
4. Pokazac wykres/tabele.
5. Pod wykresem napisac interpretacje: co jest najwieksza redukcja, czy cos wyglada nietypowo, czy jest to oczekiwane.

Wazna preferencja uzytkownika:

- najpierw opis zjawiska,
- potem wykres/tabela,
- potem komentarz interpretacyjny pod spodem.

Nie robic wykresow tylko po to, zeby byly. Jesli wykres pokazuje prawie same zera albo oczywista informacje, lepiej opisac to tekstem.

## Styl czesci eksperymentalnej

Preferowana narracja:

1. Najpierw opis modelu lub wariantu eksperymentu.
2. Potem wynik/wykres/macierz pomylek.
3. Potem komentarz, co ten wynik oznacza.
4. Dopiero po kilku modelach zbiorcza tabela porownawcza.

W obecnej pracy warto prowadzic badania w tej kolejnosci:

- regresja logistyczna jako interpretowalny punkt odniesienia,
- CNN jako pierwszy model sekwencyjny,
- hybryda CNN + cechy tabularne,
- GRU/LSTM jako porownanie i wyjasnienie, czemu byly slabsze,
- tabela podsumowujaca wszystkie setupy,
- analiza cech i macierzy pomylek.

## Co przeniesc do aktualnej pracy

- Wstep powinien byc bardziej narracyjny i mniej poszatkowany.
- Teoria powinna byc rozbudowana tak, aby kazdy uzyty model mial prosty opis i uzasadnienie.
- W EDA nalezy unikac wykresow bez mocnego komentarza.
- Przy kazdym rysunku powinien byc komentarz interpretacyjny po rysunku.
- Czesci praktyczne powinny byc pisane "krok po kroku", a nie tylko jako zbiorcze wyniki.

## Czego nie kopiowac bezposrednio

- Nie kopiowac sformulowan ani fragmentow tekstu ze starej pracy.
- Nie powtarzac zbyt dlugich list narzedzi, jesli mozna je opisac zwiezlej.
- Nie zostawiac wynikow bez wniosku pod spodem.
- Nie konczyc pracy zbyt szybko po eksperymentach; w obecnej pracy potrzebna bedzie wyrazniejsza dyskusja, ograniczenia i dalsze kierunki.
