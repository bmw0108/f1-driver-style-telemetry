from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
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
    "short_qualifying_2023_2025_top5": {
        "path": EXPORT_DIR / "lap_features_model_min_40_laps.csv",
        "drivers": ["ALB", "SAI", "VER", "OCO", "LEC"],
    },
    "long_qualifying_2018_2025_top5": {
        "path": EXPORT_DIR / "balanced_top5_lap_features_2018_2025_strict.csv",
        "drivers": ["SAI", "VER", "LEC", "OCO", "HAM"],
    },
    "race_2025_clean_laps_top5": {
        "path": EXPORT_DIR / "race_2025_balanced_top5_lap_features.csv",
        "drivers": ["SAI", "VER", "LEC", "OCO", "HAM"],
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


def feature_sets(df: pd.DataFrame) -> dict[str, list[str]]:
    base_excluded = {
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
    context_features = {
        "Compound",
        "TyreLife",
        "Stint",
        "SessionPart",
        "drs_active_frac",
    }
    all_missing = {c for c in df.columns if df[c].isna().all()}

    def keep(excluded: set[str]) -> list[str]:
        return [c for c in df.columns if c not in excluded and c not in all_missing]

    return {
        "all_telemetry_features": keep(base_excluded | weak_or_constant),
        "no_time_features": keep(base_excluded | weak_or_constant | time_features),
        "style_core_no_time_context": keep(
            base_excluded | weak_or_constant | time_features | context_features
        ),
    }


def build_model(model_name: str, feature_cols: list[str]) -> Pipeline:
    # The concrete feature dtypes are only known at fit time, so the caller passes
    # a pre-split column list via DataFrame selection before building the pipeline.
    # This helper is kept for backwards compatibility with numeric-only calls.
    return build_model_for_frame(model_name, None, feature_cols)


def build_model_for_frame(model_name: str, X: pd.DataFrame | None, feature_cols: list[str]) -> Pipeline:
    if X is None:
        numeric_features = feature_cols
        categorical_features = []
    else:
        categorical_features = [c for c in feature_cols if X[c].dtype == "object"]
        numeric_features = [c for c in feature_cols if c not in categorical_features]

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
            )
        ],
        remainder="drop",
    )

    if model_name == "logistic_l2":
        model = LogisticRegression(
            penalty="l2",
            C=1.0,
            solver="lbfgs",
            max_iter=2000,
            random_state=RANDOM_STATE,
        )
    elif model_name == "logistic_l1":
        model = LogisticRegression(
            penalty="l1",
            C=2.0,
            solver="saga",
            max_iter=2500,
            random_state=RANDOM_STATE,
        )
    elif model_name == "random_forest_regularized":
        model = RandomForestClassifier(
            n_estimators=160,
            max_depth=8,
            min_samples_leaf=5,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
    elif model_name == "hist_gradient_boosting_regularized":
        model = HistGradientBoostingClassifier(
            learning_rate=0.04,
            max_iter=120,
            max_leaf_nodes=15,
            l2_regularization=0.2,
            random_state=RANDOM_STATE,
        )
    else:
        raise ValueError(model_name)

    return Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])


def make_direct_oof(
    df: pd.DataFrame,
    target_col: str,
    feature_cols: list[str],
    groups: np.ndarray,
    model_name: str,
) -> tuple[np.ndarray, LabelEncoder]:
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df[target_col].astype(str))
    min_count = pd.Series(y).value_counts().min()
    n_splits = min(N_SPLITS, int(min_count))
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    oof = np.full(len(df), -1, dtype=int)
    X = df[feature_cols].copy()

    for train_idx, test_idx in cv.split(X, y, groups):
        model = build_model_for_frame(model_name, X.iloc[train_idx], feature_cols)
        model.fit(X.iloc[train_idx], y[train_idx])
        oof[test_idx] = model.predict(X.iloc[test_idx])
    return oof, label_encoder


def train_team_specific_driver_model(
    train_df: pd.DataFrame,
    team: str,
    feature_cols: list[str],
    model_name: str,
) -> tuple[Pipeline | None, LabelEncoder | None, str | None]:
    team_df = train_df[train_df["Team"] == team]
    drivers = sorted(team_df["Driver"].astype(str).unique())
    if len(drivers) == 0:
        return None, None, None
    if len(drivers) == 1:
        return None, None, drivers[0]

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(team_df["Driver"].astype(str))
    model = build_model_for_frame(model_name, team_df[feature_cols], feature_cols)
    model.fit(team_df[feature_cols], y)
    return model, label_encoder, None


def hierarchical_oof(
    df: pd.DataFrame,
    feature_cols: list[str],
    team_model_name: str,
    driver_model_name: str,
) -> tuple[np.ndarray, np.ndarray]:
    driver_encoder = LabelEncoder()
    team_encoder = LabelEncoder()
    y_driver = driver_encoder.fit_transform(df["Driver"].astype(str))
    y_team = team_encoder.fit_transform(df["Team"].astype(str))
    groups = df[session_column(df)].astype(str).to_numpy()

    min_count = pd.Series(y_team).value_counts().min()
    n_splits = min(N_SPLITS, int(min_count))
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)

    oof_team = np.full(len(df), -1, dtype=int)
    oof_driver = np.full(len(df), -1, dtype=int)
    X = df[feature_cols].copy()

    for train_idx, test_idx in cv.split(X, y_team, groups):
        train_df = df.iloc[train_idx].copy()
        test_df = df.iloc[test_idx].copy()

        team_model = build_model_for_frame(team_model_name, train_df[feature_cols], feature_cols)
        team_model.fit(train_df[feature_cols], y_team[train_idx])
        pred_team_idx = team_model.predict(test_df[feature_cols])
        oof_team[test_idx] = pred_team_idx
        pred_team_names = team_encoder.inverse_transform(pred_team_idx)

        global_driver_model = build_model_for_frame(driver_model_name, train_df[feature_cols], feature_cols)
        global_driver_model.fit(train_df[feature_cols], y_driver[train_idx])

        local_models = {}
        for predicted_team in sorted(set(pred_team_names)):
            local_models[predicted_team] = train_team_specific_driver_model(
                train_df,
                predicted_team,
                feature_cols,
                driver_model_name,
            )

        for predicted_team in sorted(set(pred_team_names)):
            fold_positions = test_idx[pred_team_names == predicted_team]
            x_rows = df.iloc[fold_positions][feature_cols]
            model, local_encoder, constant_driver = local_models[predicted_team]
            if constant_driver is not None:
                predicted_drivers = [constant_driver] * len(fold_positions)
            elif model is not None and local_encoder is not None:
                local_pred = model.predict(x_rows)
                predicted_drivers = local_encoder.inverse_transform(local_pred)
            else:
                fallback_pred = global_driver_model.predict(x_rows)
                predicted_drivers = driver_encoder.inverse_transform(fallback_pred)
            oof_driver[fold_positions] = driver_encoder.transform(predicted_drivers)

    return oof_team, oof_driver


def dataset_rows(
    dataset_name: str,
    df: pd.DataFrame,
    feature_config: str,
    feature_cols: list[str],
    model_names: list[str],
) -> list[dict[str, object]]:
    group_col = session_column(df)
    groups = df[group_col].astype(str).to_numpy()

    rows = []
    for model_name in model_names:
        direct_driver_pred, driver_encoder = make_direct_oof(
            df, "Driver", feature_cols, groups, model_name
        )
        direct_team_pred, team_encoder = make_direct_oof(
            df, "Team", feature_cols, groups, model_name
        )
        y_driver = driver_encoder.transform(df["Driver"].astype(str))
        y_team = team_encoder.transform(df["Team"].astype(str))

        for result_name, target_name, y_true, y_pred, team_model_name, driver_model_name in [
            ("direct_driver", "Driver", y_driver, direct_driver_pred, None, model_name),
            ("direct_team", "Team", y_team, direct_team_pred, model_name, None),
        ]:
            rows.append(
                {
                    "dataset": dataset_name,
                    "feature_config": feature_config,
                    "result_name": result_name,
                    "target": target_name,
                    "team_model": team_model_name,
                    "driver_model": driver_model_name,
                    "n_samples": len(df),
                    "n_drivers": df["Driver"].nunique(),
                    "n_teams": df["Team"].nunique(),
                    "n_groups": df[group_col].nunique(),
                    "n_features": len(feature_cols),
                    "accuracy": accuracy_score(y_true, y_pred),
                    "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
                    "macro_f1": f1_score(y_true, y_pred, average="macro"),
                }
            )

    hierarchical_pairs = [
        ("logistic_l2", "logistic_l2"),
        ("random_forest_regularized", "logistic_l2"),
        ("hist_gradient_boosting_regularized", "logistic_l2"),
        ("logistic_l2", "random_forest_regularized"),
        ("logistic_l2", "hist_gradient_boosting_regularized"),
    ]
    if feature_config != "style_core_no_time_context":
        return rows

    for team_model_name, driver_model_name in hierarchical_pairs:
            hierarchical_team_pred, hierarchical_driver_pred = hierarchical_oof(
                df, feature_cols, team_model_name, driver_model_name
            )
            driver_encoder = LabelEncoder().fit(df["Driver"].astype(str))
            team_encoder = LabelEncoder().fit(df["Team"].astype(str))
            y_driver = driver_encoder.transform(df["Driver"].astype(str))
            y_team = team_encoder.transform(df["Team"].astype(str))
            for result_name, target_name, y_true, y_pred in [
                ("hierarchical_team_stage", "Team", y_team, hierarchical_team_pred),
                ("hierarchical_driver_final", "Driver", y_driver, hierarchical_driver_pred),
            ]:
                rows.append(
                    {
                        "dataset": dataset_name,
                        "feature_config": feature_config,
                        "result_name": result_name,
                        "target": target_name,
                        "team_model": team_model_name,
                        "driver_model": driver_model_name,
                        "n_samples": len(df),
                        "n_drivers": df["Driver"].nunique(),
                        "n_teams": df["Team"].nunique(),
                        "n_groups": df[group_col].nunique(),
                        "n_features": len(feature_cols),
                        "accuracy": accuracy_score(y_true, y_pred),
                        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
                        "macro_f1": f1_score(y_true, y_pred, average="macro"),
                    }
                )
    return rows


def main() -> None:
    rows = []
    coverage_rows = []
    direct_model_names = [
        "logistic_l2",
        "random_forest_regularized",
        "hist_gradient_boosting_regularized",
    ]

    for dataset_name, config in DATASETS.items():
        path = config["path"]
        if not path.exists():
            continue
        df = pd.read_csv(path)
        df = df[df["Driver"].isin(config["drivers"])].copy()
        df = df.dropna(subset=["Driver", "Team"])
        for feature_config, cols in feature_sets(df).items():
            print(f"Running {dataset_name} / {feature_config}", flush=True)
            rows.extend(dataset_rows(dataset_name, df, feature_config, cols, direct_model_names))

        coverage = (
            df.groupby(["Driver", "Team"], dropna=False)
            .size()
            .reset_index(name="n_laps")
            .sort_values(["Driver", "n_laps"], ascending=[True, False])
        )
        coverage.insert(0, "dataset", dataset_name)
        coverage_rows.append(coverage)

    summary = pd.DataFrame(rows)
    best = (
        summary.sort_values(["dataset", "result_name", "macro_f1", "accuracy"], ascending=[True, True, False, False])
        .groupby(["dataset", "result_name"], as_index=False)
        .head(1)
        .reset_index(drop=True)
    )
    coverage = pd.concat(coverage_rows, ignore_index=True)

    export_csv(summary, "hierarchical_team_driver_summary")
    export_csv(best, "hierarchical_team_driver_best_models")
    export_csv(coverage, "hierarchical_team_driver_coverage")

    print("Hierarchical team-driver analysis complete.")
    print(best.to_string(index=False))


if __name__ == "__main__":
    main()
