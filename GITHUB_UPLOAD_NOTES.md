# GitHub upload notes

Ten folder jest przygotowaną paczką repozytorium, a nie pełną kopią katalogu roboczego `mgr`.

Zawartość:

- `01_*.ipynb`--`09_*.ipynb` - główne notebooki badawcze.
- `scripts/` - najnowsze skrypty `.py`, z których powstały późniejsze notebooki.
- `exports/` - CSV mniejsze niż 50 MB.
- `figures/` - grafiki używane w notebookach i pracy.
- `thesis_latex/` - aktualny kod LaTeX, bibliografia, klasa `mgr.cls`, logo i figury pracy.
- `docs/` - notatki metodologiczne, status projektu i pomocnicze opisy wyników.
- `pdf_reference/` - lokalne PDF-y poglądowe; są ignorowane przez Git przez regułę `*.pdf`.

Sugerowana ścieżka:

```bash
git init
git add .
git status
git commit -m "Initial thesis project structure"
git branch -M main
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```

Przed `git commit` warto sprawdzić `git status`, czy nie wchodzi żaden przypadkowo duży plik.
