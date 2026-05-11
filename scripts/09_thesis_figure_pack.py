from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


EXPORT_DIR = Path("exports")
FIG_DIR = Path("figures") / "thesis"
FIG_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", context="talk")
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.dpi"] = 220
plt.rcParams["font.family"] = "DejaVu Sans"


def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(EXPORT_DIR / f"{name}.csv")


def savefig(name: str) -> Path:
    path = FIG_DIR / name
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    return path


def model_label(model: str) -> str:
    return {
        "cnn": "CNN",
        "hybrid_cnn_tabular": "Hybryda",
        "gru": "GRU",
        "lstm": "LSTM",
    }.get(model, model)


def pretty_dataset(dataset: str) -> str:
    return {
        "short_qualifying_2023_2025": "Kwalifikacje\n2023-2025",
        "short_qualifying_2023_2025_top5": "Kwalifikacje\n2023-2025",
        "long_qualifying_2018_2025_top5": "Kwalifikacje\n2018-2025",
        "race_2025_clean_laps_top5": "Wyścigi\n2025",
    }.get(dataset, dataset)


def plot_filter_funnels() -> list[Path]:
    setup_specs = [
        ("Kwalifikacje 2023-2025", load_csv("lap_filter_summary"), "01a_filter_funnel_qualifying_2023_2025.png"),
        ("Kwalifikacje 2018-2025", load_csv("lap_filter_summary_2018_2025_strict"), "01b_filter_funnel_qualifying_2018_2025.png"),
        ("Wyścigi 2025", load_csv("race_2025_filter_summary"), "01c_filter_funnel_race_2025.png"),
    ]
    label_map = {
        "00_raw_all_qualifying_laps": "Surowe\ndane",
        "00_raw_race_laps": "Surowe\nokrążenia",
        "01_lap_time_not_null": "Poprawny\nczas",
        "02_dry_sessions_only": "Suche\nsesje",
        "03_is_accurate_true": "Dokładne\nokrążenia",
        "04_not_deleted": "Nieusunięte",
        "05_not_fastf1_generated": "Niegenerowane",
        "06_track_status_eq_1": "Zielony\ntor",
        "07a_personal_best_only": "Najlepsze\nokrążenie",
        "07_not_pit_in_out": "Bez\npit-stopu",
        "08_within_2s_of_stint_median": "Blisko mediany\nstintu",
    }
    paths = []
    for setup, df, filename in setup_specs:
        plot_df = df.copy()
        start = plot_df["n_rows"].iloc[0]
        plot_df["retention_pct"] = plot_df["n_rows"] / start * 100
        plot_df["label"] = plot_df["step"].map(label_map).fillna(plot_df["step"])

        fig, ax = plt.subplots(figsize=(9.2, 4.9))
        sns.lineplot(data=plot_df, x="label", y="retention_pct", marker="o", linewidth=2.5, ax=ax, color="#4c78a8")
        ax.set_title(setup, fontsize=16, pad=10)
        ax.set_xlabel("Etapy filtrowania", fontsize=10, labelpad=6)
        ax.set_ylabel("Pozostało [%]", fontsize=12)
        ax.set_ylim(0, 105)
        ax.grid(axis="y", alpha=0.25)
        ax.tick_params(axis="x", rotation=0, labelsize=9)
        ax.tick_params(axis="y", labelsize=10)
        for x_pos, row in enumerate(plot_df.itertuples(index=False)):
            if x_pos in {0, len(plot_df) - 1}:
                ax.annotate(
                    f"{row.retention_pct:.1f}%",
                    (x_pos, row.retention_pct),
                    textcoords="offset points",
                    xytext=(0, 8),
                    ha="center",
                    fontsize=10,
                    color="#2f4b7c",
                )
        paths.append(savefig(filename))
    return paths


def plot_model_progression() -> Path:
    rows = []

    short = load_csv("final_results_model_comparison")
    for _, row in short.iterrows():
        label = {
            "handcrafted": "Regresja logistyczna",
            "sequence": "CNN",
            "hybrid": "Hybryda",
        }.get(row["model_family"], row["model"])
        rows.append({"setup": "Kwalifikacje\n2023-2025", "model": label, "macro_f1": row["oof_macro_f1"]})

    long_seq = load_csv("long_horizon_sequence_model_summary")
    long_base = load_csv("long_horizon_baseline_model_summary")
    long_log = long_base[
        (long_base["subset_name"] == "balanced_top5")
        & (long_base["experiment"] == "with_time_features")
        & (long_base["model"] == "logistic_regression")
    ]["oof_macro_f1"].iloc[0]
    rows.append({"setup": "Kwalifikacje\n2018-2025", "model": "Regresja logistyczna", "macro_f1": long_log})
    for model in ["cnn", "hybrid_cnn_tabular", "gru", "lstm"]:
        val = long_seq[(long_seq["subset_name"] == "balanced_top5") & (long_seq["model"] == model)]["oof_macro_f1"].iloc[0]
        rows.append({"setup": "Kwalifikacje\n2018-2025", "model": model_label(model), "macro_f1": val})

    race_seq = load_csv("race_2025_sequence_model_summary")
    race_base = load_csv("race_2025_baseline_model_summary")
    race_log = race_base[
        (race_base["experiment"] == "style_core_no_time_no_race_context")
        & (race_base["model"] == "logistic_regression")
    ]["oof_macro_f1"].iloc[0]
    rows.append({"setup": "Wyścigi\n2025", "model": "Regresja logistyczna", "macro_f1": race_log})
    for model in ["cnn", "hybrid_cnn_tabular", "gru", "lstm"]:
        val = race_seq[race_seq["model"] == model]["oof_macro_f1"].iloc[0]
        rows.append({"setup": "Wyścigi\n2025", "model": model_label(model), "macro_f1": val})

    plot_df = pd.DataFrame(rows)
    order = ["Regresja logistyczna", "CNN", "Hybryda", "GRU", "LSTM"]
    plt.figure(figsize=(13, 6))
    ax = sns.barplot(
        data=plot_df,
        x="setup",
        y="macro_f1",
        hue="model",
        hue_order=order,
        palette=["#4c78a8", "#59a14f", "#f28e2b", "#b07aa1", "#e15759"],
    )
    ax.set_title("Porównanie modeli w trzech setupach")
    ax.set_xlabel("")
    ax.set_ylabel("Macro F1")
    ax.set_ylim(0, 1)
    ax.legend(title="", ncols=5, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    return savefig("02_model_progression.png")


def plot_training_curve_short_horizon() -> Path:
    history = load_csv("sequence_cnn_training_history")
    plot_df = (
        history.groupby("epoch", as_index=False)
        .agg(
            train_accuracy=("accuracy", "mean"),
            val_accuracy=("val_accuracy", "mean"),
            train_loss=("loss", "mean"),
            val_loss=("val_loss", "mean"),
        )
    )

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    sns.lineplot(data=plot_df, x="epoch", y="train_accuracy", ax=axes[0], label="trening")
    sns.lineplot(data=plot_df, x="epoch", y="val_accuracy", ax=axes[0], label="walidacja")
    axes[0].set_title("CNN 2023-2025: dokładność")
    axes[0].set_xlabel("Epoka")
    axes[0].set_ylabel("Dokładność")
    axes[0].set_ylim(0, 1)

    sns.lineplot(data=plot_df, x="epoch", y="train_loss", ax=axes[1], label="trening")
    sns.lineplot(data=plot_df, x="epoch", y="val_loss", ax=axes[1], label="walidacja")
    axes[1].set_title("CNN 2023-2025: strata")
    axes[1].set_xlabel("Epoka")
    axes[1].set_ylabel("Strata")
    return savefig("03_cnn_training_curve_short_horizon.png")


def plot_epochs_trained() -> Path:
    rows = []
    for setup, filename in [
        ("Kwalifikacje\n2018-2025", "long_qualifying_top5_sequence_full_rerun_fold_metrics"),
        ("Wyścigi\n2025", "race_2025_top5_sequence_full_rerun_fold_metrics"),
    ]:
        df = load_csv(filename)
        for _, row in df.iterrows():
            rows.append(
                {
                    "setup": setup,
                    "model": model_label(row["model"]),
                    "fold": row["fold"],
                    "epochs_trained": row["epochs_trained"],
                }
            )

    plot_df = pd.DataFrame(rows)
    plt.figure(figsize=(12, 5.5))
    ax = sns.boxplot(data=plot_df, x="model", y="epochs_trained", hue="setup", palette=["#4c78a8", "#f28e2b"])
    sns.stripplot(data=plot_df, x="model", y="epochs_trained", hue="setup", dodge=True, color="black", alpha=0.45, ax=ax)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[:2], labels[:2], title="")
    ax.set_title("Liczba epok do early stopping")
    ax.set_xlabel("")
    ax.set_ylabel("Epoki")
    return savefig("04_epochs_to_early_stopping.png")


def plot_confusion_matrix() -> Path:
    cm = load_csv("final_model_confusion_matrix")
    matrix = cm.pivot(index="true_driver", columns="pred_driver", values="row_normalized").fillna(0)
    plt.figure(figsize=(7.5, 6))
    ax = sns.heatmap(matrix, annot=True, fmt=".2f", cmap="Blues", vmin=0, vmax=1, square=True)
    ax.set_title("Macierz pomyłek: finalny model interpretowalny")
    ax.set_xlabel("Predykcja")
    ax.set_ylabel("Rzeczywisty kierowca")
    return savefig("05_final_model_confusion_matrix.png")


def plot_feature_importance() -> Path:
    imp = load_csv("final_model_feature_importance_global").head(15).copy()
    imp["feature"] = imp["feature"].str.replace("num__", "", regex=False)
    plt.figure(figsize=(10, 7))
    ax = sns.barplot(data=imp, y="feature", x="mean_abs_coef", color="#4c78a8")
    ax.set_title("Najważniejsze cechy w modelu interpretowalnym")
    ax.set_xlabel("Średnia bezwzględna wartość współczynnika")
    ax.set_ylabel("")
    return savefig("06_driver_feature_importance.png")


def plot_team_bias() -> Path:
    team = load_csv("team_bias_team_classification_summary")
    team_best = (
        team.sort_values(["dataset", "oof_macro_f1"], ascending=[True, False])
        .groupby("dataset", as_index=False)
        .head(1)
    )
    direct = load_csv("hierarchical_team_driver_best_models")
    driver_best = direct[direct["result_name"] == "direct_driver"].copy()

    plot_rows = []
    for _, row in team_best.iterrows():
        plot_rows.append({"dataset": pretty_dataset(row["dataset"]), "task": "Predykcja zespołu", "macro_f1": row["oof_macro_f1"]})
    for _, row in driver_best.iterrows():
        plot_rows.append({"dataset": pretty_dataset(row["dataset"]), "task": "Predykcja kierowcy", "macro_f1": row["macro_f1"]})

    plot_df = pd.DataFrame(plot_rows)
    plt.figure(figsize=(12, 5.8))
    ax = sns.barplot(data=plot_df, x="dataset", y="macro_f1", hue="task", palette=["#f28e2b", "#4c78a8"])
    ax.set_title("Predykcja kierowcy a predykcja zespołu")
    ax.set_xlabel("")
    ax.set_ylabel("Macro F1")
    ax.set_ylim(0, 1)
    ax.legend(title="")
    return savefig("07_driver_vs_team_prediction.png")


def plot_hierarchical_team_aware() -> Path:
    hier = load_csv("hierarchical_team_driver_best_models")
    aware = load_csv("team_aware_driver_model_comparison")
    rows = []
    for _, row in hier[hier["result_name"] == "direct_driver"].iterrows():
        rows.append({"dataset": pretty_dataset(row["dataset"]), "method": "Bezpośrednio: kierowca", "macro_f1": row["macro_f1"]})
    for _, row in hier[hier["result_name"] == "hierarchical_driver_final"].iterrows():
        rows.append({"dataset": pretty_dataset(row["dataset"]), "method": "Najpierw zespół, potem kierowca", "macro_f1": row["macro_f1"]})
    for _, row in aware[aware["model_family"] == "team_aware_tabular"].iterrows():
        rows.append({"dataset": pretty_dataset(row["dataset"]), "method": "Zespół jako cecha pomocnicza", "macro_f1": row["macro_f1"]})

    plot_df = pd.DataFrame(rows)
    plt.figure(figsize=(12, 5.8))
    ax = sns.barplot(data=plot_df, x="dataset", y="macro_f1", hue="method", palette=["#4c78a8", "#e15759", "#59a14f"])
    ax.set_title("Strategie wykorzystania informacji o zespole")
    ax.set_xlabel("")
    ax.set_ylabel("Macro F1")
    ax.set_ylim(0, 1)
    ax.legend(title="", fontsize=11)
    return savefig("08_hierarchical_team_aware_comparison.png")


def plot_same_team_importance() -> Path:
    imp = load_csv("team_bias_same_team_driver_feature_importance")
    sel = imp[
        (imp["task"] == "same_team_ferrari_ham_vs_lec_2025_race")
        & (imp["feature_config"] == "style_core_no_time_context")
        & (imp["class_name"].isin(["HAM", "LEC"]))
        & (imp["rank"] <= 10)
    ].copy()
    sel["feature"] = sel["feature"].str.replace("num__", "", regex=False)
    plt.figure(figsize=(12, 7))
    ax = sns.barplot(data=sel, y="feature", x="coef", hue="class_name", palette=["#4c78a8", "#e15759"])
    ax.axvline(0, color="black", linewidth=1)
    ax.set_title("Ferrari 2025: cechy rozróżniające HAM i LEC")
    ax.set_xlabel("Współczynnik modelu")
    ax.set_ylabel("")
    ax.legend(title="")
    return savefig("09_same_team_ham_lec_feature_importance.png")


def append_mean_history(rows: list[dict], setup: str, filename: str, model: str) -> None:
    history = load_csv(filename)
    if "model" in history.columns:
        history = history[history["model"] == model].copy()
    grouped = (
        history.groupby("epoch", as_index=False)
        .agg(
            train_accuracy=("accuracy", "mean"),
            val_accuracy=("val_accuracy", "mean"),
            train_loss=("loss", "mean"),
            val_loss=("val_loss", "mean"),
        )
    )
    for _, row in grouped.iterrows():
        rows.append({"setup": setup, "model": model_label(model), **row.to_dict()})


def plot_training_curves_multisetup() -> Path:
    rows = []
    append_mean_history(rows, "Kwalifikacje 2023-2025\nHybryda", "sequence_architecture_training_history", "hybrid_cnn_tabular")
    append_mean_history(rows, "Kwalifikacje 2018-2025\nHybryda", "long_qualifying_top5_sequence_full_rerun_training_history", "hybrid_cnn_tabular")
    append_mean_history(rows, "Wyścigi 2025\nHybryda", "race_2025_top5_sequence_full_rerun_training_history", "hybrid_cnn_tabular")
    plot_df = pd.DataFrame(rows)

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    sns.lineplot(data=plot_df, x="epoch", y="val_accuracy", hue="setup", ax=axes[0], linewidth=2)
    axes[0].set_title("Walidacja: dokładność")
    axes[0].set_xlabel("Epoka")
    axes[0].set_ylabel("Dokładność walidacyjna")
    axes[0].set_ylim(0, 1)
    axes[0].legend(title="", fontsize=10)

    sns.lineplot(data=plot_df, x="epoch", y="val_loss", hue="setup", ax=axes[1], linewidth=2)
    axes[1].set_title("Walidacja: strata")
    axes[1].set_xlabel("Epoka")
    axes[1].set_ylabel("Strata walidacyjna")
    axes[1].legend(title="", fontsize=10)
    return savefig("10_training_curves_multisetup_hybrid.png")


def plot_sequence_fold_variability() -> Path:
    frames = []
    short = load_csv("sequence_architecture_fold_metrics")
    short["setup"] = "Kwalifikacje\n2023-2025"
    frames.append(short[["setup", "model", "fold", "test_macro_f1"]])

    long_df = load_csv("long_qualifying_top5_sequence_full_rerun_fold_metrics")
    long_df["setup"] = "Kwalifikacje\n2018-2025"
    frames.append(long_df[["setup", "model", "fold", "test_macro_f1"]])

    race_df = load_csv("race_2025_top5_sequence_full_rerun_fold_metrics")
    race_df["setup"] = "Wyścigi\n2025"
    frames.append(race_df[["setup", "model", "fold", "test_macro_f1"]])

    plot_df = pd.concat(frames, ignore_index=True)
    plot_df["model"] = plot_df["model"].map(model_label)

    plt.figure(figsize=(13, 6))
    ax = sns.boxplot(data=plot_df, x="model", y="test_macro_f1", hue="setup", palette=["#4c78a8", "#59a14f", "#f28e2b"])
    sns.stripplot(data=plot_df, x="model", y="test_macro_f1", hue="setup", dodge=True, color="black", alpha=0.35, ax=ax)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[:3], labels[:3], title="")
    ax.set_title("Zmienność wyniku między foldami")
    ax.set_xlabel("")
    ax.set_ylabel("Macro F1 na foldzie testowym")
    ax.set_ylim(0, 1)
    return savefig("11_sequence_fold_variability.png")


def normalized_matrix(cm: pd.DataFrame, model: str) -> pd.DataFrame:
    if "model" in cm.columns:
        cm = cm[cm["model"] == model].copy()
    matrix = cm.pivot(index="true_driver", columns="pred_driver", values="count").fillna(0)
    return matrix.div(matrix.sum(axis=1).replace(0, 1), axis=0)


def plot_best_sequence_confusion_matrices() -> Path:
    items = [
        ("Kwalifikacje 2023-2025\nHybryda", load_csv("sequence_architecture_confusion_matrix"), "hybrid_cnn_tabular"),
        ("Kwalifikacje 2018-2025\nHybryda", load_csv("long_qualifying_top5_sequence_full_rerun_confusion_matrix"), "hybrid_cnn_tabular"),
        ("Wyścigi 2025\nHybryda", load_csv("race_2025_top5_sequence_full_rerun_confusion_matrix"), "hybrid_cnn_tabular"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.2))
    for ax, (title, cm, model) in zip(axes, items):
        matrix = normalized_matrix(cm, model)
        sns.heatmap(matrix, annot=True, fmt=".2f", cmap="Blues", vmin=0, vmax=1, square=True, cbar=ax is axes[-1], ax=ax)
        ax.set_title(title)
        ax.set_xlabel("Predykcja")
        ax.set_ylabel("Rzeczywisty")
    return savefig("12_best_sequence_confusion_matrices.png")


def main() -> None:
    paths = []
    paths.extend(plot_filter_funnels())
    paths.extend([
        plot_model_progression(),
        plot_training_curve_short_horizon(),
        plot_epochs_trained(),
        plot_confusion_matrix(),
        plot_feature_importance(),
        plot_team_bias(),
        plot_hierarchical_team_aware(),
        plot_same_team_importance(),
        plot_training_curves_multisetup(),
        plot_sequence_fold_variability(),
        plot_best_sequence_confusion_matrices(),
    ])
    print("Thesis figure pack created:")
    for path in paths:
        print(f"- {path}")


if __name__ == "__main__":
    main()
