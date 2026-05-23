"""Small binary factor graph toolkit for ShadowMap message-passing experiments.

The implementation is intentionally compact. It is for canon transfer tests and
structural triage, not for production-grade tensor-network simulation.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

EPS = 1e-12


def normalize(v: np.ndarray) -> np.ndarray:
    """Return a normalized nonnegative vector, falling back to uniform if needed."""
    v = np.maximum(np.asarray(v, dtype=float), 0.0)
    total = float(np.sum(v))
    if total <= EPS:
        return np.ones_like(v, dtype=float) / len(v)
    return v / total


@dataclass(frozen=True)
class Factor:
    """A factor over binary variables.

    Attributes:
        name: Human-readable factor name.
        vars: Ordered variable names indexing the factor table axes.
        table: Nonnegative compatibility table with shape ``(2,) * len(vars)``.
    """

    name: str
    vars: Tuple[str, ...]
    table: np.ndarray

    def __post_init__(self) -> None:
        expected_shape = (2,) * len(self.vars)
        table = np.asarray(self.table, dtype=float)
        if table.shape != expected_shape:
            raise ValueError(f"Factor {self.name!r} has shape {table.shape}; expected {expected_shape}")
        if np.any(table < 0):
            raise ValueError(f"Factor {self.name!r} contains negative entries")
        object.__setattr__(self, "table", table)


class BinaryFactorGraph:
    """Binary factor graph with exact enumeration and loopy BP/Bethe scoring."""

    def __init__(self, variables: List[str], factors: List[Factor]):
        if len(set(variables)) != len(variables):
            raise ValueError("Variables must be unique")
        unknown = sorted({v for f in factors for v in f.vars if v not in variables})
        if unknown:
            raise ValueError(f"Factors reference unknown variables: {unknown}")
        self.variables = list(variables)
        self.var_index = {v: i for i, v in enumerate(self.variables)}
        self.factors = list(factors)
        self.neighbors: Dict[str, List[int]] = {v: [] for v in self.variables}
        for fi, factor in enumerate(self.factors):
            for var in factor.vars:
                self.neighbors[var].append(fi)

    def exact(self) -> Dict[str, object]:
        """Exact partition and marginals by exhaustive enumeration."""
        n = len(self.variables)
        Z = 0.0
        var_marginals = {v: np.zeros(2, dtype=float) for v in self.variables}
        factor_marginals = {f.name: np.zeros_like(f.table, dtype=float) for f in self.factors}

        for bits in itertools.product([0, 1], repeat=n):
            weight = 1.0
            for factor in self.factors:
                idx = tuple(bits[self.var_index[v]] for v in factor.vars)
                weight *= float(factor.table[idx])
            Z += weight
            for var in self.variables:
                var_marginals[var][bits[self.var_index[var]]] += weight
            for factor in self.factors:
                idx = tuple(bits[self.var_index[v]] for v in factor.vars)
                factor_marginals[factor.name][idx] += weight

        logZ = math.log(max(Z, EPS))
        for var in self.variables:
            var_marginals[var] = normalize(var_marginals[var])
        for factor in self.factors:
            factor_marginals[factor.name] = factor_marginals[factor.name] / max(Z, EPS)
        return {"Z": Z, "logZ": logZ, "var_marginals": var_marginals, "factor_marginals": factor_marginals}

    def run_bp(self, max_iter: int = 500, tol: float = 1e-10, damping: float = 0.15) -> Dict[str, object]:
        """Run loopy belief propagation and return beliefs plus a Bethe logZ estimate."""
        if not 0.0 <= damping < 1.0:
            raise ValueError("damping must be in [0, 1)")

        f_to_v: Dict[Tuple[int, str], np.ndarray] = {}
        v_to_f: Dict[Tuple[str, int], np.ndarray] = {}
        for fi, factor in enumerate(self.factors):
            for var in factor.vars:
                f_to_v[(fi, var)] = np.ones(2, dtype=float) / 2
                v_to_f[(var, fi)] = np.ones(2, dtype=float) / 2

        max_delta = math.inf
        iterations = 0
        for it in range(max_iter):
            iterations = it + 1
            max_delta = 0.0

            new_v_to_f = dict(v_to_f)
            for var in self.variables:
                for fi in self.neighbors[var]:
                    prod = np.ones(2, dtype=float)
                    for fj in self.neighbors[var]:
                        if fj != fi:
                            prod *= f_to_v[(fj, var)]
                    msg = normalize(prod)
                    old = v_to_f[(var, fi)]
                    msg = normalize((1.0 - damping) * msg + damping * old)
                    new_v_to_f[(var, fi)] = msg
                    max_delta = max(max_delta, float(np.max(np.abs(msg - old))))
            v_to_f = new_v_to_f

            new_f_to_v = dict(f_to_v)
            for fi, factor in enumerate(self.factors):
                axes_vars = list(factor.vars)
                for target in factor.vars:
                    out = np.zeros(2, dtype=float)
                    target_axis = axes_vars.index(target)
                    for assignment in itertools.product([0, 1], repeat=len(axes_vars)):
                        weight = float(factor.table[assignment])
                        for var, bit in zip(axes_vars, assignment):
                            if var != target:
                                weight *= float(v_to_f[(var, fi)][bit])
                        out[assignment[target_axis]] += weight
                    msg = normalize(out)
                    old = f_to_v[(fi, target)]
                    msg = normalize((1.0 - damping) * msg + damping * old)
                    new_f_to_v[(fi, target)] = msg
                    max_delta = max(max_delta, float(np.max(np.abs(msg - old))))
            f_to_v = new_f_to_v

            if max_delta < tol:
                break

        var_beliefs = {}
        for var in self.variables:
            belief = np.ones(2, dtype=float)
            for fi in self.neighbors[var]:
                belief *= f_to_v[(fi, var)]
            var_beliefs[var] = normalize(belief)

        factor_beliefs = {}
        for fi, factor in enumerate(self.factors):
            belief = np.zeros_like(factor.table, dtype=float)
            axes_vars = list(factor.vars)
            for assignment in itertools.product([0, 1], repeat=len(axes_vars)):
                weight = float(factor.table[assignment])
                for var, bit in zip(axes_vars, assignment):
                    weight *= float(v_to_f[(var, fi)][bit])
                belief[assignment] = weight
            factor_beliefs[factor.name] = belief / max(float(np.sum(belief)), EPS)

        logZ_f_sum = 0.0
        for fi, factor in enumerate(self.factors):
            zf = 0.0
            axes_vars = list(factor.vars)
            for assignment in itertools.product([0, 1], repeat=len(axes_vars)):
                weight = float(factor.table[assignment])
                for var, bit in zip(axes_vars, assignment):
                    for fj in self.neighbors[var]:
                        if fj != fi:
                            weight *= float(f_to_v[(fj, var)][bit])
                zf += weight
            logZ_f_sum += math.log(max(zf, EPS))

        logZ_v_corr = 0.0
        for var in self.variables:
            zi = 0.0
            for bit in [0, 1]:
                prod = 1.0
                for fi in self.neighbors[var]:
                    prod *= float(f_to_v[(fi, var)][bit])
                zi += prod
            degree = len(self.neighbors[var])
            logZ_v_corr += (1 - degree) * math.log(max(zi, EPS))

        return {
            "iters": iterations,
            "max_delta": max_delta,
            "var_beliefs": var_beliefs,
            "factor_beliefs": factor_beliefs,
            "logZ_bethe": logZ_f_sum + logZ_v_corr,
            "f_to_v": f_to_v,
            "v_to_f": v_to_f,
        }

    def evaluate(self, max_iter: int = 500) -> Dict[str, object]:
        """Compare exact enumeration to BP/Bethe and rank residual hotspots."""
        exact = self.exact()
        bp = self.run_bp(max_iter=max_iter)
        log_residual = abs(float(exact["logZ"]) - float(bp["logZ_bethe"]))

        var_l1s = {
            var: float(np.sum(np.abs(exact["var_marginals"][var] - bp["var_beliefs"][var])))
            for var in self.variables
        }
        factor_l1s = {
            factor.name: float(np.sum(np.abs(exact["factor_marginals"][factor.name] - bp["factor_beliefs"][factor.name])))
            for factor in self.factors
        }
        top_factors = sorted(factor_l1s.items(), key=lambda kv: kv[1], reverse=True)[:5]
        return {
            "exact_logZ": float(exact["logZ"]),
            "bp_bethe_logZ": float(bp["logZ_bethe"]),
            "K_loop_logZ": float(log_residual),
            "mean_var_L1": float(np.mean(list(var_l1s.values()))),
            "max_var_L1": float(np.max(list(var_l1s.values()))),
            "top_factor_residuals": top_factors,
            "var_exact": {k: exact["var_marginals"][k].tolist() for k in self.variables},
            "var_bp": {k: bp["var_beliefs"][k].tolist() for k in self.variables},
            "bp_iters": int(bp["iters"]),
            "bp_max_delta": float(bp["max_delta"]),
        }


def pair_table(strength: float, same: bool = True) -> np.ndarray:
    """Binary pair compatibility table.

    Args:
        strength: Positive values sharpen compatibility.
        same: If True, favors equal states; otherwise favors opposite states.
    """
    table = np.ones((2, 2), dtype=float)
    for a in [0, 1]:
        for b in [0, 1]:
            table[a, b] = math.exp(strength if ((a == b) == same) else -strength)
    return table


def noisy_implication(strength: float) -> np.ndarray:
    """Soft parent->child implication table for binary variables."""
    table = np.ones((2, 2), dtype=float)
    table[1, 1] = math.exp(strength)
    table[1, 0] = math.exp(-strength)
    table[0, 0] = math.exp(0.45 * strength)
    table[0, 1] = math.exp(-0.35 * strength)
    return table


def unary(p1: float) -> np.ndarray:
    """Unary prior with probability mass p1 on state 1."""
    if not 0.0 <= p1 <= 1.0:
        raise ValueError("p1 must be in [0, 1]")
    return normalize(np.array([1.0 - p1, p1], dtype=float))
