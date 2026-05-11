from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
EXPORTS = ROOT / "exports"
FIG_DIR = ROOT / "figures" / "thesis"
FIG_DIR.mkdir(parents=True, exist_ok=True)


SETUPS = {
    "Kwalifikacje\n2023-2025": {
        "file": EXPORTS / "lap_features_model_min_40_laps.csv",
        "drivers": ["ALB", "SAI", "VER", "OCO", "LEC"],
        "filter_file": EXPORTS / "lap_filter_summary.csv",
        "telemetry_file": EXPORTS / "best_laps_telemetry_audit.csv",
    },
    "Kwalifikacje\n2018-2025": {
        "file": EXPORTS / "balanced_top5_lap_features_2018_2025_strict.csv",
        "drivers": ["SAI", "VER", "LEC", "OCO", "HAM"],
        "filter_file": EXPORTS / "lap_filter_summary_2018_2025_strict.csv",
        "telemetry_file": EXPORTS / "balanced_top6_telemetry_audit_2018_2025_strict.csv",
    },
    "Wyścigi\n2025": {
        "file": EXPORTS / "race_2025_balanced_top5_lap_features.csv",
        "drivers": ["SAI", "VER", "LEC", "OCO", "HAM"],
        "filter_file": EXPORTS / "race_2025_filter_summary.csv",
        "telemetry_file": EXPORTS / "race_2025_balanced_top5_telemetry_audit.csv",
    },
}


STYLE_FEATURES = [
    "speed_mean",
    "speed_std",
    "speed_min",
    "speed_max",
    "throttle_mean",
    "throttle_std",
    "throttle_zero_frac",
    "throttle_full_frac",
    "brake_active_frac",
    "brake_on_count",
    "rpm_mean",
    "rpm_std",
    "gear_mean",
    "gear_change_count",
]


def savefig(name: str) -> None:
    plt.tight_layout()
    plt.savefig(FIG_DIR / name, dpi=180, bbox_inches="tight")
    plt.close()


def load_setup_frames() -> dict[str, pd.DataFrame]:
    frames = {}
    for setup_name, cfg in SETUPS.items():
        df = pd.read_csv(cfg["file"])
        if "Driver" in df.columns:
            df = df[df["Driver"].isin(cfg["drivers"])].copy()
        df["eda_setup"] = setup_name.replace("\n", " ")
        frames[setup_name] = df
    return frames


def plot_dataset_sizes(frames: dict[str, pd.DataFrame]) -> None:
    rows = []
    for setup_name, cfg in SETUPS.items():
        filter_df = pd.read_csv(cfg["filter_file"])
        raw = int(filter_df.iloc[0]["n_rows"])
        filtered_pool = int(filter_df.iloc[-1]["n_rows"])
        model_rows = len(frames[setup_name])
        rows.append(
            {
                "setup": setup_name.replace("\n", " "),
                "raw_rows": raw,
                "filtered_pool_rows": filtered_pool,
                "model_rows": model_rows,
                "retention_raw_to_model": model_rows / raw,
                "retention_filtered_to_model": model_rows / filtered_pool,
            }
        )
    overview = pd.DataFrame(rows)
    overview.to_csv(EXPORTS / "thesis_eda_dataset_overview.csv", index=False)

    x = np.arange(len(overview))
    width = 0.26
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(x - width, overview["raw_rows"], width, label="surowe okrążenia", color="#9aa7b4")
    ax.bar(x, overview["filtered_pool_rows"], width, label="po głównych filtrach", color="#4d7c9f")
    ax.bar(x + width, overview["model_rows"], width, label="w modelu", color="#c7673b")
    ax.set_yscale("log")
    ax.set_ylabel("Liczba okrążeń (skala log)")
    ax.set_title("Skala danych przed i po filtracji")
    ax.set_xticks(x)
    ax.set_xticklabels(overview["setup"], rotation=0)
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    savefig("24_eda_dataset_sizes.png")


def plot_class_balance(frames: dict[str, pd.DataFrame]) -> None:
    balance_rows = []
    for setup_name, df in frames.items():
        counts = df["Driver"].value_counts().sort_index()
        for driver, n in counts.items():
            balance_rows.append({"setup": setup_name.replace("\n", " "), "Driver": driver, "n_laps": n})
    balance = pd.DataFrame(balance_rows)
    balance.to_csv(EXPORTS / "thesis_eda_class_balance.csv", index=False)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=False)
    colors = ["#5b7894", "#c7673b", "#75845c"]
    for ax, (setup_name, group), color in zip(axes, balance.groupby("setup", sort=False), colors):
        group = group.sort_values("n_laps", ascending=False)
        ax.bar(group["Driver"], group["n_laps"], color=color)
        ax.set_title(setup_name)
        ax.set_ylabel("Liczba okrążeń")
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle("Liczebność klas kierowców w finalnych setupach", y=1.04)
    savefig("25_eda_class_balance.png")


def feature_type_inventory(frames: dict[str, pd.DataFrame]) -> None:
    id_like = {
        "lap_key",
        "Driver",
        "Team",
        "Compound",
        "session_key",
        "event_name",
        "TrackStatus",
        "SessionType",
        "eda_setup",
    }
    rows = []
    for setup_name, df in frames.items():
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = [c for c in df.columns if c not in numeric_cols]
        identifier_cols = [c for c in df.columns if c in id_like or c.lower().endswith("key")]
        model_candidate_numeric = [c for c in numeric_cols if c not in identifier_cols]
        rows.append(
            {
                "setup": setup_name.replace("\n", " "),
                "n_rows": len(df),
                "n_columns": df.shape[1],
                "numeric_columns": len(numeric_cols),
                "categorical_columns": len(categorical_cols),
                "identifier_or_context_columns": len(identifier_cols),
                "numeric_model_candidate_columns": len(model_candidate_numeric),
            }
        )
    pd.DataFrame(rows).to_csv(EXPORTS / "thesis_eda_feature_type_inventory.csv", index=False)


def plot_missingness(frames: dict[str, pd.DataFrame]) -> None:
    excluded = {
        "season",
        "round",
        "LapNumber",
        "lap_key",
        "Driver",
        "Team",
        "Compound",
        "session_key",
        "event_name",
        "SessionType",
        "SessionPart",
        "stint_id",
        "lap_time_delta_to_stint_median",
        "stint_median_lap_seconds",
        "eda_setup",
    }
    rows = []
    for setup_name, df in frames.items():
        numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in excluded]
        miss = df[numeric_cols].isna().mean().sort_values(ascending=False)
        nonzero = miss.head(10)
        for feature, frac in nonzero.items():
            rows.append({"setup": setup_name.replace("\n", " "), "feature": feature, "missing_frac": frac})
    missing = pd.DataFrame(rows)
    missing.to_csv(EXPORTS / "thesis_eda_missingness_top.csv", index=False)

    fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharex=False)
    for ax, (setup_name, group) in zip(axes, missing.groupby("setup", sort=False)):
        group = group.sort_values("missing_frac", ascending=True)
        ax.barh(group["feature"], group["missing_frac"] * 100, color="#5b7894")
        ax.set_title(setup_name)
        ax.set_xlabel("Braki danych [%]")
        ax.grid(axis="x", alpha=0.25)
    fig.suptitle("Braki danych w numerycznych cechach modelowych", y=1.02)
    savefig("26_eda_missingness.png")


def plot_sequence_lengths(frames: dict[str, pd.DataFrame]) -> None:
    rows = []
    for setup_name, cfg in SETUPS.items():
        audit = pd.read_csv(cfg["telemetry_file"])
        if "Driver" in audit.columns:
            audit = audit[audit["Driver"].isin(cfg["drivers"])].copy()
        for value in audit["merged_rows"].dropna():
            rows.append({"setup": setup_name.replace("\n", " "), "merged_rows": float(value)})
    seq = pd.DataFrame(rows)
    seq.to_csv(EXPORTS / "thesis_eda_sequence_lengths.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 5))
    labels = []
    data = []
    for setup_name, group in seq.groupby("setup", sort=False):
        labels.append(setup_name)
        data.append(group["merged_rows"].to_numpy())
    ax.boxplot(data, tick_labels=labels, showfliers=False, patch_artist=True)
    ax.set_ylabel("Liczba próbek telemetrycznych w okrążeniu")
    ax.set_title("Długość sekwencji telemetrycznych przed resamplingiem")
    ax.grid(axis="y", alpha=0.25)
    savefig("27_eda_sequence_lengths.png")


def plot_feature_distributions(frames: dict[str, pd.DataFrame]) -> None:
    combined = pd.concat(frames.values(), ignore_index=True)
    features = [
        "speed_mean",
        "speed_std",
        "throttle_full_frac",
        "throttle_zero_frac",
        "brake_active_frac",
        "gear_mean",
    ]
    existing = [f for f in features if f in combined.columns]
    rows = []
    for feature in existing:
        for setup, group in combined.groupby("eda_setup", sort=False):
            values = pd.to_numeric(group[feature], errors="coerce").dropna()
            if len(values) == 0:
                continue
            rows.append(
                {
                    "feature": feature,
                    "setup": setup,
                    "mean": values.mean(),
                    "std": values.std(),
                    "p25": values.quantile(0.25),
                    "median": values.median(),
                    "p75": values.quantile(0.75),
                }
            )
    pd.DataFrame(rows).to_csv(EXPORTS / "thesis_eda_key_feature_summary.csv", index=False)

    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    axes = axes.ravel()
    for ax, feature in zip(axes, existing):
        plot_data = []
        labels = []
        for setup, group in combined.groupby("eda_setup", sort=False):
            values = pd.to_numeric(group[feature], errors="coerce").dropna()
            plot_data.append(values)
            labels.append(setup.replace(" ", "\n"))
        ax.boxplot(plot_data, tick_labels=labels, showfliers=False, patch_artist=True)
        ax.set_title(feature)
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle("Rozkłady wybranych cech telemetrycznych", y=1.02)
    savefig("28_eda_feature_distributions.png")


def plot_correlation_heatmap(frames: dict[str, pd.DataFrame]) -> None:
    common_features = [f for f in STYLE_FEATURES if all(f in df.columns for df in frames.values())]
    combined = pd.concat([df[common_features].assign(setup=name) for name, df in frames.items()], ignore_index=True)
    corr = combined[common_features].corr()
    corr.to_csv(EXPORTS / "thesis_eda_selected_feature_correlation.csv")

    fig, ax = plt.subplots(figsize=(9.5, 8))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(np.arange(len(common_features)))
    ax.set_yticks(np.arange(len(common_features)))
    ax.set_xticklabels(common_features, rotation=45, ha="right")
    ax.set_yticklabels(common_features)
    ax.set_title("Korelacje wybranych cech telemetrycznych")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Korelacja Pearsona")
    savefig("29_eda_feature_correlation_heatmap.png")


def main() -> None:
    frames = load_setup_frames()
    plot_dataset_sizes(frames)
    plot_class_balance(frames)
    feature_type_inventory(frames)
    plot_missingness(frames)
    plot_sequence_lengths(frames)
    plot_feature_distributions(frames)
    plot_correlation_heatmap(frames)
    print("Generated EDA figures 24-29 and CSV summaries.")


if __name__ == "__main__":
    main()
