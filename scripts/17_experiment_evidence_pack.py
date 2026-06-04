from __future__ import annotations

from pathlib import Path
import math

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score


EXPORT_DIR = Path("exports")
RANDOM_STATE = 42
N_BOOTSTRAP = 10000


def export_csv(df: pd.DataFrame, name: str) -> Path:
    path = EXPORT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    print(f"Saved {path}")
    return path


def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(EXPORT_DIR / f"{name}.csv")


def bootstrap_mean_ci(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    if len(values) == 0:
        return np.nan, np.nan
    draws = rng.choice(values, size=(N_BOOTSTRAP, len(values)), replace=True).mean(axis=1)
    return float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def collect_fold_metric_frames() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    if (EXPORT_DIR / "final_model_fold_metrics.csv").exists():
        df = load_csv("final_model_fold_metrics")
        df = df.assign(
            setup="short_qualifying_2023_2025_top5",
            setup_label="Kwalifikacje 2023-2025",
            model="logistic_regression_final",
            model_label="Regresja logistyczna",
            result_source="final_model_fold_metrics.csv",
        )
        frames.append(df)

    sequence_sources = [
        (
            "sequence_architecture_fold_metrics",
            "sequence_architecture_split_summary",
            "short_qualifying_2023_2025_top5",
            "Kwalifikacje 2023-2025",
        ),
        (
            "long_qualifying_top5_sequence_full_rerun_fold_metrics",
            "long_qualifying_top5_sequence_full_rerun_split_summary",
            "long_qualifying_2018_2025_top5",
            "Kwalifikacje 2018-2025",
        ),
        (
            "race_2025_top5_sequence_full_rerun_fold_metrics",
            "race_2025_top5_sequence_full_rerun_split_summary",
            "race_2025_clean_laps_top5",
            "Wyścigi 2025",
        ),
    ]
    for name, split_name, setup, label in sequence_sources:
        path = EXPORT_DIR / f"{name}.csv"
        if not path.exists():
            continue
        df = load_csv(name)
        split_path = EXPORT_DIR / f"{split_name}.csv"
        if split_path.exists() and not {"n_train", "n_train_inner", "n_val", "n_test"}.issubset(df.columns):
            split_df = load_csv(split_name)
            split_cols = [c for c in ["fold", "n_train", "n_train_inner", "n_val", "n_test"] if c in split_df.columns]
            df = df.merge(split_df[split_cols], on="fold", how="left", suffixes=("", "_split"))
        df = df.assign(
            setup=setup,
            setup_label=label,
            model_label=df["model"].map(model_label).fillna(df["model"]),
            result_source=f"{name}.csv",
        )
        frames.append(df)

    tabular_sources = [
        (
            "long_horizon_baseline_fold_metrics",
            "long_qualifying_2018_2025_top5",
            "Kwalifikacje 2018-2025",
            {"subset_name": "balanced_top5", "experiment": "with_time_features"},
        ),
        (
            "race_2025_baseline_fold_metrics",
            "race_2025_clean_laps_top5",
            "Wyścigi 2025",
            {"experiment": "style_core_no_time_no_race_context"},
        ),
    ]
    for name, setup, label, filters in tabular_sources:
        path = EXPORT_DIR / f"{name}.csv"
        if not path.exists():
            continue
        df = load_csv(name)
        for col, value in filters.items():
            df = df[df[col] == value].copy()
        df = df.assign(
            setup=setup,
            setup_label=label,
            model_label=df["model"].map(model_label).fillna(df["model"]),
            result_source=f"{name}.csv",
        )
        frames.append(df)

    cols = [
        "setup",
        "setup_label",
        "model",
        "model_label",
        "fold",
        "n_train",
        "n_train_inner",
        "n_val",
        "n_test",
        "epochs_trained",
        "train_accuracy",
        "test_accuracy",
        "train_balanced_accuracy",
        "test_balanced_accuracy",
        "train_macro_f1",
        "test_macro_f1",
        "result_source",
    ]
    out = pd.concat(frames, ignore_index=True, sort=False)
    for col in cols:
        if col not in out.columns:
            out[col] = np.nan
    return out[cols]


def model_label(model: str) -> str:
    mapping = {
        "logistic_regression": "Regresja logistyczna",
        "logistic_regression_final": "Regresja logistyczna",
        "cnn": "CNN",
        "hybrid_cnn_tabular": "Hybryda CNN + tabular",
        "gru": "GRU",
        "lstm": "LSTM",
        "random_forest": "Random Forest",
        "hist_gradient_boosting": "HistGradientBoosting",
    }
    return mapping.get(str(model), str(model))


def add_oof_scores(summary: pd.DataFrame) -> pd.DataFrame:
    oof_rows: list[dict] = []

    final_oof_path = EXPORT_DIR / "final_model_oof_predictions.csv"
    if final_oof_path.exists():
        final_oof = pd.read_csv(final_oof_path)
        oof_rows.append(
            {
                "result_source": "final_model_fold_metrics.csv",
                "model": "logistic_regression_final",
                "oof_macro_f1": f1_score(final_oof["true_driver"], final_oof["pred_driver"], average="macro"),
                "oof_accuracy": accuracy_score(final_oof["true_driver"], final_oof["pred_driver"]),
                "oof_balanced_accuracy": balanced_accuracy_score(final_oof["true_driver"], final_oof["pred_driver"]),
            }
        )

    sources = [
        ("sequence_architecture_fold_metrics.csv", "sequence_architecture_summary", None),
        (
            "long_qualifying_top5_sequence_full_rerun_fold_metrics.csv",
            "long_qualifying_top5_sequence_full_rerun_model_summary",
            None,
        ),
        (
            "race_2025_top5_sequence_full_rerun_fold_metrics.csv",
            "race_2025_top5_sequence_full_rerun_model_summary",
            None,
        ),
        ("long_horizon_baseline_fold_metrics.csv", "long_horizon_baseline_best_models", None),
        ("race_2025_baseline_fold_metrics.csv", "race_2025_baseline_best_models", None),
    ]

    for source_file, summary_name, forced_model in sources:
        path = EXPORT_DIR / f"{summary_name}.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        for _, row in df.iterrows():
            model = forced_model or row.get("model")
            if pd.isna(model):
                model = row.get("model_name")
            oof_rows.append(
                {
                    "result_source": source_file,
                    "model": model,
                    "subset_name": row.get("subset_name"),
                    "experiment": row.get("experiment"),
                    "oof_macro_f1": row.get("oof_macro_f1", row.get("macro_f1")),
                    "oof_accuracy": row.get("oof_accuracy", row.get("accuracy")),
                    "oof_balanced_accuracy": row.get("oof_balanced_accuracy", row.get("balanced_accuracy")),
                }
            )

    oof = pd.DataFrame(oof_rows)
    if oof.empty:
        summary["oof_macro_f1"] = np.nan
        return summary

    # Keep one row per source/model. Fold-level rows already encode setup and filters.
    oof = oof.drop_duplicates(subset=["result_source", "model"], keep="first")
    return summary.merge(oof[["result_source", "model", "oof_macro_f1", "oof_accuracy", "oof_balanced_accuracy"]], on=["result_source", "model"], how="left")


def summarize_fold_uncertainty(folds: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_STATE)
    rows: list[dict] = []
    group_cols = ["setup", "setup_label", "model", "model_label", "result_source"]
    for keys, group in folds.groupby(group_cols, dropna=False):
        values = group["test_macro_f1"].dropna().to_numpy(dtype=float)
        train_values = group["train_macro_f1"].dropna().to_numpy(dtype=float)
        if len(values) == 0:
            continue
        ci_low, ci_high = bootstrap_mean_ci(values, rng)
        row = dict(zip(group_cols, keys))
        row.update(
            {
                "n_folds": int(len(values)),
                "test_macro_f1_mean": float(values.mean()),
                "test_macro_f1_std": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
                "test_macro_f1_min": float(values.min()),
                "test_macro_f1_max": float(values.max()),
                "test_macro_f1_bootstrap_ci95_low": ci_low,
                "test_macro_f1_bootstrap_ci95_high": ci_high,
                "train_macro_f1_mean": float(train_values.mean()) if len(train_values) else np.nan,
                "train_macro_f1_std": float(train_values.std(ddof=1)) if len(train_values) > 1 else np.nan,
                "macro_f1_gap_mean": float(train_values.mean() - values.mean()) if len(train_values) else np.nan,
                "n_train_mean": float(group["n_train"].dropna().mean()) if group["n_train"].notna().any() else np.nan,
                "n_val_mean": float(group["n_val"].dropna().mean()) if group["n_val"].notna().any() else np.nan,
                "n_test_mean": float(group["n_test"].dropna().mean()) if group["n_test"].notna().any() else np.nan,
                "epochs_trained_mean": float(group["epochs_trained"].dropna().mean()) if group["epochs_trained"].notna().any() else np.nan,
                "epochs_trained_std": float(group["epochs_trained"].dropna().std(ddof=1)) if group["epochs_trained"].notna().sum() > 1 else np.nan,
            }
        )
        rows.append(row)
    return add_oof_scores(pd.DataFrame(rows))


def paired_fold_comparisons(folds: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    comparisons = {
        "short_qualifying_2023_2025_top5": [
            ("hybrid_cnn_tabular", "cnn"),
            ("hybrid_cnn_tabular", "logistic_regression_final"),
            ("cnn", "logistic_regression_final"),
        ],
        "long_qualifying_2018_2025_top5": [
            ("hybrid_cnn_tabular", "cnn"),
            ("hybrid_cnn_tabular", "logistic_regression"),
            ("cnn", "logistic_regression"),
        ],
        "race_2025_clean_laps_top5": [
            ("hybrid_cnn_tabular", "cnn"),
            ("hybrid_cnn_tabular", "logistic_regression"),
            ("cnn", "logistic_regression"),
        ],
    }
    for setup, pairs in comparisons.items():
        setup_df = folds[folds["setup"] == setup]
        for model_a, model_b in pairs:
            a = setup_df[setup_df["model"] == model_a][["fold", "test_macro_f1"]].rename(columns={"test_macro_f1": "a"})
            b = setup_df[setup_df["model"] == model_b][["fold", "test_macro_f1"]].rename(columns={"test_macro_f1": "b"})
            merged = a.merge(b, on="fold")
            if merged.empty:
                continue
            diff = (merged["a"] - merged["b"]).to_numpy(dtype=float)
            nonzero = diff[diff != 0]
            n_nonzero = len(nonzero)
            n_positive = int((nonzero > 0).sum())
            n_negative = int((nonzero < 0).sum())
            if n_nonzero:
                # Exact two-sided sign test with p=0.5; conservative but dependency-light.
                k = min(n_positive, n_negative)
                tail = sum(math.comb(n_nonzero, i) for i in range(k + 1)) / (2 ** n_nonzero)
                sign_test_p_value = min(1.0, 2 * tail)
            else:
                sign_test_p_value = 1.0
            rows.append(
                {
                    "setup": setup,
                    "setup_label": setup_df["setup_label"].dropna().iloc[0] if setup_df["setup_label"].notna().any() else setup,
                    "model_a": model_a,
                    "model_a_label": model_label(model_a),
                    "model_b": model_b,
                    "model_b_label": model_label(model_b),
                    "n_paired_folds": int(len(diff)),
                    "macro_f1_diff_mean": float(diff.mean()),
                    "macro_f1_diff_std": float(diff.std(ddof=1)) if len(diff) > 1 else 0.0,
                    "macro_f1_diff_min": float(diff.min()),
                    "macro_f1_diff_max": float(diff.max()),
                    "n_positive_folds": n_positive,
                    "n_negative_folds": n_negative,
                    "sign_test_p_value": sign_test_p_value,
                    "fold_diffs": ";".join(f"{x:.6f}" for x in diff),
                }
            )
    return pd.DataFrame(rows)


def protocol_summary() -> pd.DataFrame:
    rows = [
        {
            "area": "outer_validation",
            "parameter": "splitter",
            "value": "StratifiedGroupKFold",
            "notes": "Główna walidacja grupowana; grupa odpowiada sesji, aby okrążenia z tej samej sesji nie trafiały równocześnie do train i test.",
        },
        {
            "area": "outer_validation",
            "parameter": "n_splits",
            "value": "5",
            "notes": "Odpowiada mniej więcej podziałowi 80/20 w każdym foldzie, ale dokładne proporcje zależą od liczby okrążeń w grupach.",
        },
        {
            "area": "outer_validation",
            "parameter": "shuffle/random_state",
            "value": "shuffle=True, random_state=42",
            "notes": "Stały seed zapewnia powtarzalność podziałów.",
        },
        {
            "area": "tabular_preprocessing",
            "parameter": "numeric preprocessing",
            "value": "SimpleImputer(strategy='median') + StandardScaler()",
            "notes": "W modelach sklearn preprocessing znajduje się w Pipeline i jest fitowany wyłącznie na części treningowej danego folda.",
        },
        {
            "area": "tabular_preprocessing",
            "parameter": "categorical preprocessing",
            "value": "SimpleImputer(strategy='most_frequent') + OneHotEncoder(handle_unknown='ignore')",
            "notes": "Stosowane tylko w konfiguracjach zawierających zmienne kategoryczne.",
        },
        {
            "area": "sequence_preprocessing",
            "parameter": "sequence length/channels",
            "value": "300 samples; Speed, Throttle, Brake, RPM, nGear",
            "notes": "Każde okrążenie resamplowano liniowo do wspólnej długości.",
        },
        {
            "area": "sequence_preprocessing",
            "parameter": "scaling",
            "value": "mean/std from inner-training data",
            "notes": "Sekwencje i cechy tabularne w modelu hybrydowym standaryzowano parametrami wyliczonymi na części treningowej bez folda walidacyjnego i testowego.",
        },
        {
            "area": "sequence_training",
            "parameter": "inner validation",
            "value": "StratifiedGroupKFold(n_splits=5), first split inside outer train",
            "notes": "Inner validation służy do early stoppingu; test fold pozostaje niewidziany podczas treningu.",
        },
        {
            "area": "sequence_training",
            "parameter": "optimizer/loss/batch",
            "value": "Adam(lr=0.001), sparse_categorical_crossentropy, batch_size=32",
            "notes": "Wspólna konfiguracja dla CNN, hybrydy, GRU i LSTM.",
        },
        {
            "area": "sequence_training",
            "parameter": "early stopping",
            "value": "monitor='val_loss', restore_best_weights=True",
            "notes": "Maksymalna liczba epok i patience zależą od setupu; szczegóły w sequence_training_parameters.",
        },
    ]
    return pd.DataFrame(rows)


def sequence_architecture_spec() -> pd.DataFrame:
    rows = [
        {
            "model": "cnn",
            "input": "sequence: 300 x 5",
            "layers": "Conv1D(32,k=7)-Conv1D(32,k=7)-MaxPool(2)-Dropout(0.2)-Conv1D(64,k=5)-Conv1D(64,k=5)-GlobalAveragePooling-Dense(64)-Dropout(0.3)-Dense(n_classes,softmax)",
        },
        {
            "model": "hybrid_cnn_tabular",
            "input": "sequence: 300 x 5; tabular features",
            "layers": "sequence branch: Conv1D(32,k=7)-Conv1D(32,k=7)-MaxPool(2)-Dropout(0.2)-Conv1D(64,k=5)-GlobalAveragePooling; tabular branch: Dense(32)-Dropout(0.2); merge: Concatenate-Dense(64)-Dropout(0.3)-Dense(n_classes,softmax)",
        },
        {
            "model": "gru",
            "input": "sequence: 300 x 5",
            "layers": "GRU(64,return_sequences=True,dropout=0.2)-GRU(32,dropout=0.2)-Dense(64)-Dropout(0.3)-Dense(n_classes,softmax)",
        },
        {
            "model": "lstm",
            "input": "sequence: 300 x 5",
            "layers": "LSTM(64,return_sequences=True,dropout=0.2)-LSTM(32,dropout=0.2)-Dense(64)-Dropout(0.3)-Dense(n_classes,softmax)",
        },
    ]
    return pd.DataFrame(rows)


def sequence_training_parameters() -> pd.DataFrame:
    rows = [
        {
            "setup": "short_qualifying_2023_2025_top5",
            "setup_label": "Kwalifikacje 2023-2025",
            "max_epochs": 150,
            "patience": 20,
            "notes": "Wartości z 02_short_horizon_qualifying_modeling.ipynb; batch_size w tym pierwotnym treningu wynosił 16.",
        },
        {
            "setup": "long_qualifying_2018_2025_top5",
            "setup_label": "Kwalifikacje 2018-2025",
            "max_epochs": 80,
            "patience": 10,
            "notes": "Wartości z scripts/10_sequence_full_history_rerun.py.",
        },
        {
            "setup": "race_2025_clean_laps_top5",
            "setup_label": "Wyścigi 2025",
            "max_epochs": 60,
            "patience": 8,
            "notes": "Wartości z scripts/10_sequence_full_history_rerun.py.",
        },
    ]
    return pd.DataFrame(rows)


def main() -> None:
    folds = collect_fold_metric_frames()
    uncertainty = summarize_fold_uncertainty(folds)
    paired = paired_fold_comparisons(folds)

    export_csv(protocol_summary(), "thesis_experiment_protocol_summary")
    export_csv(sequence_architecture_spec(), "thesis_sequence_architecture_spec")
    export_csv(sequence_training_parameters(), "thesis_sequence_training_parameters")
    export_csv(folds, "thesis_fold_metric_inventory")
    export_csv(uncertainty, "thesis_model_uncertainty_summary")
    export_csv(paired, "thesis_paired_fold_comparisons")

    print("\nUncertainty summary:")
    print(
        uncertainty[
            [
                "setup_label",
                "model_label",
                "n_folds",
                "test_macro_f1_mean",
                "test_macro_f1_std",
                "test_macro_f1_bootstrap_ci95_low",
                "test_macro_f1_bootstrap_ci95_high",
                "oof_macro_f1",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
