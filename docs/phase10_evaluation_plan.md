# Phase 10: Evaluation Plan

## Objective
Evaluate the WASTESENSE ML workflow using reproducible metrics, suitable baselines, and explicit limitations.

## Step 1: Evaluation Scope and Metrics
- Regression models: MAE, RMSE, R-squared, and baseline comparison.
- Waste detection: precision, recall, F1, and confusion matrix when trustworthy ground-truth labels are available.
- Persistence: verify expected behavior on controlled temporal sequences.
- Root-cause intelligence: assess output validity and ensure hypotheses are not presented as confirmed causes.
- Recommendations: assess rule correctness, input validation, deterministic output, and human-review safeguards.
- Savings and replay: assess numerical consistency and distinguish hypothetical reductions from realized savings.

## Step 2: Resource Prediction Evaluation
Evaluate CPU, memory, and power models on an appropriate held-out test set. Preserve chronological separation for time-dependent observations and compare against a simple baseline. Report sample counts and limitations.

## Step 3: Waste Detection and Intelligence Evaluation
Evaluate against labelled cases when available. Otherwise, report controlled-case tests separately from real-world detection performance. Do not invent ground-truth labels.

## Step 4: Recommendations and Savings/Replay Evaluation
Evaluate recommendation rules, input validation, and consistency with savings estimation and replay outputs. Do not interpret potential or hypothetical reductions as realized savings.

## Step 5: Consolidated Results
Produce a reproducible results summary with metrics, sample sizes, baselines, test outcomes, limitations, and unresolved issues.

## Step 6: Documentation and Handoff
Document results and limitations, run the required evaluation tests, and record the final phase status.

## Evaluation Principles
- Do not modify earlier phases without a concrete defect or evaluation-supported need.
- Do not silently change existing data, models, or artifacts.
- Do not claim performance improvements without measured evidence.
- Do not claim production readiness or guaranteed savings from test results alone.
- Preserve unrelated and untracked repository files.
