from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler


EXPORT_DIR = Path("exports")
RANDOM_STATE = 42
N_SPLITS = 5


DATASETS = {
    "short_qualifying_2023_2025_top5": {
        "path": EXPORT_DIR / "lap_features_model_min_40_laps.csv",
        "drivers": ["ALB", "SAI", "VER", "OCO", "LEC"],
        "sequence_summary": EXPORT_DIR / "sequence_architecture_summary.csv",
        "sequence_filter": {"model": ["hybrid_cnn_tabular", "cnn"]},
    },
    "long_qualifying_2018_2025_top5": {
        "path": EXPORT_DIR / "balanced_top5_lap_features_2018_2025_strict.csv",
        "drivers": ["SAI", "VER", "LEC", "OCO", "HAM"],
        "sequence_summary": EXPORT_DIR / "long_horizon_sequence_model_summary.csv",
        "sequence_filter": {"subset_name": ["balanced_top5"], "model": ["hybrid_cnn_tabular", "cnn"]},
    },
    "race_2025_clean_laps_top5": {
        "path": EXPORT_DIR / "race_2025_balanced_top5_lap_features.csv",
        "drivers": ["SAI", "VER", "LEC", "OCO", "HAM"],
        "sequence_summary": EXPORT_DIR / "race_2025_sequence_model_summary.csv",
        "sequence_filter": {"model": ["hybrid_cnn_tabular", "cnn"]},
    },
}


def export_csv(df: pd.DataFrame, name: str) -> Path:
    path = EXPORT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    return path


def session_column(df: pd.DataFrame) -> str:
    if "session_key" in df.columns:
        return "session_key"
    return "round"


def style_feature_cols(df: pd.DataFrame) -> list[str]:
    excluded = {
        "lap_key",
        "Driver",
        "Team",
        "season",
        "round",
        "LapNumber",
        "event_name",
        "EventName",
        "session_name",
        "session_key",
        "TrackStatus",
        "lap_time_not_null",
        "dry_session",
        "accurate",
        "not_deleted",
        "not_fastf1_generated",
        "track_status_green",
        "not_pit_in_out",
        "within_2s_of_stint_median",
        "within_3s_of_stint_median",
        "LapTimeSeconds",
        "Sector1TimeSeconds",
        "Sector2TimeSeconds",
        "Sector3TimeSeconds",
        "sector_sum_seconds",
        "sector1_share",
        "sector2_share",
        "sector3_share",
        "stint_median_lap_seconds",
        "lap_time_delta_to_stint_median",
        "Compound",
        "TyreLife",
        "Stint",
        "SessionPart",
        "throttle_min",
        "brake_min",
        "brake_median",
        "brake_hard_frac",
        "drs_toggle_count",
        "brake_diff_mean",
        "drs_active_frac",
    }
    all_missing = {c for c in df.columns if df[c].isna().all()}
    return [c for c in df.columns if c not in excluded and c not in all_missing]


def build_logreg(feature_cols: list[str]) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                feature_cols,
            )
        ],
        remainder="drop",
    )
    model = LogisticRegression(
        penalty="l2",
        C=1.0,
        solver="lbfgs",
        max_iter=2000,
        random_state=RANDOM_STATE,
    )
    return Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])


def oof_team_probabilities(df: pd.DataFrame, feature_cols: list[str], groups: np.ndarray) -> tuple[np.ndarray, list[str]]:
    team_encoder = LabelEncoder()
    y_team = team_encoder.fit_transform(df["Team"].astype(str))
    classes = list(team_encoder.classes_)
    n_splits = min(N_SPLITS, int(pd.Series(y_team).value_counts().min()))
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    probs = np.zeros((len(df), len(classes)), dtype=float)
    X = df[feature_cols].copy()

    for train_idx, test_idx in cv.split(X, y_team, groups):
        model = build_logreg(feature_cols)
        model.fit(X.iloc[train_idx], y_team[train_idx])
        fold_probs = model.predict_proba(X.iloc[test_idx])
        for local_idx, class_idx in enumerate(model.named_steps["model"].classes_):
            probs[test_idx, class_idx] = fold_probs[:, local_idx]
    return probs, classes


def evaluate_driver_model(
    df: pd.DataFrame,
    feature_cols: list[str],
    groups: np.ndarray,
    extra_features: np.ndarray | None = None,
) -> dict[str, float]:
    driver_encoder = LabelEncoder()
    y_driver = driver_encoder.fit_transform(df["Driver"].astype(str))
    n_splits = min(N_SPLITS, int(pd.Series(y_driver).value_counts().min()))
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    oof = np.full(len(df), -1, dtype=int)
    X_base = df[feature_cols].copy()

    if extra_features is not None:
        extra_cols = [f"team_prob_{i}" for i in range(extra_features.shape[1])]
        X_full = pd.concat(
            [X_base.reset_index(drop=True), pd.DataFrame(extra_features, columns=extra_cols)],
            axis=1,
        )
    else:
        X_full = X_base.reset_index(drop=True)

    full_cols = list(X_full.columns)
    for train_idx, test_idx in cv.split(X_full, y_driver, groups):
        model = build_logreg(full_cols)
        model.fit(X_full.iloc[train_idx], y_driver[train_idx])
        oof[test_idx] = model.predict(X_full.iloc[test_idx])

    return {
        "accuracy": accuracy_score(y_driver, oof),
        "balanced_accuracy": balanced_accuracy_score(y_driver, oof),
        "macro_f1": f1_score(y_driver, oof, average="macro"),
    }


def load_sequence_references(dataset_name: str, config: dict[str, object]) -> list[dict[str, object]]:
    path = config["sequence_summary"]
    if not path.exists():
        return []
    df = pd.read_csv(path)
    for col, allowed in config.get("sequence_filter", {}).items():
        if col in df.columns:
            df = df[df[col].isin(allowed)]
    rows = []
    for _, row in df.iterrows():
        rows.append(
            {
                "dataset": dataset_name,
                "model_family": "sequence_reference",
                "model_name": row["model"],
                "n_samples": int(row.get("n_samples", np.nan)),
                "accuracy": float(row["oof_accuracy"]),
                "balanced_accuracy": float(row["oof_balanced_accuracy"]),
                "macro_f1": float(row["oof_macro_f1"]),
                "notes": "existing sequence/hybrid result, not retrained in this script",
            }
        )
    return rows


def main() -> None:
    rows = []

    for dataset_name, config in DATASETS.items():
        df = pd.read_csv(config["path"])
        df = df[df["Driver"].isin(config["drivers"])].dropna(subset=["Driver", "Team"]).copy()
        feature_cols = style_feature_cols(df)
        groups = df[session_column(df)].astype(str).to_numpy()

        direct = evaluate_driver_model(df, feature_cols, groups)
        rows.append(
            {
                "dataset": dataset_name,
                "model_family": "tabular",
                "model_name": "direct_driver_logistic_l2",
                "n_samples": len(df),
                **direct,
                "notes": "style core features only",
            }
        )

        team_probs, team_classes = oof_team_probabilities(df, feature_cols, groups)
        team_aware = evaluate_driver_model(df, feature_cols, groups, extra_features=team_probs)
        rows.append(
            {
                "dataset": dataset_name,
                "model_family": "team_aware_tabular",
                "model_name": "driver_logistic_l2_plus_oof_team_probabilities",
                "n_samples": len(df),
                **team_aware,
                "notes": "style core features plus OOF team probability features: "
                + ", ".join(team_classes),
            }
        )

        rows.extend(load_sequence_references(dataset_name, config))

    summary = pd.DataFrame(rows)
    summary = summary.sort_values(["dataset", "macro_f1", "accuracy"], ascending=[True, False, False])
    best = summary.groupby("dataset", as_index=False).head(1).reset_index(drop=True)

    export_csv(summary, "team_aware_driver_model_comparison")
    export_csv(best, "team_aware_driver_model_best")

    print("Team-aware driver model comparison complete.")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
