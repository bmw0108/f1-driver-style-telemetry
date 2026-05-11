from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


EXPORT_DIR = Path("exports")
FIG_DIR = Path("figures") / "thesis"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def export_csv(df: pd.DataFrame, name: str) -> Path:
    path = EXPORT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    return path


def savefig(name: str) -> Path:
    path = FIG_DIR / name
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight", dpi=220)
    plt.close()
    return path


def plot_research_arc() -> Path:
    rows = [
        {"stage": "1. Kierowca\nz telemetrii", "result": "Model rozpoznaje kierowcę", "score": 0.9147},
        {"stage": "2. Kontrola\nzespołu", "result": "Zespół też ma podpis", "score": 0.8240},
        {"stage": "3. Ten sam\nzespół", "result": "Styl nie znika w jednym aucie", "score": 0.8820},
        {"stage": "4. Transfer\nstylu", "result": "Część stylu przenosi się", "score": 0.6480},
    ]
    df = pd.DataFrame(rows)
    plt.figure(figsize=(12, 5.5))
    ax = sns.barplot(data=df, x="stage", y="score", color="#4c78a8")
    ax.set_title("Klamra badawcza: od klasyfikacji do interpretacji stylu")
    ax.set_xlabel("")
    ax.set_ylabel("Przykładowa metryka")
    ax.set_ylim(0, 1)
    for idx, row in df.iterrows():
        ax.text(idx, row["score"] + 0.025, row["result"], ha="center", va="bottom", fontsize=10)
    return savefig("22_thesis_research_arc.png")


def plot_transfer_case_studies() -> Path:
    summary = pd.read_csv(EXPORT_DIR / "driver_style_transfer_stability_summary.csv")
    selected = summary[summary["Driver"].isin(["OCO", "GAS", "ALO", "RIC", "SAI", "BOT"])].copy()
    selected["case_type"] = selected["Driver"].map(
        {
            "OCO": "mocny przykład",
            "GAS": "mocny przykład",
            "ALO": "mocny przykład",
            "RIC": "częściowy przykład",
            "SAI": "kontrprzykład",
            "BOT": "kontrprzykład",
        }
    )
    selected = selected.sort_values("median_similarity", ascending=False)
    export_csv(selected, "thesis_selected_transfer_case_studies")

    plt.figure(figsize=(11, 5.8))
    ax = sns.barplot(
        data=selected,
        x="Driver",
        y="median_similarity",
        hue="case_type",
        dodge=False,
        palette={
            "mocny przykład": "#59a14f",
            "częściowy przykład": "#f28e2b",
            "kontrprzykład": "#e15759",
        },
    )
    ax.axhline(0, color="black", linewidth=1)
    ax.set_title("Wybrane przykłady stabilności stylu po zmianie zespołu")
    ax.set_xlabel("Kierowca")
    ax.set_ylabel("Mediana podobieństwa profilu między zespołami")
    ax.set_ylim(-0.05, 0.8)
    ax.legend(title="")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", fontsize=9)
    return savefig("23_selected_driver_transfer_case_studies.png")


def write_narrative_note() -> Path:
    text = """# Proponowana klamra badawcza pracy

## Główna narracja

Praca może być poprowadzona jako przejście od prostego pytania klasyfikacyjnego do interpretacji stylu i dopasowania kierowca-samochód.

1. Najpierw sprawdzam, czy z samej telemetrii można rozpoznać kierowcę.
2. Następnie pokazuję, że wynik nie jest trywialny, bo w danych istnieje także podpis zespołu/samochodu.
3. Potem kontroluję ten problem przez testy w tym samym zespole, np. Ferrari 2025 HAM vs LEC.
4. Na końcu sprawdzam, czy elementy stylu kierowcy są częściowo stabilne po zmianie samochodu.

## Dlaczego to jest mocne

Taka struktura pokazuje, że praca nie kończy się na wyniku klasyfikatora. Model jest użyty jako narzędzie do badania bardziej motorsportowego problemu: czy styl kierowcy jest mierzalny, na ile miesza się z charakterystyką auta i czy może przenosić się między zespołami.

## Jak uniknąć zarzutu cherry-pickingu

W głównej pracy można pokazać wybrane case studies, ale trzeba jawnie napisać kryterium:

- wybieram przykłady z wystarczającą liczbą okrążeń i zmianą zespołu,
- pokazuję zarówno mocne przykłady stabilności, jak i kontrprzykłady,
- pełna tabela wyników znajduje się w dodatku lub w repozytorium.

Rekomendowany zestaw:

- OCO, GAS, ALO jako mocniejsze przykłady stabilności,
- RIC jako częściowo stabilny i bardzo ciekawy motorsportowo przypadek,
- SAI i BOT jako kontrprzykłady, gdzie profil mocniej zależy od samochodu/kontekstu.

## Proponowany wniosek

Wyniki sugerują, że styl kierowcy nie jest ani całkowicie niezależny od samochodu, ani całkowicie przez samochód determinowany. Publiczna telemetria pozwala uchwycić powtarzalne wzorce jazdy, ale ich interpretacja wymaga kontroli wpływu zespołu, samochodu i sezonu.
"""
    path = Path("THESIS_FINAL_RESEARCH_ARC_PL.md")
    path.write_text(text, encoding="utf-8")
    return path


def main() -> None:
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams["font.family"] = "DejaVu Sans"
    paths = [
        plot_research_arc(),
        plot_transfer_case_studies(),
    ]
    note = write_narrative_note()
    print("Thesis narrative case-study figures created:")
    for path in paths:
        print(f"- {path}")
    print(f"Note: {note}")


if __name__ == "__main__":
    main()
