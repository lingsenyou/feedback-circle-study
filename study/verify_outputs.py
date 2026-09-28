"""Independently audit saved results without rerunning the learner."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np


def main():
    root = Path(__file__).resolve().parent
    out = root / "results"
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    cfg = json.loads((root / "config.json").read_text(encoding="utf-8"))
    with (out / "run_metrics.csv").open(encoding="utf-8", newline="") as f:
        runs = list(csv.DictReader(f))
    with (out / "world_metrics.csv").open(encoding="utf-8", newline="") as f:
        worlds = list(csv.DictReader(f))
    numeric = [k for k in runs[0] if k not in ["scenario", "condition"]]
    assert len(runs) == summary["actual_runs"] == 7200
    assert len(worlds) == 720
    assert all(np.isfinite(float(row[k])) for row in runs for k in numeric)
    run_lookup = {(r["scenario"], r["beta"], r["condition"], r["world"], r["seed"]): r for r in runs}
    assert len(run_lookup) == len(runs)
    residuals = []
    for row in runs:
        mean_risk = sum(float(row[f"g{g}_risk"]) for g in range(3)) / 3
        residuals.extend([
            abs(mean_risk - float(row["population_risk"])),
            abs(float(row["population_risk"]) - float(row["oracle_risk"]) - float(row["population_regret"])),
            abs(float(row["population_risk"]) - float(row["feedback_weighted_risk"]) - float(row["monitoring_gap"])),
        ])
        assert float(row["population_regret"]) >= 0
        if row["scenario"] == "no_conflict":
            assert abs(float(row["oracle_risk"]) - cfg["within_group_noise_halfwidth"] ** 2 / 3) < 1e-12
        if float(row["beta"]) == 0 and row["condition"] == "endogenous":
            other = run_lookup[(row["scenario"], row["beta"], "static", row["world"], row["seed"])]
            assert all(row[k] == other[k] for k in numeric)
    world_mean_residuals = []
    for row in worlds:
        matching = [run_lookup[(row["scenario"], row["beta"], row["condition"], row["world"], str(seed))] for seed in range(10)]
        for metric in row:
            if metric not in ["scenario", "beta", "condition", "world"]:
                world_mean_residuals.append(abs(float(row[metric]) - np.mean([float(r[metric]) for r in matching])))
    lookup_world = {(r["scenario"], r["beta"], r["condition"], r["world"]): r for r in worlds}
    differences = np.array([float(lookup_world[("main", "3.0", "endogenous", str(w))]["g0_risk"])
                            - float(lookup_world[("main", "3.0", "static", str(w))]["g0_risk"]) for w in range(20)])
    rng = np.random.default_rng(cfg["bootstrap_seed"])
    indices = rng.integers(0, 20, size=(cfg["bootstrap_resamples"], 20))
    interval = np.quantile(differences[indices].mean(axis=1), [0.025, 0.975])
    expected = summary["primary_result"]
    primary_error = max(abs(differences.mean() - expected["mean"]), abs(interval[0] - expected["ci95_low"]), abs(interval[1] - expected["ci95_high"]))
    replay = np.load(out / "replay_main_beta3_world0_seed0.npz")
    lr = cfg["learning_rate"]
    # Closed-form EMA reconstruction uses all stored feedback values, not the online update implementation.
    batch_means = replay["preferences"].mean(axis=1)
    T = len(batch_means)
    closed_form_final = (1 - lr) ** T * replay["actions_before"][0] + lr * np.sum((1 - lr) ** np.arange(T - 1, -1, -1) * batch_means)
    closed_form_error = abs(closed_form_final - replay["actions_after"][-1])
    hash_checks = {}
    for file, key in [("run_study.py", "code_sha256"), ("PROTOCOL.md", "protocol_sha256"), ("config.json", "config_sha256")]:
        hash_checks[file] = hashlib.sha256((root / file).read_bytes()).hexdigest() == summary[key]
    assert all(hash_checks.values())
    assert max(residuals + world_mean_residuals + [primary_error, closed_form_error]) < 1e-11
    report = {"status": "passed", "actual_run_rows": len(runs), "world_rows": len(worlds),
              "max_saved_metric_identity_error": max(residuals), "max_world_mean_error": max(world_mean_residuals),
              "primary_recalculation_error": float(primary_error), "closed_form_replay_error": float(closed_form_error),
              "pre_execution_hashes_still_match": hash_checks,
              "scope": "Independent audit of saved CSV/NPZ data, group aggregation, bootstrap interval, and closed-form replay."}
    (out / "independent_audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
