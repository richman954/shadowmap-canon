#!/usr/bin/env python3
"""Run ShadowMap tensor-message transfer tests and write JSON/CSV artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from shadowmap.examples import transfer_test_cases


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    out_dir = repo_root / "data" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = transfer_test_cases()
    json_path = out_dir / "tensor_message_transfer_results.json"
    json_path.write_text(json.dumps(cases, indent=2), encoding="utf-8")

    csv_path = out_dir / "tensor_message_transfer_results.csv"
    fieldnames = [
        "case", "node_count", "factor_count", "exact_logZ", "bp_bethe_logZ",
        "K_loop_logZ", "mean_var_L1", "max_var_L1", "bp_iters", "bp_max_delta",
        "top_factor_1", "top_factor_1_L1", "top_factor_2", "top_factor_2_L1",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for case in cases:
            top = case["top_factor_residuals"]
            writer.writerow({
                "case": case["case"],
                "node_count": case["node_count"],
                "factor_count": case["factor_count"],
                "exact_logZ": case["exact_logZ"],
                "bp_bethe_logZ": case["bp_bethe_logZ"],
                "K_loop_logZ": case["K_loop_logZ"],
                "mean_var_L1": case["mean_var_L1"],
                "max_var_L1": case["max_var_L1"],
                "bp_iters": case["bp_iters"],
                "bp_max_delta": case["bp_max_delta"],
                "top_factor_1": top[0][0],
                "top_factor_1_L1": top[0][1],
                "top_factor_2": top[1][0],
                "top_factor_2_L1": top[1][1],
            })

    for case in cases:
        print(f"{case['case']}: K_loop={case['K_loop_logZ']:.6f}; top={case['top_factor_residuals'][0]}")
    print(f"Wrote {json_path}")
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
