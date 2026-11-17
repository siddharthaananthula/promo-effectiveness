"""Tests for prospective randomized experiment planning calculations."""

import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from promo_effectiveness.power import (  # noqa: E402
    estimate_household_window_sd,
    estimate_max_window_sd,
    minimum_detectable_effect,
    power_scenarios,
    two_arm_sample_size,
)


class HouseholdWindowVariabilityTests(unittest.TestCase):
    def test_sd_keeps_zero_purchase_households(self):
        rows = pd.DataFrame({
            "household_key": [1, 2, 3, 4],
            "period_id": ["a", "a", "a", "a"],
            "window_spend": [0, 0, 10, 10],
        })
        self.assertAlmostEqual(estimate_household_window_sd(rows), 5.77350269)

    def test_max_window_sd_uses_cross_sectional_window_spread(self):
        rows = pd.DataFrame({
            "household_key": [1, 2, 3, 4, 1, 2, 3, 4],
            "period_id": ["a"] * 4 + ["b"] * 4,
            "window_spend": [0, 0, 10, 10, 0, 10, 20, 30],
        })
        self.assertAlmostEqual(estimate_max_window_sd(rows), 12.90994449)

    def test_sd_rejects_duplicate_or_missing_household_windows(self):
        duplicate = pd.DataFrame({
            "household_key": [1, 1], "period_id": ["a", "a"], "window_spend": [5, 7],
        })
        with self.assertRaisesRegex(ValueError, "unique"):
            estimate_household_window_sd(duplicate)
        missing = pd.DataFrame({
            "household_key": [1, 2], "period_id": ["a", "a"], "window_spend": [5, None],
        })
        with self.assertRaisesRegex(ValueError, "missing"):
            estimate_household_window_sd(missing)


class TwoArmPowerTests(unittest.TestCase):
    def test_balanced_sample_size_matches_normal_approximation(self):
        result = two_arm_sample_size(10, 5, alpha=0.05, power=0.80)
        self.assertEqual((result.treatment_n, result.control_n, result.total_n), (63, 63, 126))
        self.assertLess(minimum_detectable_effect(10, 63, 63), 5)

    def test_allocation_ratio_and_conservative_scenarios(self):
        balanced = two_arm_sample_size(20, 10, alpha=0.05, power=0.80)
        two_controls = two_arm_sample_size(
            20, 10, alpha=0.05, power=0.80, control_to_treatment_ratio=2,
        )
        self.assertEqual(two_controls.control_n, 2 * two_controls.treatment_n)
        self.assertLess(two_controls.treatment_n, balanced.treatment_n)
        self.assertGreater(two_controls.total_n, balanced.total_n)

        scenarios = power_scenarios(240, 200)
        self.assertEqual(len(scenarios), 12)
        strict = scenarios.query("relative_mde_pct == 5 and two_sided_alpha == 0.01 and target_power == 0.9").iloc[0]
        easy = scenarios.query("relative_mde_pct == 15 and two_sided_alpha == 0.05 and target_power == 0.8").iloc[0]
        self.assertGreater(strict.total_n, easy.total_n)

    def test_invalid_design_values_are_rejected(self):
        for args in ((0, 5), (10, 0)):
            with self.assertRaises(ValueError):
                two_arm_sample_size(*args)
        with self.assertRaises(ValueError):
            two_arm_sample_size(10, 5, alpha=1)


if __name__ == "__main__":
    unittest.main()
