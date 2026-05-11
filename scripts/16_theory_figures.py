from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
FIG_DIR = ROOT / "figures" / "thesis"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def savefig(name: str) -> None:
    plt.tight_layout()
    plt.savefig(FIG_DIR / name, dpi=180, bbox_inches="tight")
    plt.close()


def logistic_sigmoid() -> None:
    x = np.linspace(-8, 8, 400)
    y = 1 / (1 + np.exp(-x))

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(x, y, color="#2f6f8f", linewidth=3)
    ax.axhline(0.5, color="#444444", linestyle="--", linewidth=1.3)
    ax.axvline(0, color="#c7673b", linestyle="--", linewidth=1.3)
    ax.fill_between(x, 0, y, where=x < 0, color="#9fb7c9", alpha=0.25, label="niższe prawdopodobieństwo klasy")
    ax.fill_between(x, 0, y, where=x >= 0, color="#e0a37d", alpha=0.25, label="wyższe prawdopodobieństwo klasy")
    ax.set_title("Funkcja logistyczna jako przejście od wyniku liniowego do prawdopodobieństwa")
    ax.set_xlabel("wynik liniowy modelu")
    ax.set_ylabel("prawdopodobieństwo klasy")
    ax.set_ylim(-0.03, 1.03)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, loc="lower right")
    savefig("30_theory_logistic_sigmoid.png")


def cnn_1d_concept() -> None:
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.axis("off")

    colors = {
        "input": "#d9e6ef",
        "conv": "#f0c38e",
        "pool": "#d7d4f0",
        "dense": "#b9d8b4",
        "out": "#e5a1a1",
    }

    blocks = [
        (0.05, 0.32, 0.16, 0.36, "Sekwencja\ntelemetrii\nSpeed, Throttle,\nBrake, RPM, nGear", colors["input"]),
        (0.29, 0.38, 0.13, 0.24, "Filtry\nkonwolucyjne\n1D", colors["conv"]),
        (0.49, 0.38, 0.12, 0.24, "Agregacja\nlokalnych\nwzorców", colors["pool"]),
        (0.68, 0.38, 0.12, 0.24, "Warstwa\nłącząca", colors["dense"]),
        (0.86, 0.38, 0.09, 0.24, "Kierowca", colors["out"]),
    ]

    for x, y, w, h, text, color in blocks:
        rect = plt.Rectangle((x, y), w, h, facecolor=color, edgecolor="#333333", linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=10)

    for i in range(len(blocks) - 1):
        x1 = blocks[i][0] + blocks[i][2]
        y1 = blocks[i][1] + blocks[i][3] / 2
        x2 = blocks[i + 1][0]
        y2 = blocks[i + 1][1] + blocks[i + 1][3] / 2
        ax.annotate("", xy=(x2 - 0.015, y2), xytext=(x1 + 0.015, y1), arrowprops=dict(arrowstyle="->", linewidth=1.8))

    t = np.linspace(0, 1, 120)
    for i, offset in enumerate([0.78, 0.73, 0.68, 0.63, 0.58]):
        ax.plot(0.06 + 0.13 * t, offset + 0.025 * np.sin(2 * np.pi * (t * (i + 1.2))), color="#2f6f8f", linewidth=1.2)

    ax.text(0.5, 0.12, "CNN 1D szuka lokalnych wzorców w przebiegu okrążenia, np. fragmentów hamowania, wejścia na gaz albo zmian biegów.", ha="center", fontsize=11)
    savefig("31_theory_1d_cnn_concept.png")


def grouped_cv_concept() -> None:
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.set_title("Walidacja grupowana: okrążenia z tej samej sesji nie trafiają jednocześnie do treningu i testu")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    sessions = ["Sesja A", "Sesja B", "Sesja C", "Sesja D", "Sesja E"]
    colors = ["#4c78a8", "#59a14f", "#f28e2b", "#b07aa1", "#e15759"]
    for i, (session, color) in enumerate(zip(sessions, colors)):
        x = 0.7 + i * 1.8
        for j in range(4):
            ax.add_patch(plt.Rectangle((x + j * 0.22, 3.3), 0.18, 0.35, facecolor=color, edgecolor="white"))
        ax.text(x + 0.35, 3.85, session, ha="center", fontsize=10)

    folds = [
        ("Fold 1", ["train", "train", "test", "train", "train"]),
        ("Fold 2", ["test", "train", "train", "train", "train"]),
        ("Fold 3", ["train", "test", "train", "train", "test"]),
    ]
    for row, (fold, states) in enumerate(folds):
        y = 2.35 - row * 0.7
        ax.text(0.05, y + 0.13, fold, ha="left", fontsize=10)
        for i, state in enumerate(states):
            x = 0.75 + i * 1.8
            face = "#d9e6ef" if state == "train" else "#c7673b"
            label = "trening" if state == "train" else "test"
            ax.add_patch(plt.Rectangle((x, y), 1.05, 0.38, facecolor=face, edgecolor="#333333", linewidth=1))
            ax.text(x + 0.525, y + 0.19, label, ha="center", va="center", fontsize=9)

    ax.text(5, 0.25, "Taki podział zmniejsza ryzyko, że model nauczy się specyfiki jednej sesji zamiast cech kierowcy.", ha="center", fontsize=11)
    savefig("32_theory_grouped_cv.png")


def main() -> None:
    logistic_sigmoid()
    cnn_1d_concept()
    grouped_cv_concept()
    print("Generated theory figures 30-32.")


if __name__ == "__main__":
    main()
