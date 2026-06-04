from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import warnings
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
N_PERMUTATION_REPEATS = 5
warnings.filterwarnings("ignore", category=UserWarning)


DATASETS = {
    "short_qualifying_2023_2025_top5": {
        "label": "Kwalifikacje 2023-2025",
        "path": EXPORT_DIR / "lap_features_model_min_40_laps.csv",
        "drivers": ["ALB", "SAI", "VER", "OCO", "LEC"],
        "feature_config": "final_compact_importance_features",
        "model_config": "logistic_l1_c2",
    },
    "long_qualifying_2018_2025_top5": {
        "label": "Kwalifikacje 2018-2025",
        "path": EXPORT_DIR / "balanced_top5_lap_features_2018_2025_strict.csv",
        "drivers": ["SAI", "VER", "LEC", "OCO", "HAM"],
        "feature_config": "style_core_no_time_context",
        "model_config": "logistic_l2_c1",
    },
    "race_2025_clean_laps_top5": {
        "label": "Wyścigi 2025",
        "path": EXPORT_DIR / "race_2025_balanced_top5_lap_features.csv",
        "drivers": ["SAI", "VER", "LEC", "OCO", "HAM"],
        "feature_config": "style_core_no_time_context",
        "model_config": "logistic_l2_c1",
    },
}


def export_csv(df: pd.DataFrame, name: str) -> Path:
    path = EXPORT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    print(f"Saved {path}")
    return path


def load_dataset(config: dict) -> pd.DataFrame:
    df = pd.read_csv(config["path"])
    df = df[df["Driver"].isin(config["drivers"])].copy()
    if "session_key" not in df.columns:
        df["session_key"] = df["season"].astype(str) + "_" + df["round"].astype(str)
    if "event_name" not in df.columns:
        df["event_name"] = "round_" + df["round"].astype(str)
    return df.reset_index(drop=True)


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
        "DRS",
    }
    all_missing = {c for c in df.columns if df[c].isna().all()}

    def keep(excluded: set[str]) -> list[str]:
        return [c for c in df.columns if c not in excluded and c not in all_missing]

    sets = {
        "all_telemetry_features": keep(base_excluded | weak_or_constant),
        "no_time_features": keep(base_excluded | weak_or_constant | time_features),
        "style_core_no_time_context": keep(base_excluded | weak_or_constant | time_features | context_features),
    }

    importance_path = EXPORT_DIR / "final_model_feature_importance_global.csv"
    if importance_path.exists():
        final_features = (
            pd.read_csv(importance_path)["feature"]
            .astype(str)
            .str.replace(r"^(num|cat)__", "", regex=True)
            .tolist()
        )
        sets["final_compact_importance_features"] = [c for c in final_features if c in df.columns and c not in all_missing]
    return sets


def build_model(df: pd.DataFrame, feature_cols: list[str], model_config: str) -> Pipeline:
    categorical_features = [c for c in feature_cols if df[c].dtype == "object"]
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
            ),
        ],
        remainder="drop",
    )
    if model_config == "logistic_l1_c2":
        model = LogisticRegression(
            penalty="l1",
            C=2.0,
            solver="saga",
            max_iter=10000,
            random_state=RANDOM_STATE,
        )
    elif model_config == "logistic_l2_c1":
        model = LogisticRegression(
            penalty="l2",
            C=1.0,
            solver="lbfgs",
            max_iter=2000,
            random_state=RANDOM_STATE,
        )
    else:
        raise ValueError(model_config)
    return Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])


def encode_target(df: pd.DataFrame) -> tuple[np.ndarray, LabelEncoder]:
    encoder = LabelEncoder()
    return encoder.fit_transform(df["Driver"].astype(str)), encoder


def family_for_feature(feature: str) -> str:
    if feature.startswith("speed"):
        return "speed"
    if feature.startswith("throttle"):
        return "throttle"
    if feature.startswith("brake"):
        return "brake"
    if feature.startswith("rpm"):
        return "rpm"
    if feature.startswith("gear") or feature.startswith("nGear"):
        return "gear"
    if "LapTime" in feature or "Sector" in feature or "sector" in feature or "lap_time" in feature:
        return "time"
    if feature in {"Compound", "TyreLife", "Stint", "SessionPart"}:
        return "context"
    if "diff" in feature:
        return "signal_dynamics"
    return "other"


def permutation_importance_for_dataset(
    dataset_name: str,
    df: pd.DataFrame,
    feature_cols: list[str],
    model_config: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    y, _ = encode_target(df)
    groups = df["session_key"].astype(str).to_numpy()
    n_splits = min(N_SPLITS, int(pd.Series(y).value_counts().min()))
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    rng = np.random.default_rng(RANDOM_STATE)

    feature_rows: list[dict] = []
    family_rows: list[dict] = []
    baseline_rows: list[dict] = []
    families = {}
    for feature in feature_cols:
        families.setdefault(family_for_feature(feature), []).append(feature)

    X = df[feature_cols].copy()
    for fold, (train_idx, test_idx) in enumerate(cv.split(X, y, groups), start=1):
        model = build_model(X.iloc[train_idx], feature_cols, model_config)
        model.fit(X.iloc[train_idx], y[train_idx])
        baseline_pred = model.predict(X.iloc[test_idx])
        baseline_macro_f1 = f1_score(y[test_idx], baseline_pred, average="macro")
        baseline_rows.append(
            {
                "dataset": dataset_name,
                "fold": fold,
                "n_train": len(train_idx),
                "n_test": len(test_idx),
                "baseline_macro_f1": baseline_macro_f1,
                "baseline_accuracy": accuracy_score(y[test_idx], baseline_pred),
                "baseline_balanced_accuracy": balanced_accuracy_score(y[test_idx], baseline_pred),
            }
        )

        for feature in feature_cols:
            drops = []
            for _ in range(N_PERMUTATION_REPEATS):
                x_perm = X.iloc[test_idx].copy()
                x_perm[feature] = rng.permutation(x_perm[feature].to_numpy())
                pred = model.predict(x_perm)
                drops.append(baseline_macro_f1 - f1_score(y[test_idx], pred, average="macro"))
            feature_rows.append(
                {
                    "dataset": dataset_name,
                    "fold": fold,
                    "feature": feature,
                    "feature_family": family_for_feature(feature),
                    "importance_macro_f1_drop_mean": float(np.mean(drops)),
                    "importance_macro_f1_drop_std": float(np.std(drops, ddof=1)) if len(drops) > 1 else 0.0,
                }
            )

        for family, cols in families.items():
            drops = []
            for _ in range(N_PERMUTATION_REPEATS):
                x_perm = X.iloc[test_idx].copy()
                for col in cols:
                    x_perm[col] = rng.permutation(x_perm[col].to_numpy())
                pred = model.predict(x_perm)
                drops.append(baseline_macro_f1 - f1_score(y[test_idx], pred, average="macro"))
            family_rows.append(
                {
                    "dataset": dataset_name,
                    "fold": fold,
                    "feature_family": family,
                    "n_features": len(cols),
                    "importance_macro_f1_drop_mean": float(np.mean(drops)),
                    "importance_macro_f1_drop_std": float(np.std(drops, ddof=1)) if len(drops) > 1 else 0.0,
                }
            )

    feature_df = pd.DataFrame(feature_rows)
    family_df = pd.DataFrame(family_rows)
    baseline_df = pd.DataFrame(baseline_rows)
    return feature_df, family_df, baseline_df


def summarize_importance(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    return (
        df.groupby(group_cols, as_index=False)
        .agg(
            importance_macro_f1_drop_mean=("importance_macro_f1_drop_mean", "mean"),
            importance_macro_f1_drop_std=("importance_macro_f1_drop_mean", "std"),
            n_folds=("fold", "nunique"),
        )
        .sort_values("importance_macro_f1_drop_mean", ascending=False)
    )


def evaluate_holdout(
    dataset_name: str,
    df: pd.DataFrame,
    feature_cols: list[str],
    model_config: str,
    holdout_col: str,
) -> pd.DataFrame:
    y, encoder = encode_target(df)
    X = df[feature_cols].copy()
    rows: list[dict] = []
    for holdout_value, test_df in df.groupby(holdout_col, sort=True):
        test_idx = test_df.index.to_numpy()
        train_idx = df.index.difference(test_idx).to_numpy()
        if len(np.unique(y[test_idx])) < 2 or len(np.unique(y[train_idx])) < len(encoder.classes_):
            status = "skipped_insufficient_classes"
            rows.append(
                {
                    "dataset": dataset_name,
                    "holdout_type": holdout_col,
                    "holdout_value": holdout_value,
                    "status": status,
                    "n_train": len(train_idx),
                    "n_test": len(test_idx),
                    "n_test_classes": len(np.unique(y[test_idx])),
                }
            )
            continue
        model = build_model(X.iloc[train_idx], feature_cols, model_config)
        model.fit(X.iloc[train_idx], y[train_idx])
        pred = model.predict(X.iloc[test_idx])
        rows.append(
            {
                "dataset": dataset_name,
                "holdout_type": holdout_col,
                "holdout_value": holdout_value,
                "status": "ok",
                "n_train": len(train_idx),
                "n_test": len(test_idx),
                "n_test_classes": len(np.unique(y[test_idx])),
                "accuracy": accuracy_score(y[test_idx], pred),
                "balanced_accuracy": balanced_accuracy_score(y[test_idx], pred),
                "macro_f1": f1_score(y[test_idx], pred, average="macro"),
            }
        )
    return pd.DataFrame(rows)


def evaluate_cross_era(dataset_name: str, df: pd.DataFrame, feature_cols: list[str], model_config: str) -> pd.DataFrame:
    if "season" not in df.columns or df["season"].nunique() < 2:
        return pd.DataFrame()
    eras = {
        "train_2018_2021_test_2022_2025": (df["season"] <= 2021, df["season"] >= 2022),
        "train_2022_2025_test_2018_2021": (df["season"] >= 2022, df["season"] <= 2021),
    }
    y, encoder = encode_target(df)
    X = df[feature_cols].copy()
    rows: list[dict] = []
    for name, (train_mask, test_mask) in eras.items():
        train_idx = df.index[train_mask].to_numpy()
        test_idx = df.index[test_mask].to_numpy()
        if len(test_idx) == 0 or len(train_idx) == 0 or len(np.unique(y[train_idx])) < len(encoder.classes_) or len(np.unique(y[test_idx])) < 2:
            rows.append(
                {
                    "dataset": dataset_name,
                    "evaluation": name,
                    "status": "skipped_insufficient_classes",
                    "n_train": len(train_idx),
                    "n_test": len(test_idx),
                }
            )
            continue
        model = build_model(X.iloc[train_idx], feature_cols, model_config)
        model.fit(X.iloc[train_idx], y[train_idx])
        pred = model.predict(X.iloc[test_idx])
        rows.append(
            {
                "dataset": dataset_name,
                "evaluation": name,
                "status": "ok",
                "n_train": len(train_idx),
                "n_test": len(test_idx),
                "accuracy": accuracy_score(y[test_idx], pred),
                "balanced_accuracy": balanced_accuracy_score(y[test_idx], pred),
                "macro_f1": f1_score(y[test_idx], pred, average="macro"),
            }
        )
    return pd.DataFrame(rows)


def oof_context_diagnostics() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[pd.DataFrame] = []
    sources = [
        ("long_qualifying_2018_2025_top5", EXPORT_DIR / "long_qualifying_top5_sequence_full_rerun_oof_predictions.csv"),
        ("race_2025_clean_laps_top5", EXPORT_DIR / "race_2025_top5_sequence_full_rerun_oof_predictions.csv"),
    ]
    for dataset_name, path in sources:
        if not path.exists():
            continue
        df = pd.read_csv(path)
        df["is_correct"] = df["true_driver"].astype(str) == df["pred_driver"].astype(str)
        for col in ["season", "round", "event_name"]:
            if col not in df.columns:
                continue
            group_rows = []
            for keys, group in df.groupby(["model", col], dropna=False):
                model, value = keys
                group_rows.append(
                    {
                        "dataset": dataset_name,
                        "model": model,
                        "context_type": col,
                        "context_value": value,
                        "n_samples": len(group),
                        "accuracy": accuracy_score(group["true_driver"], group["pred_driver"]),
                        "macro_f1": f1_score(group["true_driver"], group["pred_driver"], average="macro"),
                    }
                )
            rows.append(pd.DataFrame(group_rows))
    diagnostics = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    summary = (
        diagnostics.groupby(["dataset", "model", "context_type"], as_index=False)
        .agg(
            n_contexts=("context_value", "nunique"),
            macro_f1_mean=("macro_f1", "mean"),
            macro_f1_std=("macro_f1", "std"),
            macro_f1_min=("macro_f1", "min"),
            macro_f1_max=("macro_f1", "max"),
            accuracy_mean=("accuracy", "mean"),
            accuracy_std=("accuracy", "std"),
        )
        if not diagnostics.empty
        else pd.DataFrame()
    )
    return diagnostics, summary


def main() -> None:
    all_feature_importance = []
    all_family_importance = []
    all_perm_baselines = []
    all_holdout = []
    all_cross_era = []

    for dataset_name, config in DATASETS.items():
        print(f"\n=== {dataset_name} ===")
        df = load_dataset(config)
        features = feature_sets(df)[config["feature_config"]]
        print(f"Rows={len(df)}, features={len(features)}, model={config['model_config']}")

        feature_imp, family_imp, baseline = permutation_importance_for_dataset(
            dataset_name,
            df,
            features,
            config["model_config"],
        )
        all_feature_importance.append(feature_imp)
        all_family_importance.append(family_imp)
        all_perm_baselines.append(baseline)

        if df["season"].nunique() > 1:
            all_holdout.append(evaluate_holdout(dataset_name, df, features, config["model_config"], "season"))
            all_cross_era.append(evaluate_cross_era(dataset_name, df, features, config["model_config"]))
        all_holdout.append(evaluate_holdout(dataset_name, df, features, config["model_config"], "event_name"))

    feature_importance = pd.concat(all_feature_importance, ignore_index=True)
    family_importance = pd.concat(all_family_importance, ignore_index=True)
    perm_baselines = pd.concat(all_perm_baselines, ignore_index=True)
    holdout = pd.concat(all_holdout, ignore_index=True)
    cross_era = pd.concat([x for x in all_cross_era if not x.empty], ignore_index=True) if all_cross_era else pd.DataFrame()
    diagnostics, diagnostics_summary = oof_context_diagnostics()

    export_csv(feature_importance, "thesis_permutation_importance_by_fold")
    export_csv(
        summarize_importance(feature_importance, ["dataset", "feature", "feature_family"]),
        "thesis_permutation_importance_summary",
    )
    export_csv(family_importance, "thesis_permutation_family_importance_by_fold")
    export_csv(
        summarize_importance(family_importance, ["dataset", "feature_family", "n_features"]),
        "thesis_permutation_family_importance_summary",
    )
    export_csv(perm_baselines, "thesis_permutation_baseline_metrics")
    export_csv(holdout, "thesis_leave_one_context_out_results")
    if not cross_era.empty:
        export_csv(cross_era, "thesis_cross_era_results")
    export_csv(diagnostics, "thesis_oof_context_diagnostics")
    export_csv(diagnostics_summary, "thesis_oof_context_diagnostics_summary")

    print("\nTop family importance:")
    print(
        summarize_importance(family_importance, ["dataset", "feature_family", "n_features"])
        .groupby("dataset")
        .head(5)
        .to_string(index=False)
    )

    print("\nLeave-one-context summary:")
    ok = holdout[holdout["status"] == "ok"]
    if not ok.empty:
        print(
            ok.groupby(["dataset", "holdout_type"], as_index=False)
            .agg(n_contexts=("holdout_value", "nunique"), macro_f1_mean=("macro_f1", "mean"), macro_f1_std=("macro_f1", "std"), macro_f1_min=("macro_f1", "min"))
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()
