"""Reference ShadowMap transfer-test factor graphs."""

from __future__ import annotations

import math
from typing import Dict, List

import numpy as np

from .factor_graph import BinaryFactorGraph, Factor, noisy_implication, pair_table, unary


def make_eldmr_graph() -> BinaryFactorGraph:
    """ELDMR hidden-memory / field-shielding factor graph."""
    variables = [
        "q_memory_high",
        "E_eff_low",
        "S_pair_stable",
        "T_mixing_suppressed",
        "EL_high",
        "ELDMR_high",
        "MEL_high",
    ]
    factors = [
        Factor("prior_q_reverse_condition", ("q_memory_high",), unary(0.62)),
        Factor("memory_shields_field:q->E", ("q_memory_high", "E_eff_low"), noisy_implication(1.15)),
        Factor("low_field_stabilizes_singlet:E->S", ("E_eff_low", "S_pair_stable"), noisy_implication(1.05)),
        Factor("singlet_drives_EL:S->EL", ("S_pair_stable", "EL_high"), noisy_implication(0.95)),
        Factor("singlet_drives_ELDMR:S->ELDMR", ("S_pair_stable", "ELDMR_high"), noisy_implication(1.25)),
        Factor("low_field_drives_MEL:E->MEL", ("E_eff_low", "MEL_high"), noisy_implication(0.85)),
        Factor("ELDMR_hysteresis_feedback:ELDMR->q", ("ELDMR_high", "q_memory_high"), noisy_implication(0.75)),
        Factor("MEL_spin_loop:MEL<->Tmix", ("MEL_high", "T_mixing_suppressed"), noisy_implication(0.70)),
        Factor("Tmix_supports_singlet:Tmix->S", ("T_mixing_suppressed", "S_pair_stable"), noisy_implication(0.45)),
    ]
    return BinaryFactorGraph(variables, factors)


def make_kernel_survivor_graph() -> BinaryFactorGraph:
    """Kernel/Survivor financial-fragility factor graph.

    This is a structural demo only, not an investment recommendation.
    """
    variables = [
        "debt_accel_high",
        "fcf_stable",
        "interest_cover_high",
        "funding_stress_high",
        "market_crash_sensitive",
        "kernel_energy_high",
        "survivor_score_high",
        "victim_score_high",
    ]
    factors = [
        Factor("prior_funding_regime", ("funding_stress_high",), unary(0.45)),
        Factor("prior_debt_acceleration", ("debt_accel_high",), unary(0.50)),
        Factor("fcf_supports_survivor", ("fcf_stable", "survivor_score_high"), noisy_implication(1.00)),
        Factor("interest_cover_supports_survivor", ("interest_cover_high", "survivor_score_high"), noisy_implication(0.90)),
        Factor("debt_drives_kernel", ("debt_accel_high", "kernel_energy_high"), noisy_implication(1.15)),
        Factor(
            "funding_x_market_drives_kernel",
            ("funding_stress_high", "market_crash_sensitive", "kernel_energy_high"),
            np.array([
                [[math.exp(0.30), math.exp(-0.20)], [math.exp(-0.15), math.exp(0.45)]],
                [[math.exp(-0.10), math.exp(0.35)], [math.exp(-0.80), math.exp(1.30)]],
            ], dtype=float),
        ),
        Factor("kernel_drives_victim", ("kernel_energy_high", "victim_score_high"), noisy_implication(1.10)),
        Factor("debt_drives_victim", ("debt_accel_high", "victim_score_high"), noisy_implication(0.90)),
        Factor("survivor_victim_tension", ("survivor_score_high", "victim_score_high"), pair_table(0.65, same=False)),
        Factor("funding_degrades_fcf", ("funding_stress_high", "fcf_stable"), pair_table(0.75, same=False)),
        Factor("debt_market_stress_loop", ("debt_accel_high", "market_crash_sensitive"), noisy_implication(0.60)),
    ]
    return BinaryFactorGraph(variables, factors)


def summarize_graph(name: str, graph: BinaryFactorGraph, interpretation: str) -> Dict[str, object]:
    result = graph.evaluate()
    return {
        "case": name,
        "node_count": len(graph.variables),
        "factor_count": len(graph.factors),
        "exact_logZ": result["exact_logZ"],
        "bp_bethe_logZ": result["bp_bethe_logZ"],
        "K_loop_logZ": result["K_loop_logZ"],
        "mean_var_L1": result["mean_var_L1"],
        "max_var_L1": result["max_var_L1"],
        "bp_iters": result["bp_iters"],
        "bp_max_delta": result["bp_max_delta"],
        "top_factor_residuals": result["top_factor_residuals"],
        "exact_high_probabilities": {v: result["var_exact"][v][1] for v in graph.variables},
        "bp_high_probabilities": {v: result["var_bp"][v][1] for v in graph.variables},
        "interpretation": interpretation,
    }


def transfer_test_cases() -> List[Dict[str, object]]:
    """Run the two canonical tensor-message transfer tests."""
    return [
        summarize_graph(
            "ELDMR_pair_kinetic_factor_graph",
            make_eldmr_graph(),
            "Loop residual localizes on q_memory -> E_eff -> S_pair -> ELDMR feedback and MEL/Tmix branches.",
        ),
        summarize_graph(
            "Kernel_Survivor_financial_fragility_factor_graph",
            make_kernel_survivor_graph(),
            "Loop residual localizes on debt/funding/market/kernel/victim paths and survivor-victim tension.",
        ),
    ]
