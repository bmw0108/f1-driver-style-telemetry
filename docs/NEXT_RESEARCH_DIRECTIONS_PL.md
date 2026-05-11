# Dalsze mozliwe kierunki analizy

## Kontekst

Glowny temat badawczy jest juz dobrze pokryty:

- modele potrafia rozpoznawac kierowcow z telemetrii,
- najskuteczniejsze sa modele sekwencyjne i hybrydowe,
- wyniki daja sie czesciowo interpretowac przez styl jazdy,
- wykryto i opisano bias zespolowy,
- sprawdzono model hierarchiczny `Team -> Driver`,
- sprawdzono wariant team-aware.

Ponizsze punkty to mozliwe rozszerzenia, a nie konieczne warunki domkniecia pracy.

## 1. Same-team case studies

Najbardziej wartosciowy kierunek dodatkowy:

- `HAM` vs `LEC` w Ferrari 2025,
- `LEC` vs `SAI` w Ferrari 2023-2024.

Dlaczego:

- ten sam zespol pozwala lepiej kontrolowac samochod,
- mozna pokazac, ze sygnal kierowcy istnieje mimo wspolnego auta,
- latwo polaczyc wyniki z opisami zewnetrznymi stylu jazdy.

Ten kierunek ma duza wartosc interpretacyjna i pasuje do glownej tezy.

## 2. Driver transfer

Pomysl:

- trenowac model na okresie, gdy kierowca jezdzil w jednym zespole,
- testowac na okresie po zmianie zespolu.

Przyklady:

- `SAI`: McLaren/Ferrari/Williams,
- `HAM`: Mercedes/Ferrari,
- `OCO`: Renault/Alpine/Haas,
- `LEC`: Sauber/Ferrari.

Ryzyko:

- malo probek w niektorych kombinacjach,
- zmienia sie samochod, regulamin i sezon,
- bardzo latwo pomylic styl kierowcy ze zmiana kontekstu.

Warto wspomniec jako ciekawy kierunek przyszlych badan, ale nie musi byc glownym eksperymentem.

## 3. Team-aware model

Sprawdzone:

- dodanie predykcji zespolu jako pomocniczych cech do modelu kierowcy.

Wynik:

- brak wyraznej poprawy,
- minimalny zysk tylko w dlugim horyzoncie kwalifikacyjnym,
- pogorszenie w setupie wyscigowym.

Wniosek:

- informacja o zespole jest wazna jako kontrola biasu,
- ale nie jest obecnie skutecznym sposobem poprawienia finalnego modelu kierowcy.

## 4. Interpretacja roznic zespolowych

Warto zostawic jako osobny podrozdzial:

- zespol tez ma podpis w telemetrii,
- Red Bull, Ferrari, Williams i Haas roznia sie profilami predkosci, gazu, hamowania i biegow,
- czesc tych roznic da sie porownac z publicznymi opisami samochodow.

To dobrze uzupelnia prace, bo pokazuje, ze model rozpoznaje nie tylko kierowce, ale tez charakterystyke techniczna samochodu.

## 5. Segmentacja toru / zakrety

Pomysl:

- przejsc z analizy calego okrazenia do sektorow lub zakretow.

Dlaczego ciekawe:

- styl jazdy moze byc najlepiej widoczny na wejściu/wyjściu z zakretu,
- mozna analizowac hamowanie, apex i powrot do gazu.

Ryzyko:

- obecne laczenie telemetrii i pozycji nie jest jeszcze wystarczajaco precyzyjne do mocnej segmentacji zakretow,
- wymaga lepszego wyrównania czasowego danych car/position.

To dobry kierunek przyszlych badan, ale niekoniecznie do obecnej wersji pracy.

## Rekomendacja

Najbardziej sensowny finalny ksztalt czesci badawczej:

1. Glowny model kierowcy.
2. Interpretacja stylu kierowcow.
3. Porownanie z publicznie opisywanym stylem jazdy.
4. Analiza biasu zespolowego.
5. Same-team case studies jako najmocniejsza kontrola.
6. Model hierarchiczny i team-aware jako sprawdzone, ale slabsze alternatywy.

Driver transfer i segmentacja zakretow lepiej wpisuja sie w rozdzial "Dalsze prace".
