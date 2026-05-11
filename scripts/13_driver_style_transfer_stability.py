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
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler


EXPORT_DIR = Path("exports")
CACHE_DIR = Path("f1_cache")
FIG_DIR = Path("figures") / "thesis"
FIG_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_LAPS_PATH = EXPORT_DIR / "session_driver_best_laps_2018_2025_strict.csv"
TARGETS_PATH = EXPORT_DIR / "driver_style_transfer_targets.csv"
AUDIT_PATH = EXPORT_DIR / "driver_style_transfer_telemetry_audit.csv"
TELEMETRY_PATH = EXPORT_DIR / "driver_style_transfer_telemetry_merged.csv"
FEATURES_PATH = EXPORT_DIR / "driver_style_transfer_lap_features.csv"
LOG_PATH = EXPORT_DIR / "driver_style_transfer.log"

RATE_LIMIT_SLEEP_SECONDS = 3600
DRIVERS = ["RIC", "SAI", "HAM", "ALO", "BOT", "GAS", "OCO", "VET"]

STYLE_FEATURES = [
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
    "rpm_mean",
    "rpm_std",
    "rpm_diff_abs_mean",
    "gear_mean",
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
                log(f"{description}: rate limit on attempt {attempt}. Sleeping one hour before retry.")
                time.sleep(RATE_LIMIT_SLEEP_SECONDS)
                continue
            raise


def append_csv_rows(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    df = pd.DataFrame(rows)
    df.to_csv(path, mode="a", header=not path.exists(), index=False)


def append_df(path: Path, df: pd.DataFrame) -> None:
    if df.empty:
        return
    df.to_csv(path, mode="a", header=not path.exists(), index=False)


def build_targets() -> pd.DataFrame:
    laps = pd.read_csv(SOURCE_LAPS_PATH)
    targets = laps[laps["Driver"].isin(DRIVERS)].copy()
    targets = targets.sort_values(["season", "round", "Driver"]).reset_index(drop=True)
    export_csv(targets, "driver_style_transfer_targets")
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

                    for col in [
                        "LapTimeSeconds",
                        "Sector1TimeSeconds",
                        "Sector2TimeSeconds",
                        "Sector3TimeSeconds",
                        "Compound",
                        "TyreLife",
                        "Team",
                        "session_key",
                        "event_name",
                    ]:
                        car_data[col] = target.get(col)

                    pos_keep = [c for c in pos_data.columns if c in ["lap_key", "X", "Y", "Z", "Status", "pos_time_sec", "pos_session_time_sec"]]
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


def safe_frac(mask: pd.Series) -> float:
    return float(mask.mean()) if len(mask) else np.nan


def brake_to_float(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    mapped = series.astype(str).str.strip().str.lower().map({"true": 1.0, "false": 0.0})
    return numeric.fillna(mapped).fillna(0.0).astype(float)


def count_state_changes(mask: pd.Series) -> int:
    values = mask.astype(int).to_numpy()
    if len(values) <= 1:
        return 0
    return int(np.abs(np.diff(values)).sum())


def build_features_for_lap(lap_df: pd.DataFrame) -> dict:
    lap_df = lap_df.sort_values("sample_idx").reset_index(drop=True)
    speed = pd.to_numeric(lap_df["Speed"], errors="coerce")
    throttle = pd.to_numeric(lap_df["Throttle"], errors="coerce")
    rpm = pd.to_numeric(lap_df["RPM"], errors="coerce")
    gear = pd.to_numeric(lap_df["nGear"], errors="coerce")
    brake = brake_to_float(lap_df["Brake"])

    throttle_zero = throttle <= 0.0
    throttle_full = throttle >= 99.0
    throttle_mid = (throttle > 0.0) & (throttle < 99.0)
    brake_active = brake >= 0.5

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
        "brake_active_frac": safe_frac(brake_active),
        "brake_on_count": count_state_changes(brake_active) // 2 + int(brake_active.iloc[0]) if len(brake_active) else 0,
        "rpm_mean": rpm.mean(),
        "rpm_std": rpm.std(),
        "rpm_diff_abs_mean": rpm.diff().abs().mean(),
        "gear_mean": gear.mean(),
        "gear_std": gear.std(),
        "gear_change_count": int(gear.diff().fillna(0).ne(0).sum()),
        "speed_diff_abs_mean": speed.diff().abs().mean(),
        "throttle_diff_abs_mean": throttle.diff().abs().mean(),
    }


def build_features() -> pd.DataFrame:
    telemetry = pd.read_csv(TELEMETRY_PATH, low_memory=False)
    rows = []
    for lap_key, lap_df in telemetry.groupby("lap_key", sort=True):
        meta = lap_df.iloc[0]
        row = build_features_for_lap(lap_df)
        row.update(
            {
                "lap_key": lap_key,
                "Driver": meta["Driver"],
                "Team": meta["Team"],
                "season": int(meta["season"]),
                "round": int(meta["round"]),
                "session_key": meta["session_key"],
                "event_name": meta["event_name"],
                "LapTimeSeconds": meta["LapTimeSeconds"],
            }
        )
        rows.append(row)
    features = pd.DataFrame(rows)
    export_csv(features, "driver_style_transfer_lap_features")
    return features


def session_normalize(features: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for session_key, group in features.groupby("session_key"):
        if len(group) < 2:
            continue
        out = group[["lap_key", "Driver", "Team", "season", "round", "session_key", "event_name"]].copy()
        for feature in STYLE_FEATURES:
            mean = group[feature].mean()
            std = group[feature].std()
            if not np.isfinite(std) or std == 0:
                std = 1.0
            out[f"{feature}_session_z"] = (group[feature] - mean) / std
        rows.append(out)
    norm = pd.concat(rows, ignore_index=True)
    export_csv(norm, "driver_style_transfer_session_normalized_features")
    return norm


def build_profiles(norm: pd.DataFrame) -> pd.DataFrame:
    z_cols = [f"{feature}_session_z" for feature in STYLE_FEATURES]
    profiles = (
        norm.groupby(["Driver", "Team"], as_index=False)
        .agg(
            n_laps=("lap_key", "count"),
            first_season=("season", "min"),
            last_season=("season", "max"),
            **{col: (col, "mean") for col in z_cols},
        )
    )
    export_csv(profiles, "driver_style_transfer_profiles")
    return profiles


def profile_similarity(profiles: pd.DataFrame) -> pd.DataFrame:
    z_cols = [f"{feature}_session_z" for feature in STYLE_FEATURES]
    rows = []
    for driver, group in profiles.groupby("Driver"):
        if len(group) < 2:
            continue
        x = group[z_cols].to_numpy(dtype=float)
        sim = cosine_similarity(x)
        for i, row_i in group.reset_index(drop=True).iterrows():
            for j, row_j in group.reset_index(drop=True).iterrows():
                if i >= j:
                    continue
                rows.append(
                    {
                        "Driver": driver,
                        "team_a": row_i["Team"],
                        "team_b": row_j["Team"],
                        "n_a": row_i["n_laps"],
                        "n_b": row_j["n_laps"],
                        "first_season_a": row_i["first_season"],
                        "last_season_a": row_i["last_season"],
                        "first_season_b": row_j["first_season"],
                        "last_season_b": row_j["last_season"],
                        "cosine_similarity": sim[i, j],
                        "cosine_distance": 1 - sim[i, j],
                    }
                )
    out = pd.DataFrame(rows).sort_values(["Driver", "cosine_distance"])
    export_csv(out, "driver_style_transfer_profile_similarity")
    return out


def driver_stability_summary(similarity: pd.DataFrame) -> pd.DataFrame:
    summary = (
        similarity.groupby("Driver", as_index=False)
        .agg(
            n_team_pairs=("cosine_similarity", "count"),
            mean_similarity=("cosine_similarity", "mean"),
            median_similarity=("cosine_similarity", "median"),
            max_similarity=("cosine_similarity", "max"),
            mean_distance=("cosine_distance", "mean"),
            median_distance=("cosine_distance", "median"),
        )
        .sort_values("median_similarity", ascending=False)
    )
    export_csv(summary, "driver_style_transfer_stability_summary")
    return summary


def lap_level_nearest_profiles(norm: pd.DataFrame, profiles: pd.DataFrame) -> pd.DataFrame:
    z_cols = [f"{feature}_session_z" for feature in STYLE_FEATURES]
    profile_rows = profiles.reset_index(drop=True)
    profile_x = profile_rows[z_cols].to_numpy(dtype=float)
    rows = []
    for _, lap in norm.dropna(subset=z_cols).iterrows():
        own_profiles = profile_rows[(profile_rows["Driver"] == lap["Driver"]) & (profile_rows["Team"] != lap["Team"])]
        other_profiles = profile_rows[profile_rows["Driver"] != lap["Driver"]]
        if own_profiles.empty:
            continue
        lap_x = lap[z_cols].to_numpy(dtype=float).reshape(1, -1)
        own_sim = cosine_similarity(lap_x, own_profiles[z_cols].to_numpy(dtype=float))[0]
        other_sim = cosine_similarity(lap_x, other_profiles[z_cols].to_numpy(dtype=float))[0] if not other_profiles.empty else np.array([np.nan])
        rows.append(
            {
                "lap_key": lap["lap_key"],
                "Driver": lap["Driver"],
                "Team": lap["Team"],
                "season": lap["season"],
                "session_key": lap["session_key"],
                "best_own_other_team_similarity": np.nanmax(own_sim),
                "best_other_driver_similarity": np.nanmax(other_sim),
                "own_style_margin": np.nanmax(own_sim) - np.nanmax(other_sim),
            }
        )
    out = pd.DataFrame(rows)
    export_csv(out, "driver_style_transfer_lap_nearest_profile_margins")
    return out


def plot_stability_summary(summary: pd.DataFrame) -> Path:
    plt.figure(figsize=(10, 5.5))
    ax = sns.barplot(data=summary, x="Driver", y="median_similarity", color="#4c78a8")
    ax.set_title("Stabilność profilu stylu między zespołami")
    ax.set_xlabel("Kierowca")
    ax.set_ylabel("Mediana podobieństwa cosinusowego")
    ax.set_ylim(-1, 1)
    ax.axhline(0, color="black", linewidth=1)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", fontsize=9)
    return savefig("19_driver_style_transfer_stability_summary.png")


def plot_ricciardo_team_similarity(similarity: pd.DataFrame) -> Path:
    ric = similarity[similarity["Driver"] == "RIC"].copy()
    ric["team_pair"] = ric["team_a"] + " - " + ric["team_b"]
    ric = ric.sort_values("cosine_similarity", ascending=False)
    plt.figure(figsize=(11, 6))
    ax = sns.barplot(data=ric, y="team_pair", x="cosine_similarity", color="#f28e2b")
    ax.set_title("Ricciardo: podobieństwo profilu stylu między zespołami")
    ax.set_xlabel("Podobieństwo cosinusowe")
    ax.set_ylabel("")
    ax.set_xlim(-1, 1)
    ax.axvline(0, color="black", linewidth=1)
    return savefig("20_ricciardo_style_transfer_team_pairs.png")


def plot_lap_profile_margin(margins: pd.DataFrame) -> Path:
    plt.figure(figsize=(11, 5.5))
    ax = sns.boxplot(data=margins, x="Driver", y="own_style_margin", color="#59a14f")
    sns.stripplot(data=margins, x="Driver", y="own_style_margin", color="black", alpha=0.25, ax=ax)
    ax.axhline(0, color="black", linewidth=1)
    ax.set_title("Czy okrążenie przypomina własny styl z innego zespołu?")
    ax.set_xlabel("Kierowca")
    ax.set_ylabel("Przewaga podobieństwa do własnego profilu\nnad najbliższym innym kierowcą")
    return savefig("21_driver_style_transfer_lap_profile_margin.png")


def write_notes(summary: pd.DataFrame, similarity: pd.DataFrame, margins: pd.DataFrame) -> Path:
    ric_summary = summary[summary["Driver"] == "RIC"].iloc[0]
    ric_pairs = similarity[similarity["Driver"] == "RIC"].sort_values("cosine_similarity", ascending=False)
    ric_margin = margins[margins["Driver"] == "RIC"]["own_style_margin"]

    lines = [
        "# Stabilnosc stylu kierowcy po zmianie zespolu",
        "",
        "## Pytanie",
        "",
        "Czy kierowca zachowuje rozpoznawalny profil stylu mimo zmiany samochodu i zespolu?",
        "",
        "## Metoda",
        "",
        "- uzyto czystych reprezentatywnych okrazen kwalifikacyjnych 2018-2025,",
        "- cechy byly normalizowane wzgledem sesji, zeby ograniczyc wplyw toru i warunkow,",
        "- porownano profile kierowca-zespol dla kierowcow, ktorzy zmieniali zespoly.",
        "",
        "## Ricciardo",
        "",
        f"- liczba par zespolow Ricciardo: {int(ric_summary['n_team_pairs'])},",
        f"- mediana podobienstwa miedzy profilami zespolow: {ric_summary['median_similarity']:.3f},",
        f"- srednia podobienstwa: {ric_summary['mean_similarity']:.3f},",
        f"- mediana marginesu lap-level: {ric_margin.median():.3f}.",
        "",
        "Najbardziej podobne pary zespolow Ricciardo:",
    ]
    for _, row in ric_pairs.head(8).iterrows():
        lines.append(f"- {row['team_a']} vs {row['team_b']}: similarity={row['cosine_similarity']:.3f}.")

    lines.extend(["", "## Porownanie z innymi kierowcami", ""])
    for _, row in summary.iterrows():
        lines.append(
            f"- {row['Driver']}: median similarity={row['median_similarity']:.3f}, "
            f"mean={row['mean_similarity']:.3f}, n_pairs={int(row['n_team_pairs'])}."
        )

    lines.extend(
        [
            "",
            "## Interpretacja",
            "",
            "- Stabilnosc stylu miedzy zespolami jest widoczna u czesci kierowcow, ale nie jest idealna, bo samochod i zespol mocno zmieniaja profil telemetrii.",
            "- Wynik Ricciardo nalezy interpretowac jako czesciowe wsparcie tezy, ze zachowywal pewne powtarzalne cechy stylu, ale nie jako dowod pelnej niezaleznosci stylu od samochodu.",
            "- Ten eksperyment dobrze pasuje do dyskusji o praktycznych zastosowaniach: analiza transferu kierowcy, dopasowania do auta i tego, ktore cechy stylu sa stabilne.",
        ]
    )
    path = Path("DRIVER_STYLE_TRANSFER_STABILITY_RESULTS_PL.md")
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
    norm = session_normalize(features)
    profiles = build_profiles(norm)
    similarity = profile_similarity(profiles)
    summary = driver_stability_summary(similarity)
    margins = lap_level_nearest_profiles(norm, profiles)

    paths = [
        plot_stability_summary(summary),
        plot_ricciardo_team_similarity(similarity),
        plot_lap_profile_margin(margins),
    ]
    notes = write_notes(summary, similarity, margins)

    print("Driver style transfer stability analysis complete.")
    print(summary.to_string(index=False))
    print("Figures:")
    for path in paths:
        print(f"- {path}")
    print(f"Notes: {notes}")


if __name__ == "__main__":
    main()
