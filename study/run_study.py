"""Reproducible synthetic feedback-selection mechanism study (NumPy only)."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


METRICS = [
    "g0_risk", "g1_risk", "g2_risk", "population_risk",
    "population_regret", "feedback_weighted_risk", "monitoring_gap",
    "sample_monitoring_gap", "g0_feedback_share", "g0_expected_feedback_share",
    "expected_invitations_per_accepted", "action",
]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path, rows, fields):
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def propensities(w, theta, friction, beta, cfg):
    variance = cfg["within_group_noise_halfwidth"] ** 2 / 3.0
    losses = (w[:, None] - theta) ** 2 + variance
    z = cfg["participation_intercept"] - friction[None, :] - beta * losses
    raw = cfg["participation_floor"] + cfg["participation_span"] / (1.0 + np.exp(-z))
    return raw, raw / raw.sum(axis=1, keepdims=True)


def bootstrap(values, indices):
    values = np.asarray(values, dtype=float)
    replicates = values[indices].mean(axis=1)
    low, high = np.quantile(replicates, [0.025, 0.975])
    return {"mean": float(values.mean()), "ci95_low": float(low), "ci95_high": float(high), "n_worlds": len(values)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results"))
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("config.json"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out / "summary.json").exists():
        raise SystemExit("Output already contains completed results; choose a new --output directory.")
    if cfg["batch_size"] % 3:
        raise ValueError("batch_size must be divisible by three for exact quotas")

    W, S, T, B = (cfg[k] for k in ["worlds", "paired_seeds_per_world", "rounds", "batch_size"])
    N = W * S
    variance = cfg["within_group_noise_halfwidth"] ** 2 / 3.0
    code_hash = sha256(__file__)
    provenance = {
        "study_version": cfg["study_version"],
        "recorded_before_main_execution_utc": datetime.now(timezone.utc).isoformat(),
        "record_type": "local pre-execution record, not public preregistration",
        "config_sha256": sha256(args.config),
        "protocol_sha256": sha256(root / "PROTOCOL.md"),
        "code_sha256": code_hash,
        "python": platform.python_version(), "numpy": np.__version__,
        "planned_runs": N * len(cfg["scenarios"]) * len(cfg["betas"]) * len(cfg["conditions"]),
        "config": cfg,
    }
    write_json(out / "execution_start.json", provenance)
    start = time.perf_counter()

    theta_world = np.asarray(cfg["theta_base"])[None, :] + np.random.default_rng(cfg["world_seed"]).uniform(
        -cfg["theta_jitter_halfwidth"], cfg["theta_jitter_halfwidth"], size=(W, 3))
    world_ids = np.repeat(np.arange(W), S)
    seed_ids = np.tile(np.arange(S), W)
    base_theta = np.repeat(theta_world, S, axis=0)
    draws = np.empty((N, T, B), dtype=float)
    noise = np.empty_like(draws)
    for n, (world, seed) in enumerate(zip(world_ids, seed_ids)):
        rng = np.random.default_rng(np.random.SeedSequence([cfg["training_seed"], int(world), int(seed)]))
        draws[n] = rng.random((T, B))
        noise[n] = rng.uniform(-cfg["within_group_noise_halfwidth"], cfg["within_group_noise_halfwidth"], size=(T, B))
    np.savez_compressed(out / "world_parameters.npz", theta=theta_world)
    row_index = np.arange(N)[:, None]
    quota_groups = np.broadcast_to(np.repeat(np.arange(3), B // 3)[None, :], (N, B))
    endpoint_arrays = {}
    world_arrays = {}
    run_rows, world_rows, trajectory_rows = [], [], []
    checks = {"status": "pending", "max_risk_decomposition_error": 0.0,
              "max_probability_sum_error": 0.0, "max_no_conflict_group_risk_difference": 0.0,
              "zero_beta_endogenous_static_max_endpoint_difference": 0.0,
              "quota_count_check": True, "replay_max_action_error": None,
              "ipw_expectation_max_error": 0.0}
    replay = {}
    condition_counter = 0

    for scenario in cfg["scenarios"]:
        theta = base_theta.copy()
        if scenario == "no_conflict":
            theta[:] = theta.mean(axis=1, keepdims=True)
        friction = np.zeros(3) if scenario == "symmetric" else np.array(cfg["friction"], dtype=float)
        oracle_action = theta.mean(axis=1)
        oracle_risk = ((theta - oracle_action[:, None]) ** 2).mean(axis=1) + variance
        for beta in cfg["betas"]:
            initial_raw, initial_probs = propensities(oracle_action, theta, friction, beta, cfg)
            for condition in cfg["conditions"]:
                w = oracle_action.copy()
                totals = np.zeros((N, len(METRICS)), dtype=float)
                key = (scenario, float(beta), condition)
                is_replay_case = scenario == "main" and beta == 3.0 and condition == "endogenous"
                if is_replay_case:
                    replay = {"groups": [], "preferences": [], "actions_before": [], "actions_after": [], "batch_estimates": []}
                for t in range(T):
                    raw, probabilities = propensities(w, theta, friction, beta, cfg)
                    if condition == "static":
                        raw, probabilities = initial_raw, initial_probs
                    if condition == "quota":
                        groups = quota_groups
                        sample_probs = np.full_like(probabilities, 1.0 / 3.0)
                        invitation_cost = (1.0 / raw).mean(axis=1)
                    else:
                        sample_probs = probabilities
                        cumulative = probabilities.cumsum(axis=1)
                        groups = ((draws[:, t, :] >= cumulative[:, 0, None]).astype(np.int8)
                                  + (draws[:, t, :] >= cumulative[:, 1, None]).astype(np.int8))
                        invitation_cost = 3.0 / raw.sum(axis=1)
                    checks["max_probability_sum_error"] = max(checks["max_probability_sum_error"], float(np.max(np.abs(sample_probs.sum(axis=1) - 1))))
                    y = theta[row_index, groups] + noise[:, t, :]
                    risk = (w[:, None] - theta) ** 2 + variance
                    pop_risk = risk.mean(axis=1)
                    regret = (w - oracle_action) ** 2
                    decomposition_error = np.max(np.abs(pop_risk - oracle_risk - regret))
                    checks["max_risk_decomposition_error"] = max(checks["max_risk_decomposition_error"], float(decomposition_error))
                    if scenario == "no_conflict":
                        checks["max_no_conflict_group_risk_difference"] = max(checks["max_no_conflict_group_risk_difference"], float(np.max(np.ptp(risk, axis=1))))
                    weighted_risk = (sample_probs * risk).sum(axis=1)
                    observed_risk = ((w[:, None] - y) ** 2).mean(axis=1)
                    observed_g0 = (groups == 0).mean(axis=1)
                    values = np.column_stack([risk, pop_risk, regret, weighted_risk, pop_risk - weighted_risk,
                                              pop_risk - observed_risk, observed_g0, sample_probs[:, 0], invitation_cost, w])
                    if t >= T - cfg["endpoint_last_rounds"]:
                        totals += values / cfg["endpoint_last_rounds"]
                    if t % 10 == 0:
                        means = values.reshape(W, S, -1).mean(axis=1)
                        for world in range(W):
                            trajectory_rows.append({"scenario": scenario, "beta": beta, "condition": condition,
                                                    "world": world, "completed_updates": t,
                                                    **dict(zip(METRICS, means[world].tolist()))})
                    if condition == "ipw":
                        weights = 1.0 / (3.0 * probabilities[row_index, groups])
                        estimate = (weights * y).sum(axis=1) / weights.sum(axis=1)
                        inv_weight = 1.0 / (3.0 * probabilities)
                        moment_error = max(float(np.max(np.abs((probabilities * inv_weight).sum(axis=1) - 1))),
                                           float(np.max(np.abs((probabilities * inv_weight * theta).sum(axis=1) - oracle_action))))
                        checks["ipw_expectation_max_error"] = max(checks["ipw_expectation_max_error"], moment_error)
                    else:
                        estimate = y.mean(axis=1)
                    if is_replay_case:
                        replay["groups"].append(groups[0].copy())
                        replay["preferences"].append(y[0].copy())
                        replay["actions_before"].append(float(w[0]))
                        replay["batch_estimates"].append(float(estimate[0]))
                    w = (1 - cfg["learning_rate"]) * w + cfg["learning_rate"] * estimate
                    if is_replay_case:
                        replay["actions_after"].append(float(w[0]))

                # Endpoint action is the last-50-round mean; final-state action is a separate column.
                endpoint_arrays[key] = totals.copy()
                worlds = totals.reshape(W, S, -1).mean(axis=1)
                world_arrays[key] = worlds
                for n in range(N):
                    run_rows.append({"scenario": scenario, "beta": beta, "condition": condition,
                                     "world": int(world_ids[n]), "seed": int(seed_ids[n]),
                                     **dict(zip(METRICS, totals[n].tolist())), "action_after_last_update": float(w[n]),
                                     "oracle_action": float(oracle_action[n]), "oracle_risk": float(oracle_risk[n])})
                for world in range(W):
                    world_rows.append({"scenario": scenario, "beta": beta, "condition": condition,
                                       "world": world, **dict(zip(METRICS, worlds[world].tolist()))})
                # Post-update terminal snapshot: recompute the next-round population and selection risks.
                final_raw, final_probs = propensities(w, theta, friction, beta, cfg)
                if condition == "static":
                    final_raw, final_probs = initial_raw, initial_probs
                if condition == "quota":
                    final_probs = np.full_like(final_probs, 1 / 3)
                final_risk = (w[:, None] - theta) ** 2 + variance
                final_pop = final_risk.mean(axis=1)
                final_weighted = (final_probs * final_risk).sum(axis=1)
                final_cost = (1 / final_raw).mean(axis=1) if condition == "quota" else 3 / final_raw.sum(axis=1)
                unobserved = np.full(N, np.nan)
                final_values = np.column_stack([final_risk, final_pop, (w - oracle_action) ** 2, final_weighted,
                                               final_pop - final_weighted, unobserved,
                                               unobserved, final_probs[:, 0], final_cost, w])
                final_means = final_values.reshape(W, S, -1).mean(axis=1)
                for world in range(W):
                    trajectory_rows.append({"scenario": scenario, "beta": beta, "condition": condition,
                                            "world": world, "completed_updates": T,
                                            **dict(zip(METRICS, final_means[world].tolist()))})
                condition_counter += 1
                print(f"Completed {condition_counter}/36 condition cells: {scenario}, beta={beta}, {condition}", flush=True)

    for scenario in cfg["scenarios"]:
        difference = float(np.max(np.abs(endpoint_arrays[(scenario, 0.0, "endogenous")] - endpoint_arrays[(scenario, 0.0, "static")])))
        checks["zero_beta_endogenous_static_max_endpoint_difference"] = max(checks["zero_beta_endogenous_static_max_endpoint_difference"], difference)
    for g in range(3):
        checks["quota_count_check"] = checks["quota_count_check"] and bool(np.all((quota_groups == g).sum(axis=1) == B // 3))

    replay_w = float(replay["actions_before"][0])
    replay_errors = []
    for preferences, expected in zip(replay["preferences"], replay["actions_after"]):
        replay_w = (1 - cfg["learning_rate"]) * replay_w + cfg["learning_rate"] * np.asarray(preferences).mean()
        replay_errors.append(abs(replay_w - expected))
    checks["replay_max_action_error"] = float(max(replay_errors))
    np.savez_compressed(out / "replay_main_beta3_world0_seed0.npz", **{k: np.asarray(v) for k, v in replay.items()})
    for name, value in checks.items():
        if name not in ["status", "quota_count_check"] and value > 1e-11:
            raise AssertionError(f"Invariant failed: {name}={value}")
    if not checks["quota_count_check"]:
        raise AssertionError("Quota count invariant failed")
    checks["status"] = "passed"

    run_fields = ["scenario", "beta", "condition", "world", "seed"] + METRICS + ["action_after_last_update", "oracle_action", "oracle_risk"]
    write_csv(out / "run_metrics.csv", run_rows, run_fields)
    write_csv(out / "world_metrics.csv", world_rows, ["scenario", "beta", "condition", "world"] + METRICS)
    write_csv(out / "trajectories_world.csv", trajectory_rows, ["scenario", "beta", "condition", "world", "completed_updates"] + METRICS)
    bootstrap_rng = np.random.default_rng(cfg["bootstrap_seed"])
    indices = bootstrap_rng.integers(0, W, size=(cfg["bootstrap_resamples"], W))
    condition_estimates, contrasts = [], []
    for key, values in world_arrays.items():
        scenario, beta, condition = key
        for metric_index, metric in enumerate(METRICS):
            condition_estimates.append({"scenario": scenario, "beta": beta, "condition": condition,
                                        "metric": metric, **bootstrap(values[:, metric_index], indices)})
    comparisons = [("endogenous", "static"), ("endogenous", "quota"), ("ipw", "endogenous"), ("ipw", "quota")]
    primary = None
    for scenario in cfg["scenarios"]:
        for beta in cfg["betas"]:
            for lhs, rhs in comparisons:
                differences = world_arrays[(scenario, float(beta), lhs)] - world_arrays[(scenario, float(beta), rhs)]
                for metric_index, metric in enumerate(METRICS):
                    is_primary = scenario == "main" and beta == 3.0 and lhs == "endogenous" and rhs == "static" and metric == "g0_risk"
                    result = {"scenario": scenario, "beta": beta, "contrast": f"{lhs} minus {rhs}",
                              "metric": metric, "analysis_role": "primary" if is_primary else "secondary_or_exploratory",
                              **bootstrap(differences[:, metric_index], indices)}
                    contrasts.append(result)
                    if is_primary:
                        primary = result
    write_json(out / "condition_estimates.json", condition_estimates)
    write_json(out / "contrasts.json", contrasts)
    write_json(out / "checks.json", checks)
    write_csv(out / "condition_estimates.csv", condition_estimates, ["scenario", "beta", "condition", "metric", "mean", "ci95_low", "ci95_high", "n_worlds"])
    write_csv(out / "contrasts.csv", contrasts, ["scenario", "beta", "contrast", "metric", "analysis_role", "mean", "ci95_low", "ci95_high", "n_worlds"])
    summary = {
        **provenance, "completed_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": time.perf_counter() - start,
        "actual_runs": len(run_rows), "condition_cells": condition_counter,
        "worlds": W, "paired_seeds_per_world": S,
        "rounds_per_run": T, "accepted_feedback_per_round": B,
        "total_synthetic_feedback_observations": len(run_rows) * T * B,
        "primary_result": primary, "checks": checks,
        "limitations": [
            "Synthetic scalar EMA mechanism; no people, LLMs, biology, or clinical outcomes.",
            "Participation function and equally weighted squared-loss objective are assumptions.",
            "Learner starts at the complete-information population optimum.",
            "IPW uses known true propensities; self-normalized ratios can have finite-batch bias.",
            "Accepted feedback and update budgets match, invitation costs do not.",
            "Bootstrap resamples 20 worlds after averaging 10 paired seeds within each world.",
            "Secondary intervals are descriptive and not corrected for multiple comparisons.",
            "No factual-knowledge or preference-prediction retention was measured.",
        ],
    }
    summary["output_hashes"] = {p.name: sha256(p) for p in sorted(out.iterdir()) if p.is_file()}
    write_json(out / "summary.json", summary)
    print(json.dumps({"actual_runs": len(run_rows), "elapsed_seconds": summary["elapsed_seconds"], "primary_result": primary, "checks": checks}, indent=2), flush=True)


if __name__ == "__main__":
    main()
