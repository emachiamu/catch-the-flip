# Context for Summarizing Detector Experiments

## Goal and evaluation

The task is to rank Tier B heterodyne segments by the probability that a bit flip occurred. Each segment contains 400 time bins over 200 time units, with `I(t)`, `Q(t)`, a cat size `nbar ∈ {2.0, 2.5, 3.0, 3.5}`, and (in labelled splits) a flip label. The leaderboard ranks all cat sizes together, discards the 30% highest-risk segments, and scores the residual flip suppression at 70% yield:

`score = 1 - ρ₇₀`, where `ρ₇₀ = flip rate among kept segments / original flip rate`.

A useful score must therefore rank risk across cat sizes, not merely detect large dips. The validation set (`tierB_val`) has labels and was used for model development; the test set (`tierB_test`) is unlabelled and is used only for final predictions.

## Physical and data considerations that guided the experiments

- A flip produces a short **negative excursion in I**, lasting roughly 2–4 bins. With `Δt = 0.5`, the central expected width is about 3 bins (1.5 time units).
- The raw signal is strongly obscured by Gaussian white noise. Averaging adjacent bins suppresses uncorrelated noise while retaining a short burst.
- Cat size changes both the prior flip rate and the expected burst amplitude. The recorded validation flip rates were approximately 26.2%, 11.3%, 8.4%, and 4.35% for `nbar = 2.0, 2.5, 3.0, 3.5`, respectively. A raw dip score is therefore not directly comparable across cat sizes.
- The hidden device differs from the nominal simulator (finite buffer bandwidth and memory Kerr nonlinearity); training/calibrating on labelled hidden-device validation data performed better than transferring a nominal-device model.
- `Q` was investigated rather than assumed useless. The reported tests found no useful flip signal in it; see the rejected experiments below.

## Approaches tried and what was learned

### Simple baselines

| Approach | Reported `1 - ρ₇₀` | AUC | Interpretation |
|---|---:|---:|---|
| Whole-segment mean of `I` | 0.1272 | 0.5671 | Fails because a brief burst is diluted across 400 bins |
| Cat size alone (`-nbar`) | 0.3174 | 0.6665 | Captures different base flip rates, but has no segment-specific evidence |
| Raw 3-bin moving dip alone | 0.3540 | 0.6861 | Finds local bursts, but peak-only scoring is vulnerable to extreme noise spikes |

### Feature and model development

The detector evolved from a local dip score to a compact, physically motivated feature set and probabilistic calibration.

- **Multi-scale dips + global logistic regression:** reported score `0.5392`, AUC `0.7664`. Combining dip scales helped substantially, but a single global model did not fully handle the different signal and prior distributions across cat sizes.
- **Per-cat-size logistic calibration with multi-scale dip and excursion features (3-slice method):** reported score `0.5588` in one evaluation and `0.5563` in a later explicit 5-fold comparison (AUC `0.7691`). Separate models let each cat size learn its own relationship between burst evidence and flip probability.
- **Feature expansion to 21 parameters:** score fell from `0.5588` to `0.5246`. With only 586 positive flips in the validation sample, many correlated features increased overfitting.
- **Threshold/feature sweeps:** a single-threshold detector was weaker than combining three excursion thresholds. A reported out-of-fold comparison favoured thresholds `(2.0, 2.5, 3.0)` over alternatives such as `(1.8, 2.5, 3.0)`. The lower threshold can accumulate more background noise. The selected three levels encode the outer excursion, middle body, and deep core of a burst.

### Alternative model families and signal hypotheses

The following results were reported on the 5-fold benchmark:

| Alternative | `1 - ρ₇₀` | AUC | Finding |
|---|---:|---:|---|
| Richard-style histogram / likelihood-ratio model adapted to Tier B | 0.5490 | 0.7510 | Competitive, but weaker than the final feature-calibrated model |
| Histogram LLR (Richard's model; separate comparison) | 0.5490 | 0.7510 | Useful probabilistic baseline; less able to combine multiple continuous features |
| HistGradientBoosting / GBDT | 0.4978 | 0.7453 | Weaker generalization; hard partitions and rare positive examples were problematic |
| Gaussian matched filter (`σ = 1.2`) | 0.5514 | 0.7709 | Strong, but slightly below the boxcar multi-scale approach |
| Train on nominal data, transfer to hidden device | 0.5417 | 0.7711 | Device/domain shift reduced suppression |
| Rank ensemble (logistic regression + Richard model) | 0.5514 | 0.7630 | Did not improve on logistic calibration |
| Standardized features + logistic regression `C=5` | **0.5612** | 0.7681 (also reported as 0.7679) | Best reported out-of-fold suppression; selected |

Additional `Q`-quadrature tests, using the 3-slice model as reference (`0.5563` out-of-fold):

- **IQ phase rotation:** sweeping `Iφ = I cosφ + Q sinφ` found the best result at `φ = 0°` (`0.5563`). Non-zero rotation degraded performance (e.g. `−10°: 0.5344`, `+10°: 0.5197`).
- **Instantaneous power `I² + Q²`:** score fell to about `0.38`; squaring loses the sign of the negative dip and increases noise.
- **Q-based veto at the I-dip location:** score fell from `0.5563` to `0.5368`; reported I/Q correlation at the peak was only `0.023`.
- **Normalize I by `std(Q)`:** suppression was unchanged, while AUC fell from `0.7691` to `0.7662`; estimating noise from Q added estimation variability without useful information.

The conclusion from these experiments was to retain I and omit Q from the final detector.

## Selected final method: 5-fold ensemble of per-cat-size logistic models

The selected model is the **standardized, 5-fold stratified ensemble**, not the earlier single-fit/in-sample version.

### Feature extraction for each segment

1. Center each I trace by subtracting its own temporal mean: `I_c = I - mean(I)`. This removes small segment-wide offsets, including the documented numerical baseline shift.
2. Apply moving-average filters of widths 2, 3, and 4 bins: `s2`, `s3`, `s4`.
3. Extract seven features:
   - Dip depths: `d2 = -min(s2)`, `d3 = -min(s3)`, `d4 = -min(s4)`.
   - Three excursion areas from the 3-bin filtered trace: `aθ = Σ max(0, -s3(t) - θ)` for `θ ∈ {2.0, 2.5, 3.0}`.
   - Persistence: `nbel = count(s3(t) < -2.5)`.

The dip depths measure peak amplitude at different time scales. The three areas and persistence distinguish a sustained physical excursion from an isolated noise spike.

### Training and prediction

Use `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`. In each fold, and separately for each cat size:

- Fit `StandardScaler` on that fold's training subset only; transform its held-out fold and the test subset using the same scaler.
- Fit `LogisticRegression(C=5.0, max_iter=500, random_state=42)` on the training subset.
- Save predictions for the held-out validation fold as out-of-fold (OOF) scores.
- Add one fifth of that model's test probabilities to the test ensemble.

The five fold predictions are averaged: `p_test(i) = (1/5) Σₖ pₖ(i)`. The reported best OOF result is `1 - ρ₇₀ = 0.5612`, AUC approximately `0.768`, corresponding to full leaderboard points under the stated scoring scale.

Finally, choose the 70th percentile of test probabilities as the threshold and mark the highest-risk 30% for discard. Export the score and decision in `submission_template/tierB.csv`.

## Evaluation caveats to preserve

The conversation contains several score snapshots from different model versions and evaluation procedures. In particular, the 3-slice single-fit validation score around `0.5709` is **in-sample** (the same labelled validation records were used to fit and evaluate); it must not be compared as if it were an OOF result. The selected `0.5612` is the reported 5-fold OOF result. Small AUC differences (`0.7681` versus `0.7679`) also appear in separate reports; describe them as reported rounding/version differences rather than inventing a reconciliation.

Some earlier explanations call the classifier “Bayesian logistic regression.” The implementation described is standard L2-regularized `sklearn` logistic regression producing probabilities; no separate Bayesian inference procedure is specified. Avoid presenting it as a fully Bayesian model.

## Instructions for the AI that will write the evaluation summary

Produce a concise but complete narrative of the experimental progression: simple baselines → local/multi-scale signal features → cat-size-specific probabilistic calibration → feature/threshold refinement → alternative model and Q tests → final 5-fold ensemble.

For each experiment, state the hypothesis, what was changed, the reported validation metric, and what was learned. Keep in-sample and out-of-fold results clearly separate. Explain why the final method was retained: it had the best reported OOF suppression, used a compact physics-informed feature set, standardized features within each training fold, calibrated separately by cat size, and averaged five models for test inference.

Do not claim that every idea was exhaustively tested, do not invent missing scores, and do not treat physical intuition as proof of measured performance. Where the conversation gives conflicting snapshots or ambiguous metrics, explicitly flag that limitation.
