from __future__ import annotations

import unittest

import numpy as np

from shadowmap.factor_graph import BinaryFactorGraph, Factor, noisy_implication, pair_table, unary
from shadowmap.examples import make_eldmr_graph, make_kernel_survivor_graph


class FactorGraphTests(unittest.TestCase):
    def test_unary_normalizes(self) -> None:
        prior = unary(0.75)
        self.assertAlmostEqual(float(np.sum(prior)), 1.0)
        self.assertAlmostEqual(float(prior[1]), 0.75)

    def test_exact_simple_graph(self) -> None:
        graph = BinaryFactorGraph(
            ["a", "b"],
            [Factor("ab", ("a", "b"), pair_table(1.0, same=True))],
        )
        exact = graph.exact()
        self.assertGreater(exact["Z"], 0.0)
        for belief in exact["var_marginals"].values():
            self.assertAlmostEqual(float(np.sum(belief)), 1.0)

    def test_bp_runs_on_transfer_graphs(self) -> None:
        for graph in [make_eldmr_graph(), make_kernel_survivor_graph()]:
            result = graph.evaluate(max_iter=300)
            self.assertGreater(result["K_loop_logZ"], 0.0)
            self.assertLess(result["bp_max_delta"], 1e-6)
            self.assertGreaterEqual(len(result["top_factor_residuals"]), 2)

    def test_noisy_implication_shape(self) -> None:
        table = noisy_implication(0.5)
        self.assertEqual(table.shape, (2, 2))
        self.assertGreater(table[1, 1], table[1, 0])


if __name__ == "__main__":
    unittest.main()
