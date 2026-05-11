# Thesis Methods and Results Outline

This outline is based on the exported project results in `exports/` as of March 30, 2026.

## Methods Chapter Structure

### 1. Data Sources and Scope

Draft points:

- The study used Formula 1 telemetry obtained through FastF1.
- The analysis was restricted to qualifying sessions, because qualifying provides a cleaner setting for driving-style analysis than race laps.
- Only dry sessions were retained.
- The study initially covered the 2023-2025 seasons.

Numbers to cite:

- Raw qualifying laps: 22,465
- Dry qualifying laps after cleaning to `TrackStatus == 1`: 6,278
- Personal-best dry laps: 4,853
- Best laps successfully extracted with telemetry: 1,091

Main source table:

- `exports/thesis_table_pipeline_summary.csv`

### 2. Lap Selection and Quality Control

Draft points:

- The filtering pipeline removed laps with missing lap time and non-dry conditions.
- Additional quality restrictions included `IsAccurate == True` and `TrackStatus == '1'`.
- To reduce within-session duplication and to represent each driver by a single push lap, one best lap per driver per qualifying session was selected.

Methodological justification:

- This design reduces repeated near-duplicate laps from the same session.
- It also makes the comparison between drivers more defensible, because each observation corresponds to a representative qualifying effort.

### 3. Telemetry Representation

Draft points:

- Two representations were used.
- The first was a handcrafted lap-level feature representation.
- The second was a whole-lap sequence representation built from resampled telemetry.
- The sequence models used 300 normalized progress samples per lap and 5 telemetry channels: `Speed`, `Throttle`, `Brake`, `RPM`, and `nGear`.

Important limitation to mention:

- The current car-data and position-data merge was adequate for whole-lap modeling, but not precise enough for corner-level segmentation.

### 4. Handcrafted Feature Engineering

Draft points:

- Lap-level features summarized speed, throttle, brake, RPM, gear, and dynamics across the whole lap.
- Constant or near-constant variables were excluded from modeling.
- To reduce leakage, identifiers and clear timing variables were removed in the no-time experiments.
- Later ablations showed that dynamics and throttle-related feature families carried the strongest signal, while context and phase features were weak or slightly noisy.

### 5. Validation Design

Draft points:

- Initial baselines used stratified cross-validation.
- The stronger validation design used `StratifiedGroupKFold`, with one qualifying session treated as one group.
- This prevented train and test folds from sharing the same session context.

Why this matters:

- It tests whether the driver signal generalizes beyond a single event rather than exploiting session-specific conditions.

### 6. Model Families

Draft points:

- Handcrafted-feature baselines: logistic regression, random forest, HistGradientBoosting, and XGBoost.
- Final interpretable handcrafted model: logistic regression on the `distinctive_top5` subset with the `compact_no_context_no_phase` feature set.
- Sequence models: 1D CNN, GRU, LSTM.
- Hybrid model: CNN sequence branch combined with the compact handcrafted tabular branch.

## Results Chapter Structure

### 1. Broad 14-Driver Baseline

Draft wording:

> In the broad 14-driver setting, the strongest handcrafted baseline was logistic regression. In standard stratified cross-validation, the best no-time configuration achieved 0.6175 accuracy and 0.6160 macro F1. Under grouped session-level validation, the same general setup improved slightly to 0.6397 accuracy and 0.6392 macro F1. This showed that the telemetry feature space contained driver-specific information, but the 14-class problem remained challenging.

Main source tables:

- `exports/baseline_best_models.csv`
- `exports/grouped_best_models.csv`
- `exports/thesis_table_model_progression.csv`

### 2. Reduced Driver-Subset Experiments

Draft wording:

> The broad setting was followed by a data-driven subset selection step. Drivers were ranked by grouped per-class recall, and the `distinctive_top5` subset (`ALB`, `SAI`, `VER`, `OCO`, `LEC`) provided the cleanest focused setting. In this subset, the grouped handcrafted logistic model reached 0.8571 accuracy and 0.8581 macro F1, indicating that a reduced but more distinctive driver set substantially improves separability.

Main source tables:

- `exports/subset_grouped_summary.csv`
- `exports/thesis_table_model_progression.csv`

### 3. Final Handcrafted Model

Draft wording:

> Feature ablation and compact-model comparison led to a smaller final handcrafted model based on the `compact_no_context_no_phase` feature set. The final interpretable model achieved 0.8608 accuracy and 0.8617 macro F1. Its strongest signals were related to gear behavior, throttle dynamics, speed variability, and RPM dynamics rather than metadata or simple context variables.

Main source tables:

- `exports/final_model_config.csv`
- `exports/final_model_feature_importance_global.csv`
- `exports/final_results_model_comparison.csv`

### 4. Sequence and Hybrid Comparison

Draft wording:

> A whole-lap sequence baseline was then trained on resampled telemetry sequences. The 1D CNN improved over the final handcrafted model, reaching 0.8974 accuracy and 0.8952 macro F1. The best result was obtained with the hybrid CNN-plus-tabular model, which combined whole-lap sequence input with the compact handcrafted feature set and achieved 0.9158 accuracy and 0.9147 macro F1.

Draft wording on recurrent models:

> GRU and LSTM architectures were also evaluated, but they performed clearly worse in this setting. The GRU achieved 0.4945 accuracy and 0.4595 macro F1, while the LSTM achieved 0.3700 accuracy and 0.3365 macro F1. Therefore, recurrent models were not retained as the main sequence approach in the final comparison.

Main source tables:

- `exports/thesis_table_sequence_architecture_comparison.csv`
- `exports/final_results_model_comparison.csv`
- `exports/final_results_recommendation.csv`

### 5. Per-Driver Effects of the Hybrid Model

Draft wording:

> The hybrid model did not improve all drivers equally. The largest gain was observed for `ALB`, whose recall increased by 0.2000 relative to the handcrafted baseline, corresponding to an estimated reduction of 11 classification errors. Smaller but still meaningful recall gains were observed for `VER` (+0.0727) and `OCO` (+0.0370). `LEC` was the only driver for whom recall decreased slightly in the hybrid configuration (-0.0364).

Main source tables:

- `exports/thesis_table_hybrid_driver_gains.csv`
- `exports/final_results_per_driver_gain_vs_handcrafted.csv`

### 6. Confusion Patterns

Draft wording:

> The hybrid model substantially reduced several confusions that were prominent in the handcrafted model. For example, the `ALB -> SAI` confusion dropped from 5 cases to 0, and the `VER -> ALB` confusion dropped from 4 cases to 0. Some confusions remained, especially around `LEC` and `SAI`, but the overall error structure became cleaner in the hybrid model.

Main source tables:

- `exports/thesis_table_hybrid_confusion_reductions.csv`
- `exports/final_results_confusion_pair_gain_vs_handcrafted.csv`

### 7. Limitations

Draft points:

- The sequence models operated on whole-lap resampled telemetry rather than corner-segmented telemetry.
- Same-track analysis was explored, but under the current one-best-lap-per-session design it became too small to replace the main cross-track setup.
- The final focused comparison used a reduced driver set, so the strongest results should be interpreted as evidence of separability within that selected subset rather than for the entire grid.

## Recommended Thesis Tables

- Pipeline summary: `exports/thesis_table_pipeline_summary.csv`
- Model progression from broad baseline to final hybrid: `exports/thesis_table_model_progression.csv`
- Sequence architecture comparison: `exports/thesis_table_sequence_architecture_comparison.csv`
- Driver-level hybrid gains: `exports/thesis_table_hybrid_driver_gains.csv`
- Key confusion reductions: `exports/thesis_table_hybrid_confusion_reductions.csv`

## Recommended Main Narrative

Suggested one-sentence summary:

> The results indicate that Formula 1 driver identity can be recovered from whole-lap qualifying telemetry, that compact handcrafted features already provide strong separability in a focused driver subset, and that the strongest performance is achieved when whole-lap sequence information is combined with handcrafted telemetry descriptors in a hybrid model.
