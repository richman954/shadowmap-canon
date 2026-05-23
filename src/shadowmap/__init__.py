"""ShadowMap canonical utilities.

This package contains small computational scaffolds for the ShadowMap canon:
factor-graph message passing, loop-residual scoring, and transfer-test examples.
"""

from .factor_graph import BinaryFactorGraph, Factor, pair_table, noisy_implication, unary

__all__ = [
    "BinaryFactorGraph",
    "Factor",
    "pair_table",
    "noisy_implication",
    "unary",
]
