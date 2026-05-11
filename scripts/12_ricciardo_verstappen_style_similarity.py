from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler


EXPORT_DIR = Path("exports")
FIG_DIR = Path("figures") / "thesis"
FIG_DIR.mkdir(parents=True, exist_ok=True)

FEATURES_PATH = EXPORT_DIR / "red_bull_teammate_window_lap_features.csv"
PAIR_PATH = EXPORT_DIR / "red_bull_verstappen_teammate_pairs.csv"
STD_GAPS_PATH = EXPORT_DIR / "red_bull_verstappen_teammate_standardized_gaps.csv"

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

PACE_FEATURES = ["LapTimeSeconds"]


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


def load_features() -> pd.DataFrame:
    df = pd.read_csv(FEATURES_PATH)
    for col in STYLE_FEATURES + PACE_FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def session_normalized_features(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for session_key, group in df.groupby("session_key"):
        if len(group) < 2:
            continue
        out = group[["lap_key", "Driver", "Team", "season", "round", "session_key", "event_name", "analysis_team"]].copy()
        for feature in STYLE_FEATURES:
            mean = group[feature].mean()
            std = group[feature].std()
            if not np.isfinite(std) or std == 0:
                std = 1.0
            out[f"{feature}_session_z"] = (group[feature] - mean) / std
        rows.append(out)
    return pd.concat(rows, ignore_index=True)


def teammate_distance_rankings() -> pd.DataFrame:
    std = pd.read_csv(STD_GAPS_PATH)
    rb = std[std["team"] == "Red Bull Racing"].copy()
    summary = (
        rb.groupby("teammate_driver", as_index=False)
        .agg(
            n_shared_sessions=("session_key", "count"),
            mean_style_distance=("mean_style_distance_proxy", "mean"),
            median_style_distance=("mean_style_distance_proxy", "median"),
            q75_style_distance=("mean_style_distance_proxy", lambda s: s.quantile(0.75)),
        )
        .sort_values("median_style_distance")
    )
    export_csv(summary, "ricciardo_verstappen_red_bull_teammate_distance_ranking")
    return summary


def ricciardo_same_car_session_summary(pair_df: pd.DataFrame) -> pd.DataFrame:
    rb_ric = pair_df[(pair_df["team"] == "Red Bull Racing") & (pair_df["teammate_driver"] == "RIC")].copy()
    rb_ric["teammate_minus_ver_lap_time"] = -rb_ric["LapTimeSeconds_leader_minus_teammate"]
    cols = [
        "teammate_minus_ver_lap_time",
        "speed_min_leader_minus_teammate",
        "speed_mean_leader_minus_teammate",
        "throttle_full_frac_leader_minus_teammate",
        "throttle_mid_frac_leader_minus_teammate",
        "throttle_diff_abs_mean_leader_minus_teammate",
        "brake_active_frac_leader_minus_teammate",
        "gear_change_count_leader_minus_teammate",
    ]
    rows = []
    for col in cols:
        rows.append(
            {
                "metric": col,
                "mean": rb_ric[col].mean(),
                "median": rb_ric[col].median(),
                "std": rb_ric[col].std(),
                "n": len(rb_ric),
            }
        )
    summary = pd.DataFrame(rows)
    export_csv(summary, "ricciardo_verstappen_same_car_2018_summary")
    return summary


def build_driver_style_profiles(norm_df: pd.DataFrame) -> pd.DataFrame:
    z_cols = [f"{feature}_session_z" for feature in STYLE_FEATURES]
    profiles = (
        norm_df.groupby(["Driver", "Team"], as_index=False)
        .agg(
            n_laps=("lap_key", "count"),
            first_season=("season", "min"),
            last_season=("season", "max"),
            **{col: (col, "mean") for col in z_cols},
        )
    )
    export_csv(profiles, "ricciardo_verstappen_driver_style_profiles")
    return profiles


def profile_similarity(profiles: pd.DataFrame) -> pd.DataFrame:
    z_cols = [f"{feature}_session_z" for feature in STYLE_FEATURES]
    profile_matrix = profiles[z_cols].to_numpy(dtype=float)
    sim = cosine_similarity(profile_matrix)
    rows = []
    for i, row_i in profiles.iterrows():
        for j, row_j in profiles.iterrows():
            if i >= j:
                continue
            rows.append(
                {
                    "driver_a": row_i["Driver"],
                    "team_a": row_i["Team"],
                    "driver_b": row_j["Driver"],
                    "team_b": row_j["Team"],
                    "n_a": row_i["n_laps"],
                    "n_b": row_j["n_laps"],
                    "cosine_similarity": sim[i, j],
                    "cosine_distance": 1 - sim[i, j],
                }
            )
    result = pd.DataFrame(rows).sort_values("cosine_distance")
    export_csv(result, "ricciardo_verstappen_profile_similarity")
    return result


def pca_projection(norm_df: pd.DataFrame) -> pd.DataFrame:
    z_cols = [f"{feature}_session_z" for feature in STYLE_FEATURES]
    plot_df = norm_df.dropna(subset=z_cols).copy()
    scaler = StandardScaler()
    x = scaler.fit_transform(plot_df[z_cols])
    pca = PCA(n_components=2, random_state=42)
    comps = pca.fit_transform(x)
    plot_df["PC1"] = comps[:, 0]
    plot_df["PC2"] = comps[:, 1]
    plot_df["explained_var_pc1"] = pca.explained_variance_ratio_[0]
    plot_df["explained_var_pc2"] = pca.explained_variance_ratio_[1]
    export_csv(plot_df, "ricciardo_verstappen_style_pca_points")
    return plot_df


def plot_teammate_distance(summary: pd.DataFrame) -> Path:
    plt.figure(figsize=(10, 5.5))
    ax = sns.barplot(data=summary, x="teammate_driver", y="median_style_distance", color="#4c78a8")
    ax.set_title("Red Bull: podobieństwo stylu partnerów do Verstappena")
    ax.set_xlabel("Partner Verstappena")
    ax.set_ylabel("Mediana standaryzowanej odległości stylu")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.3f", fontsize=9)
    return savefig("16_red_bull_teammate_style_similarity_ranking.png")


def plot_pca(plot_df: pd.DataFrame) -> Path:
    subset = plot_df[
        ((plot_df["Team"] == "Red Bull Racing") & (plot_df["Driver"].isin(["VER", "RIC", "PER", "ALB", "GAS", "TSU"])))
        | ((plot_df["Driver"] == "RIC") & (plot_df["Team"].isin(["Renault", "McLaren", "AlphaTauri", "RB"])))
    ].copy()
    subset["label"] = subset["Driver"] + " / " + subset["Team"]
    plt.figure(figsize=(11, 7))
    ax = sns.scatterplot(
        data=subset,
        x="PC1",
        y="PC2",
        hue="label",
        style="Driver",
        s=75,
        alpha=0.85,
    )
    pc1 = plot_df["explained_var_pc1"].iloc[0] * 100
    pc2 = plot_df["explained_var_pc2"].iloc[0] * 100
    ax.set_title("Przestrzeń cech stylu: Ricciardo i Red Bull")
    ax.set_xlabel(f"PC1 ({pc1:.1f}% wariancji)")
    ax.set_ylabel(f"PC2 ({pc2:.1f}% wariancji)")
    ax.legend(title="", fontsize=8, bbox_to_anchor=(1.02, 1), loc="upper left")
    return savefig("17_ricciardo_verstappen_style_pca.png")


def plot_same_car_feature_gaps(pair_df: pd.DataFrame) -> Path:
    rb = pair_df[(pair_df["team"] == "Red Bull Racing") & (pair_df["teammate_driver"].isin(["RIC", "PER", "ALB", "GAS", "TSU"]))].copy()
    metrics = {
        "speed_min_leader_minus_teammate": "Min. prędkość",
        "speed_mean_leader_minus_teammate": "Średnia prędkość",
        "throttle_diff_abs_mean_leader_minus_teammate": "Dynamika gazu",
        "brake_active_frac_leader_minus_teammate": "Aktywne hamowanie",
    }
    rows = []
    for col, label in metrics.items():
        for _, row in rb.iterrows():
            rows.append({"teammate_driver": row["teammate_driver"], "metric": label, "value": row[col]})
    plot_df = pd.DataFrame(rows)
    g = sns.catplot(
        data=plot_df,
        x="teammate_driver",
        y="value",
        col="metric",
        kind="box",
        col_wrap=2,
        sharey=False,
        height=4,
        aspect=1.3,
        color="#f28e2b",
    )
    g.fig.suptitle("VER - partner: różnice cech w Red Bullu", y=1.03)
    for ax in g.axes.flatten():
        ax.axhline(0, color="black", linewidth=1)
        ax.set_xlabel("Partner")
        ax.set_ylabel("VER - partner")
    return savefig("18_red_bull_teammate_feature_gap_boxes.png")


def write_notes(distance_summary: pd.DataFrame, same_car_summary: pd.DataFrame, similarity: pd.DataFrame) -> Path:
    ric_row = distance_summary[distance_summary["teammate_driver"] == "RIC"].iloc[0]
    ric_sim = similarity[
        (
            (similarity["driver_a"] == "RIC")
            & (similarity["team_a"] == "Red Bull Racing")
            & (similarity["driver_b"] == "VER")
        )
        | (
            (similarity["driver_b"] == "RIC")
            & (similarity["team_b"] == "Red Bull Racing")
            & (similarity["driver_a"] == "VER")
        )
    ]

    lines = [
        "# Ricciardo vs Verstappen: analiza podobienstwa stylu",
        "",
        "## Pytanie",
        "",
        "Czy dane wspieraja popularna narracje, ze Daniel Ricciardo byl stylistycznie blizej Maxa Verstappena niz pozniejsi partnerzy Red Bulla?",
        "",
        "## Najczystszy test",
        "",
        "Najczystszy wariant to sezon 2018, czyli wspolne sesje Ricciardo i Verstappena w tym samym zespole i tym samym samochodzie.",
        f"Dostepne jest {int(ric_row['n_shared_sessions'])} wspolnych sesji VER-RIC w Red Bullu.",
        "",
        "## Ranking podobienstwa partnerow Red Bulla do Verstappena",
        "",
    ]
    for _, row in distance_summary.iterrows():
        lines.append(
            f"- {row['teammate_driver']}: mediana odleglosci stylu = {row['median_style_distance']:.3f}, "
            f"srednia = {row['mean_style_distance']:.3f}, n={int(row['n_shared_sessions'])}."
        )

    lines.extend(["", "## VER-RIC: cechy w tym samym samochodzie", ""])
    for _, row in same_car_summary.iterrows():
        lines.append(f"- {row['metric']}: mean={row['mean']:.4f}, median={row['median']:.4f}, n={int(row['n'])}.")

    lines.extend(["", "## Interpretacja", ""])
    lines.append(
        "- Ricciardo nie jest najblizszym partnerem Verstappena wedlug mediany prostej odleglosci stylu; blisko sa rowniez GAS i PER, ale probki sa nierowne."
    )
    lines.append(
        "- Jednoczesnie VER-RIC w 2018 ma bardzo mala mediane roznicy czasu okrazenia, co jest zgodne z narracja, ze Ricciardo najskuteczniej dotrzymywal tempa Verstappenowi."
    )
    lines.append(
        "- Wniosek powinien byc ostrozny: dane bardziej wspieraja teze o konkurencyjnym tempie Ricciardo w tym samym samochodzie niz jednoznaczna teze o identycznym stylu jazdy."
    )
    lines.append(
        "- Do mocniejszego wniosku o stylu potrzebne bylyby steering angle, dane setupowe albo porownanie zakret po zakrecie."
    )
    if not ric_sim.empty:
        row = ric_sim.iloc[0]
        lines.append(
            f"- Cosine similarity profilu RIC/Red Bull vs VER/Red Bull = {row['cosine_similarity']:.3f}; "
            "traktowac jako pomocnicze, bo profil oparty jest na agregatach cech."
        )

    path = Path("RICCIARDO_VERSTAPPEN_STYLE_SIMILARITY_RESULTS_PL.md")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams["font.family"] = "DejaVu Sans"

    features = load_features()
    norm_df = session_normalized_features(features)
    pair_df = pd.read_csv(PAIR_PATH)

    distance_summary = teammate_distance_rankings()
    same_car_summary = ricciardo_same_car_session_summary(pair_df)
    profiles = build_driver_style_profiles(norm_df)
    similarity = profile_similarity(profiles)
    pca_df = pca_projection(norm_df)

    paths = [
        plot_teammate_distance(distance_summary),
        plot_pca(pca_df),
        plot_same_car_feature_gaps(pair_df),
    ]
    notes = write_notes(distance_summary, same_car_summary, similarity)

    print("Ricciardo-Verstappen style similarity analysis complete.")
    print(distance_summary.to_string(index=False))
    print("Figures:")
    for path in paths:
        print(f"- {path}")
    print(f"Notes: {notes}")


if __name__ == "__main__":
    main()
