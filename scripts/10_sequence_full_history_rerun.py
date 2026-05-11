from pathlib import Path
import gc
import os
import warnings

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import LabelEncoder


warnings.filterwarnings("ignore")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

EXPORT_DIR = Path("exports")
RANDOM_STATE = 42
N_SPLITS = 5
SEQ_LEN = 300
SEQ_CHANNELS = ["Speed", "Throttle", "Brake", "RPM", "nGear"]
BATCH_SIZE = 32

# These two setups were missing full per-epoch histories in the first run.
# The short-horizon setup already has full histories in sequence_architecture_training_history.csv.
RUN_SETUPS = [s.strip() for s in os.environ.get(
    "F1_RERUN_SETUPS",
    "long_qualifying_top5,race_2025_top5",
).split(",") if s.strip()]
MODEL_NAMES = [s.strip() for s in os.environ.get(
    "F1_RERUN_MODELS",
    "cnn,hybrid_cnn_tabular,gru,lstm",
).split(",") if s.strip()]


def export_csv(df: pd.DataFrame, name: str) -> Path:
    path = EXPORT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    return path


def read_existing_export(name: str, model_names: list[str] | None = None) -> pd.DataFrame:
    path = EXPORT_DIR / f"{name}.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if model_names and "model" in df.columns:
        df = df[~df["model"].isin(model_names)].copy()
    return df


def convert_brake_column(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    mapped = series.astype(str).str.lower().map({"true": 1.0, "false": 0.0})
    return numeric.fillna(mapped).fillna(0.0).astype(float)


def resample_sequence(values: np.ndarray, target_len: int) -> np.ndarray:
    values = pd.Series(values).astype(float).interpolate(limit_direction="both").bfill().ffill()
    values = values.to_numpy(dtype=float)
    if len(values) == 0:
        return np.zeros(target_len, dtype=float)
    if len(values) == 1:
        return np.repeat(values[0], target_len)

    x_old = np.linspace(0.0, 1.0, len(values))
    x_new = np.linspace(0.0, 1.0, target_len)
    return np.interp(x_new, x_old, values)


def standardize_sequence(reference_x: np.ndarray, *arrays: np.ndarray) -> list[np.ndarray]:
    mean = reference_x.reshape(-1, reference_x.shape[-1]).mean(axis=0)
    std = reference_x.reshape(-1, reference_x.shape[-1]).std(axis=0)
    std = np.where(std > 0, std, 1.0)
    return [((arr - mean) / std).astype(np.float32) for arr in arrays]


def standardize_tabular(reference_x: np.ndarray, *arrays: np.ndarray) -> list[np.ndarray]:
    mean = np.nanmean(reference_x, axis=0)
    std = np.nanstd(reference_x, axis=0)
    mean = np.where(np.isfinite(mean), mean, 0.0)
    std = np.where((std > 0) & np.isfinite(std), std, 1.0)
    standardized = []
    for arr in arrays:
        out = (arr - mean) / std
        standardized.append(np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32))
    return standardized


def build_cnn_model(seq_len: int, n_channels: int, n_classes: int) -> tf.keras.Model:
    inp = tf.keras.Input(shape=(seq_len, n_channels), name="seq_input")
    x = tf.keras.layers.Conv1D(32, 7, padding="same", activation="relu")(inp)
    x = tf.keras.layers.Conv1D(32, 7, padding="same", activation="relu")(x)
    x = tf.keras.layers.MaxPooling1D(2)(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.Conv1D(64, 5, padding="same", activation="relu")(x)
    x = tf.keras.layers.Conv1D(64, 5, padding="same", activation="relu")(x)
    x = tf.keras.layers.GlobalAveragePooling1D()(x)
    x = tf.keras.layers.Dense(64, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    out = tf.keras.layers.Dense(n_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs=inp, outputs=out)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def build_hybrid_cnn_model(seq_len: int, n_channels: int, n_tab_features: int, n_classes: int) -> tf.keras.Model:
    seq_in = tf.keras.Input(shape=(seq_len, n_channels), name="seq_input")
    tab_in = tf.keras.Input(shape=(n_tab_features,), name="tab_input")

    x_seq = tf.keras.layers.Conv1D(32, 7, padding="same", activation="relu")(seq_in)
    x_seq = tf.keras.layers.Conv1D(32, 7, padding="same", activation="relu")(x_seq)
    x_seq = tf.keras.layers.MaxPooling1D(2)(x_seq)
    x_seq = tf.keras.layers.Dropout(0.2)(x_seq)
    x_seq = tf.keras.layers.Conv1D(64, 5, padding="same", activation="relu")(x_seq)
    x_seq = tf.keras.layers.GlobalAveragePooling1D()(x_seq)

    x_tab = tf.keras.layers.Dense(32, activation="relu")(tab_in)
    x_tab = tf.keras.layers.Dropout(0.2)(x_tab)

    x = tf.keras.layers.Concatenate()([x_seq, x_tab])
    x = tf.keras.layers.Dense(64, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    out = tf.keras.layers.Dense(n_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs=[seq_in, tab_in], outputs=out)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def build_gru_model(seq_len: int, n_channels: int, n_classes: int) -> tf.keras.Model:
    inp = tf.keras.Input(shape=(seq_len, n_channels), name="seq_input")
    x = tf.keras.layers.GRU(64, return_sequences=True, dropout=0.2)(inp)
    x = tf.keras.layers.GRU(32, dropout=0.2)(x)
    x = tf.keras.layers.Dense(64, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    out = tf.keras.layers.Dense(n_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs=inp, outputs=out)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def build_lstm_model(seq_len: int, n_channels: int, n_classes: int) -> tf.keras.Model:
    inp = tf.keras.Input(shape=(seq_len, n_channels), name="seq_input")
    x = tf.keras.layers.LSTM(64, return_sequences=True, dropout=0.2)(inp)
    x = tf.keras.layers.LSTM(32, dropout=0.2)(x)
    x = tf.keras.layers.Dense(64, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    out = tf.keras.layers.Dense(n_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs=inp, outputs=out)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def prepare_long_qualifying_top5() -> dict:
    telemetry_df = pd.read_csv(EXPORT_DIR / "balanced_top6_telemetry_merged_2018_2025_strict.csv", low_memory=False)
    features_df = pd.read_csv(EXPORT_DIR / "balanced_top5_lap_features_2018_2025_strict.csv")

    drivers = sorted(features_df["Driver"].unique().tolist())
    telemetry_df = telemetry_df[telemetry_df["Driver"].isin(drivers)].copy()
    telemetry_df["Brake"] = convert_brake_column(telemetry_df["Brake"])

    base_drop = [
        "lap_key", "Driver", "season", "round", "LapNumber",
        "Team", "event_name", "session_key", "Compound", "TyreLife",
        "throttle_min", "brake_min", "drs_active_frac",
    ]
    tab_features = [
        c for c in features_df.columns
        if c not in base_drop and pd.api.types.is_numeric_dtype(features_df[c]) and not features_df[c].isna().all()
    ]

    return make_sequence_bundle(
        setup_name="long_qualifying_top5",
        telemetry_df=telemetry_df,
        features_df=features_df,
        tab_features=tab_features,
        group_col="session_key",
        meta_cols=["lap_key", "Driver", "season", "round", "event_name", "session_key"],
        max_epochs=80,
        patience=10,
    )


def prepare_race_2025_top5() -> dict:
    telemetry_df = pd.read_csv(EXPORT_DIR / "race_2025_balanced_top5_telemetry_merged.csv", low_memory=False)
    features_df = pd.read_csv(EXPORT_DIR / "race_2025_balanced_top5_lap_features.csv")
    telemetry_df["Brake"] = convert_brake_column(telemetry_df["Brake"])

    base_drop = [
        "lap_key", "Driver", "season", "round", "event_name", "session_name", "LapNumber",
        "Team", "session_key", "TrackStatus", "lap_time_not_null", "dry_session", "accurate",
        "not_deleted", "not_fastf1_generated", "track_status_green", "not_pit_in_out",
        "within_2s_of_stint_median", "within_3s_of_stint_median", "throttle_min", "brake_min",
        "LapTimeSeconds", "stint_median_lap_seconds", "lap_time_delta_to_stint_median",
        "Compound", "TyreLife", "Stint", "SessionPart", "drs_active_frac",
    ]
    tab_features = [
        c for c in features_df.columns
        if c not in base_drop and pd.api.types.is_numeric_dtype(features_df[c]) and not features_df[c].isna().all()
    ]

    return make_sequence_bundle(
        setup_name="race_2025_top5",
        telemetry_df=telemetry_df,
        features_df=features_df,
        tab_features=tab_features,
        group_col="session_key",
        meta_cols=["lap_key", "Driver", "season", "round", "event_name", "session_key"],
        max_epochs=60,
        patience=8,
    )


def make_sequence_bundle(
    setup_name: str,
    telemetry_df: pd.DataFrame,
    features_df: pd.DataFrame,
    tab_features: list[str],
    group_col: str,
    meta_cols: list[str],
    max_epochs: int,
    patience: int,
) -> dict:
    lap_rows = []
    sequence_arrays = []

    for lap_key, lap_df in telemetry_df.sort_values(["lap_key", "sample_idx"]).groupby("lap_key"):
        lap_meta = lap_df.iloc[0]
        channel_matrix = []
        for channel in SEQ_CHANNELS:
            series = pd.to_numeric(lap_df[channel], errors="coerce")
            channel_matrix.append(resample_sequence(series.values, SEQ_LEN))
        sequence_arrays.append(np.stack(channel_matrix, axis=-1))

        row = {"lap_key": lap_key, "raw_len": len(lap_df)}
        for col in meta_cols:
            if col in lap_meta.index:
                row[col] = lap_meta[col]
        lap_rows.append(row)

    sequence_meta_df = pd.DataFrame(lap_rows)
    feature_cols = ["lap_key"] + tab_features
    meta_df = sequence_meta_df.merge(features_df[feature_cols], on="lap_key", how="inner")

    sequence_lookup = {row["lap_key"]: idx for idx, row in sequence_meta_df.reset_index(drop=True).iterrows()}
    aligned_indices = meta_df["lap_key"].map(sequence_lookup).to_numpy()
    X_seq = np.stack(sequence_arrays)[aligned_indices].astype(np.float32)
    X_tab = meta_df[tab_features].astype(float).to_numpy(dtype=np.float32)
    y_labels = meta_df["Driver"].astype(str).to_numpy()
    groups = meta_df[group_col].astype(str).to_numpy()

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_labels)

    return {
        "setup_name": setup_name,
        "tab_features": tab_features,
        "meta_df": meta_df,
        "X_seq": X_seq,
        "X_tab": X_tab,
        "y": y,
        "y_labels": y_labels,
        "groups": groups,
        "label_encoder": label_encoder,
        "max_epochs": max_epochs,
        "patience": patience,
    }


def get_model_builder(model_name: str, n_tab_features: int, n_classes: int):
    builders = {
        "cnn": lambda: build_cnn_model(SEQ_LEN, len(SEQ_CHANNELS), n_classes),
        "hybrid_cnn_tabular": lambda: build_hybrid_cnn_model(SEQ_LEN, len(SEQ_CHANNELS), n_tab_features, n_classes),
        "gru": lambda: build_gru_model(SEQ_LEN, len(SEQ_CHANNELS), n_classes),
        "lstm": lambda: build_lstm_model(SEQ_LEN, len(SEQ_CHANNELS), n_classes),
    }
    return builders[model_name]


def append_epoch_history(history_rows: list[dict], setup_name: str, model_name: str, fold: int, history) -> None:
    n_epochs = len(history.history["loss"])
    for epoch_idx in range(n_epochs):
        history_rows.append(
            {
                "setup": setup_name,
                "model": model_name,
                "fold": fold,
                "epoch": epoch_idx + 1,
                "loss": float(history.history["loss"][epoch_idx]),
                "val_loss": float(history.history["val_loss"][epoch_idx]),
                "accuracy": float(history.history["accuracy"][epoch_idx]),
                "val_accuracy": float(history.history["val_accuracy"][epoch_idx]),
            }
        )


def make_confusion_df(y_true: np.ndarray, y_pred: np.ndarray, labels: list[str], setup_name: str, model_name: str) -> pd.DataFrame:
    matrix = confusion_matrix(y_true, y_pred, labels=np.arange(len(labels)))
    rows = []
    for true_idx, true_label in enumerate(labels):
        for pred_idx, pred_label in enumerate(labels):
            rows.append(
                {
                    "setup": setup_name,
                    "model": model_name,
                    "true_driver": true_label,
                    "pred_driver": pred_label,
                    "count": int(matrix[true_idx, pred_idx]),
                }
            )
    return pd.DataFrame(rows)


def make_per_driver_df(y_true: np.ndarray, y_pred: np.ndarray, labels: list[str], setup_name: str, model_name: str) -> pd.DataFrame:
    report = classification_report(
        y_true,
        y_pred,
        labels=np.arange(len(labels)),
        target_names=labels,
        output_dict=True,
        zero_division=0,
    )
    rows = []
    for label in labels:
        rows.append(
            {
                "setup": setup_name,
                "model": model_name,
                "driver": label,
                "precision": report[label]["precision"],
                "recall": report[label]["recall"],
                "f1_score": report[label]["f1-score"],
                "support": report[label]["support"],
            }
        )
    return pd.DataFrame(rows)


def run_setup(bundle: dict) -> None:
    setup_name = bundle["setup_name"]
    X_seq = bundle["X_seq"]
    X_tab = bundle["X_tab"]
    y = bundle["y"]
    groups = bundle["groups"]
    meta_df = bundle["meta_df"].reset_index(drop=True)
    label_encoder = bundle["label_encoder"]
    labels = label_encoder.classes_.tolist()
    n_classes = len(labels)

    print(f"\n=== {setup_name}: {len(y)} laps, {n_classes} drivers, {len(np.unique(groups))} groups ===", flush=True)

    cv = StratifiedGroupKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    outer_splits = []
    for fold_idx, (train_idx, test_idx) in enumerate(cv.split(X_seq, y, groups), start=1):
        inner_cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE + fold_idx)
        train_inner_rel, val_rel = next(inner_cv.split(X_seq[train_idx], y[train_idx], groups[train_idx]))
        outer_splits.append(
            {
                "fold": fold_idx,
                "train_idx": train_idx,
                "train_inner_idx": train_idx[train_inner_rel],
                "val_idx": train_idx[val_rel],
                "test_idx": test_idx,
            }
        )

    export_prefix = f"{setup_name}_sequence_full_rerun"
    current_models = list(MODEL_NAMES)

    split_rows = [
        {
            "setup": setup_name,
            "fold": split["fold"],
            "n_train": len(split["train_idx"]),
            "n_train_inner": len(split["train_inner_idx"]),
            "n_val": len(split["val_idx"]),
            "n_test": len(split["test_idx"]),
        }
        for split in outer_splits
    ]

    fold_rows = read_existing_export(f"{export_prefix}_fold_metrics", current_models).to_dict("records")
    history_rows = read_existing_export(f"{export_prefix}_training_history", current_models).to_dict("records")
    summary_rows = read_existing_export(f"{export_prefix}_model_summary", current_models).to_dict("records")

    existing_oof = read_existing_export(f"{export_prefix}_oof_predictions", current_models)
    existing_confusion = read_existing_export(f"{export_prefix}_confusion_matrix", current_models)
    existing_per_driver = read_existing_export(f"{export_prefix}_per_driver_metrics", current_models)

    all_oof_rows = [] if existing_oof.empty else [existing_oof]
    all_confusion = [] if existing_confusion.empty else [existing_confusion]
    all_per_driver = [] if existing_per_driver.empty else [existing_per_driver]

    export_csv(pd.DataFrame(split_rows), f"{export_prefix}_split_summary")

    for model_name in MODEL_NAMES:
        print(f"--- Training {setup_name} / {model_name} ---", flush=True)
        builder = get_model_builder(model_name, X_tab.shape[1], n_classes)
        oof_pred = np.full(len(y), -1, dtype=int)
        fold_assignment = np.full(len(y), -1, dtype=int)

        for split in outer_splits:
            fold = split["fold"]
            train_idx = split["train_idx"]
            train_inner_idx = split["train_inner_idx"]
            val_idx = split["val_idx"]
            test_idx = split["test_idx"]

            seq_train_inner, seq_val, seq_test, seq_train_full = standardize_sequence(
                X_seq[train_inner_idx],
                X_seq[train_inner_idx],
                X_seq[val_idx],
                X_seq[test_idx],
                X_seq[train_idx],
            )
            tab_train_inner, tab_val, tab_test, tab_train_full = standardize_tabular(
                X_tab[train_inner_idx],
                X_tab[train_inner_idx],
                X_tab[val_idx],
                X_tab[test_idx],
                X_tab[train_idx],
            )

            callbacks = [
                tf.keras.callbacks.EarlyStopping(
                    monitor="val_loss",
                    patience=bundle["patience"],
                    restore_best_weights=True,
                )
            ]

            tf.keras.backend.clear_session()
            tf.keras.utils.set_random_seed(RANDOM_STATE + fold)
            model = builder()

            if model_name == "hybrid_cnn_tabular":
                history = model.fit(
                    [seq_train_inner, tab_train_inner],
                    y[train_inner_idx],
                    validation_data=([seq_val, tab_val], y[val_idx]),
                    epochs=bundle["max_epochs"],
                    batch_size=BATCH_SIZE,
                    verbose=0,
                    callbacks=callbacks,
                )
                train_pred = np.argmax(model.predict([seq_train_full, tab_train_full], verbose=0), axis=1)
                test_pred = np.argmax(model.predict([seq_test, tab_test], verbose=0), axis=1)
            else:
                history = model.fit(
                    seq_train_inner,
                    y[train_inner_idx],
                    validation_data=(seq_val, y[val_idx]),
                    epochs=bundle["max_epochs"],
                    batch_size=BATCH_SIZE,
                    verbose=0,
                    callbacks=callbacks,
                )
                train_pred = np.argmax(model.predict(seq_train_full, verbose=0), axis=1)
                test_pred = np.argmax(model.predict(seq_test, verbose=0), axis=1)

            oof_pred[test_idx] = test_pred
            fold_assignment[test_idx] = fold
            append_epoch_history(history_rows, setup_name, model_name, fold, history)

            fold_rows.append(
                {
                    "setup": setup_name,
                    "model": model_name,
                    "fold": fold,
                    "epochs_trained": len(history.history["loss"]),
                    "best_val_loss": float(np.min(history.history["val_loss"])),
                    "train_accuracy": accuracy_score(y[train_idx], train_pred),
                    "test_accuracy": accuracy_score(y[test_idx], test_pred),
                    "train_balanced_accuracy": balanced_accuracy_score(y[train_idx], train_pred),
                    "test_balanced_accuracy": balanced_accuracy_score(y[test_idx], test_pred),
                    "train_macro_f1": f1_score(y[train_idx], train_pred, average="macro"),
                    "test_macro_f1": f1_score(y[test_idx], test_pred, average="macro"),
                }
            )

            print(
                f"{setup_name} / {model_name} / fold {fold}: "
                f"epochs={len(history.history['loss'])}, "
                f"test_macro_f1={fold_rows[-1]['test_macro_f1']:.4f}",
                flush=True,
            )

            export_csv(pd.DataFrame(fold_rows), f"{export_prefix}_fold_metrics")
            export_csv(pd.DataFrame(history_rows), f"{export_prefix}_training_history")

            del model
            tf.keras.backend.clear_session()
            gc.collect()

        valid = oof_pred >= 0
        summary_rows.append(
            {
                "setup": setup_name,
                "model": model_name,
                "n_samples": int(valid.sum()),
                "n_drivers": n_classes,
                "n_groups": int(len(np.unique(groups))),
                "oof_accuracy": accuracy_score(y[valid], oof_pred[valid]),
                "oof_balanced_accuracy": balanced_accuracy_score(y[valid], oof_pred[valid]),
                "oof_macro_f1": f1_score(y[valid], oof_pred[valid], average="macro"),
            }
        )

        oof_meta = meta_df.loc[valid, [c for c in ["lap_key", "Driver", "season", "round", "event_name", "session_key"] if c in meta_df.columns]].copy()
        oof_meta["setup"] = setup_name
        oof_meta["model"] = model_name
        oof_meta["fold"] = fold_assignment[valid]
        oof_meta["true_driver"] = label_encoder.inverse_transform(y[valid])
        oof_meta["pred_driver"] = label_encoder.inverse_transform(oof_pred[valid])
        all_oof_rows.append(oof_meta)
        all_confusion.append(make_confusion_df(y[valid], oof_pred[valid], labels, setup_name, model_name))
        all_per_driver.append(make_per_driver_df(y[valid], oof_pred[valid], labels, setup_name, model_name))

        # Partial exports after each model protect us from losing a long overnight run.
        export_csv(pd.DataFrame(split_rows), f"{export_prefix}_split_summary")
        export_csv(pd.DataFrame(fold_rows), f"{export_prefix}_fold_metrics")
        export_csv(pd.DataFrame(history_rows), f"{export_prefix}_training_history")
        export_csv(pd.DataFrame(summary_rows), f"{export_prefix}_model_summary")
        export_csv(pd.concat(all_oof_rows, ignore_index=True), f"{export_prefix}_oof_predictions")
        export_csv(pd.concat(all_confusion, ignore_index=True), f"{export_prefix}_confusion_matrix")
        export_csv(pd.concat(all_per_driver, ignore_index=True), f"{export_prefix}_per_driver_metrics")

    summary_df = pd.DataFrame(summary_rows).sort_values(["oof_macro_f1", "oof_accuracy"], ascending=[False, False])
    export_csv(summary_df.head(1), f"{setup_name}_sequence_full_rerun_best_model")
    print(f"\nBest for {setup_name}:", flush=True)
    print(summary_df.head(1).to_string(index=False), flush=True)


def main() -> None:
    EXPORT_DIR.mkdir(exist_ok=True)
    tf.keras.utils.set_random_seed(RANDOM_STATE)

    setup_builders = {
        "long_qualifying_top5": prepare_long_qualifying_top5,
        "race_2025_top5": prepare_race_2025_top5,
    }

    for setup_name in RUN_SETUPS:
        bundle = setup_builders[setup_name]()
        run_setup(bundle)

    print("\nFull-history sequence rerun complete.", flush=True)


if __name__ == "__main__":
    main()
