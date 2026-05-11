from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
import time
import traceback

import fastf1
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


EXPORT_DIR = Path("exports")
CACHE_DIR = Path("f1_cache")
FIG_DIR = Path("figures") / "thesis"
FIG_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_LAPS_PATH = EXPORT_DIR / "session_driver_best_laps_2018_2025_strict.csv"
TARGETS_PATH = EXPORT_DIR / "red_bull_teammate_window_targets.csv"
AUDIT_PATH = EXPORT_DIR / "red_bull_teammate_window_telemetry_audit.csv"
TELEMETRY_PATH = EXPORT_DIR / "red_bull_teammate_window_telemetry_merged.csv"
FEATURES_PATH = EXPORT_DIR / "red_bull_teammate_window_lap_features.csv"
LOG_PATH = EXPORT_DIR / "red_bull_teammate_window.log"

RATE_LIMIT_SLEEP_SECONDS = 3600

TEAM_LEADERS = {
    "Red Bull Racing": "VER",
    "Ferrari": "LEC",
    "Mercedes": "HAM",
}

STYLE_FEATURES = [
    "LapTimeSeconds",
    "speed_mean",
    "speed_min",
    "speed_q10",
    "speed_q50",
    "speed_q90",
    "speed_std",
    "throttle_mean",
    "throttle_zero_frac",
    "throttle_full_frac",
    "throttle_mid_frac",
    "throttle_diff_abs_mean",
    "brake_active_frac",
    "brake_on_count",
    "first_brake_frac_pos",
    "last_brake_frac_pos",
    "rpm_mean",
    "rpm_std",
    "rpm_diff_abs_mean",
    "gear_mean",
    "gear_change_count",
]

PROXY_FEATURES = [
    "LapTimeSeconds",
    "speed_min",
    "speed_mean",
    "throttle_full_frac",
    "throttle_mid_frac",
    "throttle_diff_abs_mean",
    "brake_active_frac",
    "brake_on_count",
    "rpm_diff_abs_mean",
    "gear_change_count",
]


def log(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


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


def timed_to_seconds(series: pd.Series) -> pd.Series:
    return pd.to_timedelta(series, errors="coerce").dt.total_seconds()


def is_rate_limit_error(exc: Exception) -> bool:
    text = f"{type(exc).__name__}: {exc}".lower()
    return any(token in text for token in ["429", "rate limit", "ratelimit", "too many requests"])


def call_with_rate_limit_retry(fn, description: str):
    attempt = 0
    while True:
        attempt += 1
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            if is_rate_limit_error(exc):
                log(
                    f"{description}: detected rate limit on attempt {attempt}. "
                    f"Sleeping for {RATE_LIMIT_SLEEP_SECONDS // 3600} hour before retry."
                )
                time.sleep(RATE_LIMIT_SLEEP_SECONDS)
                continue
            raise


def append_csv_rows(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    df = pd.DataFrame(rows)
    header = not path.exists()
    df.to_csv(path, mode="a", header=header, index=False)


def append_df(path: Path, df: pd.DataFrame) -> None:
    if df.empty:
        return
    header = not path.exists()
    df.to_csv(path, mode="a", header=header, index=False)


def build_targets() -> pd.DataFrame:
    laps = pd.read_csv(SOURCE_LAPS_PATH)
    target_rows = []
    for team, leader in TEAM_LEADERS.items():
        team_df = laps[laps["Team"] == team].copy()
        for session_key, session_df in team_df.groupby("session_key"):
            if leader not in set(session_df["Driver"]):
                continue
            if session_df["Driver"].nunique() < 2:
                continue
            for _, row in session_df.iterrows():
                if row["Driver"] == leader or row["Driver"] != leader:
                    out = row.to_dict()
                    out["analysis_team"] = team
                    out["leader_driver"] = leader
                    target_rows.append(out)

    targets = pd.DataFrame(target_rows).drop_duplicates("lap_key")
    targets = targets.sort_values(["season", "round", "Team", "Driver"]).reset_index(drop=True)
    export_csv(targets, "red_bull_teammate_window_targets")
    return targets


def done_lap_keys() -> set[str]:
    if not AUDIT_PATH.exists():
        return set()
    audit = pd.read_csv(AUDIT_PATH)
    return set(audit.loc[audit["status"] == "ok", "lap_key"].astype(str))


def extract_telemetry(targets: pd.DataFrame) -> None:
    fastf1.Cache.enable_cache(str(CACHE_DIR))
    done = done_lap_keys()
    pending = targets[~targets["lap_key"].astype(str).isin(done)].copy()
    log(f"Targets: {len(targets)}; already extracted: {len(done)}; pending: {len(pending)}")
    if pending.empty:
        return

    for (season, round_number), group in pending.groupby(["season", "round"], sort=True):
        log(f"Loading {season} R{int(round_number):02d} Q for {len(group)} target laps")
        telemetry_rows = []
        audit_rows = []
        try:
            session = fastf1.get_session(int(season), int(round_number), "Q")
            call_with_rate_limit_retry(
                lambda: session.load(laps=True, telemetry=True, weather=False, messages=False),
                f"session.load({season}, R{int(round_number):02d}, Q)",
            )
            laps = session.laps.copy()

            for _, target in group.iterrows():
                lap_key = str(target["lap_key"])
                driver = target["Driver"]
                lap_number = target["LapNumber"]
                try:
                    candidate = laps[(laps["Driver"] == driver) & (laps["LapNumber"] == lap_number)].copy()
                    if len(candidate) != 1:
                        audit_rows.append(
                            {
                                "lap_key": lap_key,
                                "season": season,
                                "round": round_number,
                                "Driver": driver,
                                "LapNumber": lap_number,
                                "status": "lap_match_not_unique",
                                "n_matches": len(candidate),
                            }
                        )
                        continue

                    lap = candidate.iloc[0]
                    car_data = lap.get_car_data().copy()
                    pos_data = lap.get_pos_data().copy()

                    if "Time" in car_data.columns:
                        car_data["telemetry_time_sec"] = timed_to_seconds(car_data["Time"])
                    if "SessionTime" in car_data.columns:
                        car_data["telemetry_session_time_sec"] = timed_to_seconds(car_data["SessionTime"])
                    if "Time" in pos_data.columns:
                        pos_data["pos_time_sec"] = timed_to_seconds(pos_data["Time"])
                    if "SessionTime" in pos_data.columns:
                        pos_data["pos_session_time_sec"] = timed_to_seconds(pos_data["SessionTime"])

                    for df_ in [car_data, pos_data]:
                        df_["lap_key"] = lap_key
                        df_["season"] = season
                        df_["round"] = round_number
                        df_["Driver"] = driver
                        df_["LapNumber"] = lap_number

                    meta_cols = [
                        "LapTimeSeconds",
                        "Sector1TimeSeconds",
                        "Sector2TimeSeconds",
                        "Sector3TimeSeconds",
                        "Compound",
                        "TyreLife",
                        "Team",
                        "session_key",
                        "event_name",
                        "analysis_team",
                        "leader_driver",
                    ]
                    for col in meta_cols:
                        car_data[col] = target.get(col)

                    pos_keep = [
                        c for c in pos_data.columns
                        if c in ["lap_key", "X", "Y", "Z", "Status", "pos_time_sec", "pos_session_time_sec"]
                    ]
                    pos_data = pos_data[pos_keep].copy()

                    car_data = car_data.reset_index(drop=True)
                    pos_data = pos_data.reset_index(drop=True)
                    n_rows = min(len(car_data), len(pos_data))
                    merged = pd.concat(
                        [
                            car_data.iloc[:n_rows].reset_index(drop=True),
                            pos_data.drop(columns=["lap_key"], errors="ignore").iloc[:n_rows].reset_index(drop=True),
                        ],
                        axis=1,
                    )
                    merged["sample_idx"] = np.arange(len(merged))
                    telemetry_rows.append(merged)
                    audit_rows.append(
                        {
                            "lap_key": lap_key,
                            "season": season,
                            "round": round_number,
                            "Driver": driver,
                            "LapNumber": lap_number,
                            "status": "ok",
                            "car_rows": len(car_data),
                            "pos_rows": len(pos_data),
                            "merged_rows": len(merged),
                        }
                    )
                except Exception as exc:  # noqa: BLE001
                    audit_rows.append(
                        {
                            "lap_key": lap_key,
                            "season": season,
                            "round": round_number,
                            "Driver": driver,
                            "LapNumber": lap_number,
                            "status": "lap_extract_error",
                            "error_type": type(exc).__name__,
                            "error_msg": str(exc),
                        }
                    )

            append_df(TELEMETRY_PATH, pd.concat(telemetry_rows, ignore_index=True) if telemetry_rows else pd.DataFrame())
            append_csv_rows(AUDIT_PATH, audit_rows)
            log(f"Completed {season} R{int(round_number):02d}: {sum(r['status'] == 'ok' for r in audit_rows)}/{len(group)} ok")
        except Exception as exc:  # noqa: BLE001
            log(f"Session failed {season} R{int(round_number):02d}: {type(exc).__name__}: {exc}")
            log(traceback.format_exc(limit=3).strip())
            append_csv_rows(
                AUDIT_PATH,
                [
                    {
                        "lap_key": str(target["lap_key"]),
                        "season": season,
                        "round": round_number,
                        "Driver": target["Driver"],
                        "LapNumber": target["LapNumber"],
                        "status": "session_load_error",
                        "error_type": type(exc).__name__,
                        "error_msg": str(exc),
                    }
                    for _, target in group.iterrows()
                ],
            )


def safe_frac(mask: pd.Series) -> float:
    return float(mask.mean()) if len(mask) else np.nan


def first_true_frac_pos(mask: pd.Series) -> float:
    idx = np.flatnonzero(mask.to_numpy())
    if len(idx) == 0:
        return np.nan
    return float(idx[0] / max(len(mask) - 1, 1))


def last_true_frac_pos(mask: pd.Series) -> float:
    idx = np.flatnonzero(mask.to_numpy())
    if len(idx) == 0:
        return np.nan
    return float(idx[-1] / max(len(mask) - 1, 1))


def count_state_changes(mask: pd.Series) -> int:
    values = mask.astype(int).to_numpy()
    if len(values) <= 1:
        return 0
    return int(np.abs(np.diff(values)).sum())


def brake_to_float(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    mapped = series.astype(str).str.strip().str.lower().map({"true": 1.0, "false": 0.0})
    return numeric.fillna(mapped).fillna(0.0).astype(float)


def build_features_for_lap(lap_df: pd.DataFrame) -> dict:
    lap_df = lap_df.sort_values("sample_idx").reset_index(drop=True)
    speed = pd.to_numeric(lap_df["Speed"], errors="coerce")
    throttle = pd.to_numeric(lap_df["Throttle"], errors="coerce")
    rpm = pd.to_numeric(lap_df["RPM"], errors="coerce")
    gear = pd.to_numeric(lap_df["nGear"], errors="coerce")
    brake = brake_to_float(lap_df["Brake"])
    drs = pd.to_numeric(lap_df["DRS"], errors="coerce") if "DRS" in lap_df.columns else pd.Series(np.nan, index=lap_df.index)

    throttle_zero = throttle <= 0.0
    throttle_full = throttle >= 99.0
    throttle_mid = (throttle > 0.0) & (throttle < 99.0)
    brake_active = brake >= 0.5

    speed_diff = speed.diff()
    throttle_diff = throttle.diff()
    rpm_diff = rpm.diff()
    gear_diff = gear.diff()

    return {
        "n_samples": len(lap_df),
        "speed_mean": speed.mean(),
        "speed_std": speed.std(),
        "speed_min": speed.min(),
        "speed_max": speed.max(),
        "speed_q10": speed.quantile(0.10),
        "speed_q50": speed.quantile(0.50),
        "speed_q90": speed.quantile(0.90),
        "speed_range": speed.max() - speed.min(),
        "throttle_mean": throttle.mean(),
        "throttle_std": throttle.std(),
        "throttle_min": throttle.min(),
        "throttle_max": throttle.max(),
        "throttle_zero_frac": safe_frac(throttle_zero),
        "throttle_full_frac": safe_frac(throttle_full),
        "throttle_mid_frac": safe_frac(throttle_mid),
        "brake_mean": brake.mean(),
        "brake_std": brake.std(),
        "brake_min": brake.min(),
        "brake_max": brake.max(),
        "brake_active_frac": safe_frac(brake_active),
        "brake_on_count": count_state_changes(brake_active) // 2 + int(brake_active.iloc[0]) if len(brake_active) else 0,
        "first_brake_frac_pos": first_true_frac_pos(brake_active),
        "last_brake_frac_pos": last_true_frac_pos(brake_active),
        "rpm_mean": rpm.mean(),
        "rpm_std": rpm.std(),
        "rpm_min": rpm.min(),
        "rpm_max": rpm.max(),
        "gear_mean": gear.mean(),
        "gear_std": gear.std(),
        "gear_min": gear.min(),
        "gear_max": gear.max(),
        "gear_change_count": int(gear_diff.fillna(0).ne(0).sum()),
        "speed_diff_mean": speed_diff.mean(),
        "speed_diff_std": speed_diff.std(),
        "speed_diff_abs_mean": speed_diff.abs().mean(),
        "throttle_diff_mean": throttle_diff.mean(),
        "throttle_diff_std": throttle_diff.std(),
        "throttle_diff_abs_mean": throttle_diff.abs().mean(),
        "rpm_diff_mean": rpm_diff.mean(),
        "rpm_diff_std": rpm_diff.std(),
        "rpm_diff_abs_mean": rpm_diff.abs().mean(),
        "drs_active_frac": safe_frac(drs > 0),
    }


def build_features() -> pd.DataFrame:
    if not TELEMETRY_PATH.exists():
        raise FileNotFoundError(TELEMETRY_PATH)
    telemetry = pd.read_csv(TELEMETRY_PATH, low_memory=False)
    rows = []
    for lap_key, lap_df in telemetry.groupby("lap_key", sort=True):
        meta = lap_df.iloc[0]
        row = build_features_for_lap(lap_df)
        row.update(
            {
                "lap_key": lap_key,
                "Driver": meta["Driver"],
                "season": int(meta["season"]),
                "round": int(meta["round"]),
                "LapNumber": meta["LapNumber"],
                "LapTimeSeconds": meta.get("LapTimeSeconds"),
                "Sector1TimeSeconds": meta.get("Sector1TimeSeconds"),
                "Sector2TimeSeconds": meta.get("Sector2TimeSeconds"),
                "Sector3TimeSeconds": meta.get("Sector3TimeSeconds"),
                "Compound": meta.get("Compound"),
                "TyreLife": meta.get("TyreLife"),
                "Team": meta.get("Team"),
                "session_key": meta.get("session_key"),
                "event_name": meta.get("event_name"),
                "analysis_team": meta.get("analysis_team"),
                "leader_driver": meta.get("leader_driver"),
            }
        )
        rows.append(row)
    features = pd.DataFrame(rows)
    export_csv(features, "red_bull_teammate_window_lap_features")
    return features


def build_leader_teammate_pairs(features: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for team, leader in TEAM_LEADERS.items():
        team_df = features[features["analysis_team"] == team].copy()
        for session_key, session_df in team_df.groupby("session_key"):
            leader_rows = session_df[session_df["Driver"] == leader]
            mate_rows = session_df[session_df["Driver"] != leader]
            if leader_rows.empty or mate_rows.empty:
                continue
            leader_row = leader_rows.sort_values("LapTimeSeconds").iloc[0]
            for _, mate_row in mate_rows.iterrows():
                row = {
                    "team": team,
                    "leader_driver": leader,
                    "teammate_driver": mate_row["Driver"],
                    "season": int(leader_row["season"]),
                    "round": int(leader_row["round"]),
                    "session_key": session_key,
                    "event_name": leader_row["event_name"],
                    "leader_lap_key": leader_row["lap_key"],
                    "teammate_lap_key": mate_row["lap_key"],
                }
                for feature in STYLE_FEATURES:
                    row[f"{feature}_leader"] = leader_row[feature]
                    row[f"{feature}_teammate"] = mate_row[feature]
                    row[f"{feature}_leader_minus_teammate"] = leader_row[feature] - mate_row[feature]
                    row[f"{feature}_abs_gap"] = abs(leader_row[feature] - mate_row[feature])
                rows.append(row)
    pair_df = pd.DataFrame(rows)
    export_csv(pair_df, "red_bull_verstappen_teammate_pairs")
    return pair_df


def summarize_pairs(pair_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    season_rows = []
    for keys, group in pair_df.groupby(["team", "leader_driver", "teammate_driver", "season"]):
        row = dict(zip(["team", "leader_driver", "teammate_driver", "season"], keys))
        row["n_shared_sessions"] = len(group)
        for feature in PROXY_FEATURES:
            row[f"mean_{feature}_leader_minus_teammate"] = group[f"{feature}_leader_minus_teammate"].mean()
            row[f"mean_{feature}_abs_gap"] = group[f"{feature}_abs_gap"].mean()
        season_rows.append(row)
    season_summary = pd.DataFrame(season_rows)

    overall_rows = []
    for keys, group in pair_df.groupby(["team", "leader_driver", "teammate_driver"]):
        row = dict(zip(["team", "leader_driver", "teammate_driver"], keys))
        row["n_shared_sessions"] = len(group)
        row["first_season"] = int(group["season"].min())
        row["last_season"] = int(group["season"].max())
        for feature in PROXY_FEATURES:
            row[f"mean_{feature}_leader_minus_teammate"] = group[f"{feature}_leader_minus_teammate"].mean()
            row[f"mean_{feature}_abs_gap"] = group[f"{feature}_abs_gap"].mean()
        overall_rows.append(row)
    overall_summary = pd.DataFrame(overall_rows).sort_values(["team", "n_shared_sessions"], ascending=[True, False])

    long_rows = []
    for _, row in pair_df.iterrows():
        for feature in PROXY_FEATURES:
            long_rows.append(
                {
                    "team": row["team"],
                    "leader_driver": row["leader_driver"],
                    "teammate_driver": row["teammate_driver"],
                    "season": row["season"],
                    "round": row["round"],
                    "session_key": row["session_key"],
                    "event_name": row["event_name"],
                    "feature": feature,
                    "leader_minus_teammate": row[f"{feature}_leader_minus_teammate"],
                    "abs_gap": row[f"{feature}_abs_gap"],
                }
            )
    long_df = pd.DataFrame(long_rows)
    export_csv(season_summary, "red_bull_verstappen_teammate_season_summary")
    export_csv(overall_summary, "red_bull_verstappen_teammate_overall_summary")
    export_csv(long_df, "red_bull_verstappen_teammate_long_feature_gaps")
    return season_summary, overall_summary, long_df


def add_standardized_gaps(pair_df: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
    scale = {}
    for feature in PROXY_FEATURES:
        std = features[feature].std(skipna=True)
        scale[feature] = std if np.isfinite(std) and std > 0 else 1.0

    rows = []
    for _, row in pair_df.iterrows():
        out = {
            "team": row["team"],
            "leader_driver": row["leader_driver"],
            "teammate_driver": row["teammate_driver"],
            "season": row["season"],
            "round": row["round"],
            "session_key": row["session_key"],
            "event_name": row["event_name"],
        }
        abs_components = []
        signed_components = []
        for feature in PROXY_FEATURES:
            signed = row[f"{feature}_leader_minus_teammate"] / scale[feature]
            abs_val = abs(signed)
            out[f"{feature}_std_signed_gap"] = signed
            out[f"{feature}_std_abs_gap"] = abs_val
            abs_components.append(abs_val)
            signed_components.append(signed)
        out["mean_style_distance_proxy"] = float(np.mean(abs_components))
        out["mean_signed_proxy"] = float(np.mean(signed_components))
        rows.append(out)
    std_gap = pd.DataFrame(rows)
    export_csv(std_gap, "red_bull_verstappen_teammate_standardized_gaps")
    return std_gap


def plot_red_bull_lap_gap(pair_df: pd.DataFrame) -> Path:
    rb = pair_df[pair_df["team"] == "Red Bull Racing"].copy()
    rb["lap_gap_teammate_minus_ver"] = -rb["LapTimeSeconds_leader_minus_teammate"]
    plt.figure(figsize=(12, 5.5))
    ax = sns.boxplot(data=rb, x="season", y="lap_gap_teammate_minus_ver", color="#4c78a8")
    sns.stripplot(data=rb, x="season", y="lap_gap_teammate_minus_ver", hue="teammate_driver", dodge=True, ax=ax)
    ax.axhline(0, color="black", linewidth=1)
    ax.set_title("Red Bull: strata partnera zespołowego do Verstappena")
    ax.set_xlabel("Sezon")
    ax.set_ylabel("Różnica czasu okrążenia [s]\npartner - VER")
    ax.legend(title="Partner", ncols=4, fontsize=9)
    return savefig("13_red_bull_verstappen_teammate_lap_gap.png")


def plot_red_bull_proxy_trends(pair_df: pd.DataFrame) -> Path:
    rb = pair_df[pair_df["team"] == "Red Bull Racing"].copy()
    metrics = {
        "speed_min_leader_minus_teammate": "Min. prędkość\nVER - partner",
        "throttle_full_frac_leader_minus_teammate": "Full throttle\nVER - partner",
        "throttle_diff_abs_mean_leader_minus_teammate": "Dynamika gazu\nVER - partner",
        "brake_active_frac_leader_minus_teammate": "Aktywne hamowanie\nVER - partner",
    }
    long_rows = []
    for raw, label in metrics.items():
        for _, row in rb.iterrows():
            long_rows.append({"season": row["season"], "metric": label, "value": row[raw]})
    plot_df = pd.DataFrame(long_rows)

    g = sns.catplot(
        data=plot_df,
        x="season",
        y="value",
        col="metric",
        kind="box",
        col_wrap=2,
        sharey=False,
        height=4,
        aspect=1.35,
        color="#f28e2b",
    )
    g.fig.suptitle("Red Bull: proxy-różnice stylu Verstappen vs partner", y=1.03)
    for ax in g.axes.flatten():
        ax.axhline(0, color="black", linewidth=1)
        ax.set_xlabel("Sezon")
        ax.set_ylabel("VER - partner")
    return savefig("14_red_bull_verstappen_proxy_trends.png")


def plot_team_style_distance(std_gap_df: pd.DataFrame) -> Path:
    plt.figure(figsize=(11, 5.5))
    ax = sns.boxplot(data=std_gap_df, x="team", y="mean_style_distance_proxy", color="#59a14f")
    sns.stripplot(data=std_gap_df, x="team", y="mean_style_distance_proxy", hue="teammate_driver", dodge=True, ax=ax)
    ax.set_title("Odległość stylu lider-partner w tych samych sesjach")
    ax.set_xlabel("")
    ax.set_ylabel("Średnia standaryzowana różnica cech")
    ax.legend(title="Partner", ncols=4, fontsize=9)
    return savefig("15_team_leader_teammate_style_distance.png")


def write_notes(pair_df: pd.DataFrame, overall: pd.DataFrame, std_gap_df: pd.DataFrame) -> Path:
    rb_overall = overall[overall["team"] == "Red Bull Racing"].copy()
    team_distance = (
        std_gap_df.groupby("team", as_index=False)
        .agg(
            n_shared_sessions=("session_key", "count"),
            mean_style_distance_proxy=("mean_style_distance_proxy", "mean"),
            median_style_distance_proxy=("mean_style_distance_proxy", "median"),
        )
        .sort_values("mean_style_distance_proxy", ascending=False)
    )

    lines = [
        "# Red Bull / Verstappen teammate mini-experiment",
        "",
        "## Cel",
        "",
        "Mini-eksperyment sprawdza proxy hipotezy o dopasowaniu kierowca-samochod dla Red Bulla i Verstappena.",
        "Nie dowodzi, ze samochod byl projektowany pod konkretnego kierowce, bo nie mamy danych setupowych ani steering angle.",
        "",
        "## Pokrycie Red Bulla",
        "",
    ]
    for _, row in rb_overall.iterrows():
        lines.append(
            f"- VER vs {row['teammate_driver']}: {int(row['n_shared_sessions'])} wspolnych sesji, "
            f"sezony {int(row['first_season'])}-{int(row['last_season'])}."
        )

    lines.extend(["", "## Srednia odleglosc stylu lider-partner", ""])
    for _, row in team_distance.iterrows():
        lines.append(
            f"- {row['team']}: mean={row['mean_style_distance_proxy']:.3f}, "
            f"median={row['median_style_distance_proxy']:.3f}, n={int(row['n_shared_sessions'])}."
        )

    rb_lap = pair_df[pair_df["team"] == "Red Bull Racing"].copy()
    rb_lap["teammate_minus_ver_lap_time"] = -rb_lap["LapTimeSeconds_leader_minus_teammate"]
    lines.extend(["", "## Red Bull: czas okrazenia", ""])
    by_mate = (
        rb_lap.groupby("teammate_driver", as_index=False)
        .agg(n=("session_key", "count"), mean_gap=("teammate_minus_ver_lap_time", "mean"), median_gap=("teammate_minus_ver_lap_time", "median"))
        .sort_values("n", ascending=False)
    )
    for _, row in by_mate.iterrows():
        lines.append(
            f"- {row['teammate_driver']}: partner - VER mean={row['mean_gap']:.3f}s, "
            f"median={row['median_gap']:.3f}s, n={int(row['n'])}."
        )

    key_features = ["speed_min", "speed_mean", "throttle_full_frac", "throttle_mid_frac", "throttle_diff_abs_mean", "brake_active_frac", "gear_change_count"]
    lines.extend(["", "## Red Bull: proxy cech", ""])
    for feature in key_features:
        col = f"{feature}_leader_minus_teammate"
        lines.append(f"- {feature}: VER - partner mean={rb_lap[col].mean():.4f}, median={rb_lap[col].median():.4f}.")

    lines.extend(
        [
            "",
            "## Interpretacja ostrozna",
            "",
            "- Wyniki moga wspierac dyskusje o dopasowaniu kierowca-samochod, ale nie sa dowodem na ustawienia samochodu pod Verstappena.",
            "- Najsilniejszy material probkowy dotyczy pary VER-PER w latach 2021-2024.",
            "- W pracy glownej najlepiej traktowac to jako case study albo future work.",
        ]
    )

    path = Path("VERSTAPPEN_RED_BULL_WINDOW_RESULTS_PL.md")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams["font.family"] = "DejaVu Sans"

    targets = build_targets()
    extract_telemetry(targets)
    features = build_features()
    pair_df = build_leader_teammate_pairs(features)
    _, overall_summary, _ = summarize_pairs(pair_df)
    std_gap_df = add_standardized_gaps(pair_df, features)

    paths = [
        plot_red_bull_lap_gap(pair_df),
        plot_red_bull_proxy_trends(pair_df),
        plot_team_style_distance(std_gap_df),
    ]
    notes = write_notes(pair_df, overall_summary, std_gap_df)

    log("Red Bull teammate mini-experiment complete.")
    print(overall_summary.to_string(index=False))
    print("Figures:")
    for path in paths:
        print(f"- {path}")
    print(f"Notes: {notes}")


if __name__ == "__main__":
    main()
