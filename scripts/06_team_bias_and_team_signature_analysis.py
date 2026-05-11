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
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler


EXPORT_DIR = Path("exports")
RANDOM_STATE = 42
N_SPLITS = 5


DATASETS = {
    "short_qualifying_2023_2025": EXPORT_DIR / "lap_features_model_min_40_laps.csv",
    "long_qualifying_2018_2025_top5": EXPORT_DIR / "balanced_top5_lap_features_2018_2025_strict.csv",
    "race_2025_clean_laps_top5": EXPORT_DIR / "race_2025_balanced_top5_lap_features.csv",
}


def export_csv(df: pd.DataFrame, name: str) -> Path:
    path = EXPORT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    return path


def session_column(df: pd.DataFrame) -> str:
    if "session_key" in df.columns:
        return "session_key"
    return "round"


def feature_sets(df: pd.DataFrame) -> dict[str, list[str]]:
    identifiers = {
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
    }
    weak_or_constant = {
        "throttle_min",
        "brake_min",
        "brake_median",
        "brake_hard_frac",
        "drs_toggle_count",
        "brake_diff_mean",
    }
    time_features = {
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
    }
    race_context = {
        "Compound",
        "TyreLife",
        "Stint",
        "SessionPart",
    }
    drs_features = {
        "DRS",
        "drs_active_frac",
    }

    all_missing = {c for c in df.columns if df[c].isna().all()}

    def keep(excluded: set[str]) -> list[str]:
        cols = [c for c in df.columns if c not in excluded and c not in all_missing]
        return [c for c in cols if c in df.columns]

    return {
        "all_telemetry_features": keep(identifiers | weak_or_constant),
        "no_time_features": keep(identifiers | weak_or_constant | time_features),
        "style_core_no_time_context": keep(
            identifiers | weak_or_constant | time_features | race_context | drs_features
        ),
    }


def build_logreg(numeric_features: list[str], categorical_features: list[str]) -> Pipeline:
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
                numeric_features,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
        ]
    )
    model = LogisticRegression(
        penalty="l2",
        C=1.0,
        solver="lbfgs",
        max_iter=2000,
        random_state=RANDOM_STATE,
    )
    return Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])


def run_grouped_logreg(
    df: pd.DataFrame,
    dataset_name: str,
    task_name: str,
    target_col: str,
    feature_config: str,
    feature_cols: list[str],
) -> dict[str, object]:
    df = df.dropna(subset=[target_col]).copy()
    label_counts = df[target_col].value_counts()
    if len(label_counts) < 2:
        raise ValueError(f"{dataset_name}/{task_name}: less than two target classes")

    group_col = session_column(df)
    n_splits = min(N_SPLITS, int(label_counts.min()))
    if n_splits < 2:
        raise ValueError(f"{dataset_name}/{task_name}: not enough samples per class")

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df[target_col].astype(str))
    groups = df[group_col].astype(str).to_numpy()
    X = df[feature_cols].copy()

    categorical_features = [c for c in feature_cols if X[c].dtype == "object"]
    numeric_features = [c for c in feature_cols if c not in categorical_features]

    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    oof_pred = np.full(len(df), -1, dtype=int)
    train_scores = []
    test_scores = []

    for train_idx, test_idx in cv.split(X, y, groups):
        model = build_logreg(numeric_features, categorical_features)
        model.fit(X.iloc[train_idx], y[train_idx])
        train_pred = model.predict(X.iloc[train_idx])
        test_pred = model.predict(X.iloc[test_idx])
        oof_pred[test_idx] = test_pred
        train_scores.append(accuracy_score(y[train_idx], train_pred))
        test_scores.append(accuracy_score(y[test_idx], test_pred))

    return {
        "dataset": dataset_name,
        "task": task_name,
        "target": target_col,
        "feature_config": feature_config,
        "n_samples": len(df),
        "n_classes": len(label_counts),
        "n_groups": df[group_col].nunique(),
        "n_features": len(feature_cols),
        "min_class_count": int(label_counts.min()),
        "max_class_count": int(label_counts.max()),
        "oof_accuracy": accuracy_score(y, oof_pred),
        "oof_balanced_accuracy": balanced_accuracy_score(y, oof_pred),
        "oof_macro_f1": f1_score(y, oof_pred, average="macro"),
        "mean_train_accuracy": float(np.mean(train_scores)),
        "mean_test_accuracy": float(np.mean(test_scores)),
        "mean_accuracy_gap": float(np.mean(train_scores) - np.mean(test_scores)),
    }


def fit_logreg_feature_importance(
    df: pd.DataFrame,
    dataset_name: str,
    task_name: str,
    target_col: str,
    feature_config: str,
    feature_cols: list[str],
    top_n: int = 30,
) -> pd.DataFrame:
    df = df.dropna(subset=[target_col]).copy()
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df[target_col].astype(str))
    X = df[feature_cols].copy()

    categorical_features = [c for c in feature_cols if X[c].dtype == "object"]
    numeric_features = [c for c in feature_cols if c not in categorical_features]

    model = build_logreg(numeric_features, categorical_features)
    model.fit(X, y)

    feature_names = model.named_steps["preprocessor"].get_feature_names_out()
    coefs = model.named_steps["model"].coef_
    classes = label_encoder.classes_

    rows = []
    if len(classes) == 2 and coefs.shape[0] == 1:
        coef_matrix = np.vstack([-coefs[0], coefs[0]])
    else:
        coef_matrix = coefs

    for class_name, class_coefs in zip(classes, coef_matrix):
        order = np.argsort(np.abs(class_coefs))[::-1][:top_n]
        for rank, idx in enumerate(order, start=1):
            rows.append(
                {
                    "dataset": dataset_name,
                    "task": task_name,
                    "target": target_col,
                    "feature_config": feature_config,
                    "class_name": class_name,
                    "rank": rank,
                    "feature": feature_names[idx],
                    "coef": class_coefs[idx],
                    "abs_coef": abs(class_coefs[idx]),
                }
            )
    return pd.DataFrame(rows)


def load_datasets() -> dict[str, pd.DataFrame]:
    loaded = {}
    for name, path in DATASETS.items():
        if path.exists():
            loaded[name] = pd.read_csv(path)
    return loaded


def team_coverage_rows(datasets: dict[str, pd.DataFrame]) -> list[dict[str, object]]:
    rows = []
    for dataset_name, df in datasets.items():
        if "Driver" not in df.columns or "Team" not in df.columns:
            continue
        counts = (
            df.groupby(["Driver", "Team"], dropna=False)
            .size()
            .reset_index(name="n_laps")
            .sort_values(["Driver", "n_laps"], ascending=[True, False])
        )
        for row in counts.to_dict("records"):
            row["dataset"] = dataset_name
            rows.append(row)
    return rows


def team_classification(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for dataset_name, df in datasets.items():
        if "Team" not in df.columns:
            continue
        team_counts = df["Team"].value_counts()
        eligible_teams = team_counts[team_counts >= 30].index
        filtered = df[df["Team"].isin(eligible_teams)].copy()
        for feature_config, cols in feature_sets(filtered).items():
            rows.append(
                run_grouped_logreg(
                    filtered,
                    dataset_name,
                    "predict_team",
                    "Team",
                    feature_config,
                    cols,
                )
            )
    return pd.DataFrame(rows)


def team_feature_importance(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for dataset_name, df in datasets.items():
        if "Team" not in df.columns:
            continue
        team_counts = df["Team"].value_counts()
        eligible_teams = team_counts[team_counts >= 30].index
        filtered = df[df["Team"].isin(eligible_teams)].copy()
        for feature_config, cols in feature_sets(filtered).items():
            rows.append(
                fit_logreg_feature_importance(
                    filtered,
                    dataset_name,
                    "predict_team",
                    "Team",
                    feature_config,
                    cols,
                )
            )
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def same_team_driver_tests(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    tests = [
        {
            "dataset": "race_2025_clean_laps_top5",
            "team": "Ferrari",
            "drivers": ["HAM", "LEC"],
            "label": "same_team_ferrari_ham_vs_lec_2025_race",
        },
        {
            "dataset": "short_qualifying_2023_2025",
            "team": "Ferrari",
            "drivers": ["LEC", "SAI"],
            "label": "same_team_ferrari_lec_vs_sai_2023_2024_qual",
        },
        {
            "dataset": "long_qualifying_2018_2025_top5",
            "team": "Ferrari",
            "drivers": ["LEC", "SAI", "HAM"],
            "label": "same_team_ferrari_lec_sai_ham_long_qual",
        },
    ]
    rows = []
    for test in tests:
        df = datasets.get(test["dataset"])
        if df is None:
            continue
        filtered = df[
            (df["Team"] == test["team"]) & (df["Driver"].isin(test["drivers"]))
        ].copy()
        if filtered["Driver"].nunique() < 2:
            continue
        for feature_config, cols in feature_sets(filtered).items():
            rows.append(
                run_grouped_logreg(
                    filtered,
                    test["dataset"],
                    test["label"],
                    "Driver",
                    feature_config,
                    cols,
                )
            )
    return pd.DataFrame(rows)


def same_team_feature_importance(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    tests = [
        {
            "dataset": "race_2025_clean_laps_top5",
            "team": "Ferrari",
            "drivers": ["HAM", "LEC"],
            "label": "same_team_ferrari_ham_vs_lec_2025_race",
        },
        {
            "dataset": "short_qualifying_2023_2025",
            "team": "Ferrari",
            "drivers": ["LEC", "SAI"],
            "label": "same_team_ferrari_lec_vs_sai_2023_2024_qual",
        },
        {
            "dataset": "long_qualifying_2018_2025_top5",
            "team": "Ferrari",
            "drivers": ["LEC", "SAI", "HAM"],
            "label": "same_team_ferrari_lec_sai_ham_long_qual",
        },
    ]
    rows = []
    for test in tests:
        df = datasets.get(test["dataset"])
        if df is None:
            continue
        filtered = df[
            (df["Team"] == test["team"]) & (df["Driver"].isin(test["drivers"]))
        ].copy()
        if filtered["Driver"].nunique() < 2:
            continue
        for feature_config, cols in feature_sets(filtered).items():
            rows.append(
                fit_logreg_feature_importance(
                    filtered,
                    test["dataset"],
                    test["label"],
                    "Driver",
                    feature_config,
                    cols,
                )
            )
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def group_feature_means(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    core_features = [
        "speed_mean",
        "speed_max",
        "speed_q90",
        "speed_std",
        "speed_min",
        "throttle_mean",
        "throttle_std",
        "throttle_zero_frac",
        "throttle_mid_frac",
        "throttle_full_frac",
        "throttle_diff_std",
        "throttle_diff_abs_mean",
        "brake_active_frac",
        "brake_on_count",
        "brake_std",
        "gear_mean",
        "gear_std",
        "gear_change_count",
        "rpm_mean",
        "rpm_std",
        "rpm_max",
        "rpm_diff_std",
    ]
    rows = []
    for dataset_name, df in datasets.items():
        available = [c for c in core_features if c in df.columns]
        if "Team" in df.columns:
            team_means = df.groupby("Team", dropna=False)[available].mean().reset_index()
            team_means.insert(0, "group_type", "Team")
            team_means.insert(0, "dataset", dataset_name)
            team_means = team_means.rename(columns={"Team": "group_name"})
            rows.append(team_means)
        if "Driver" in df.columns:
            driver_means = df.groupby("Driver", dropna=False)[available].mean().reset_index()
            driver_means.insert(0, "group_type", "Driver")
            driver_means.insert(0, "dataset", dataset_name)
            driver_means = driver_means.rename(columns={"Driver": "group_name"})
            rows.append(driver_means)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def main() -> None:
    datasets = load_datasets()

    coverage = pd.DataFrame(team_coverage_rows(datasets))
    team_summary = team_classification(datasets)
    same_team_summary = same_team_driver_tests(datasets)
    team_importance = team_feature_importance(datasets)
    same_team_importance = same_team_feature_importance(datasets)
    feature_means = group_feature_means(datasets)

    team_summary = team_summary.sort_values(
        ["dataset", "oof_macro_f1", "oof_accuracy"], ascending=[True, False, False]
    )
    same_team_summary = same_team_summary.sort_values(
        ["task", "oof_macro_f1", "oof_accuracy"], ascending=[True, False, False]
    )

    export_csv(coverage, "team_bias_driver_team_coverage")
    export_csv(team_summary, "team_bias_team_classification_summary")
    export_csv(same_team_summary, "team_bias_same_team_driver_summary")
    export_csv(team_importance, "team_bias_team_feature_importance")
    export_csv(same_team_importance, "team_bias_same_team_driver_feature_importance")
    export_csv(feature_means, "team_bias_group_feature_means")

    print("Team-bias analysis complete.")
    print("\nTeam prediction:")
    print(team_summary.to_string(index=False))
    print("\nSame-team driver tests:")
    print(same_team_summary.to_string(index=False))


if __name__ == "__main__":
    main()
