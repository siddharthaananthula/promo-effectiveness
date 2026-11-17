"""Unit tests for the reusable descriptive campaign-analysis package."""

import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from promo_effectiveness.descriptive import (  # noqa: E402
    build_campaign_overview,
    summarize_household_periods,
    summarize_promotion_quality,
    summarize_redemptions,
)
from promo_effectiveness.validation import (  # noqa: E402
    build_campaign_windows,
    campaign_overlap_counts,
    normalize_window_total,
)


class CampaignWindowTests(unittest.TestCase):
    def test_campaign_26_window_boundaries_are_inclusive_and_contiguous(self):
        pre, campaign, post = build_campaign_windows(224, 264)
        self.assertEqual((pre.start_day, pre.end_day, pre.duration_days), (196, 223, 28))
        self.assertEqual((campaign.start_day, campaign.end_day, campaign.duration_days), (224, 264, 41))
        self.assertEqual((post.start_day, post.end_day, post.duration_days), (265, 292, 28))
        self.assertEqual(pre.end_day + 1, campaign.start_day)
        self.assertEqual(campaign.end_day + 1, post.start_day)

    def test_unequal_window_totals_normalize_to_28_day_equivalent(self):
        self.assertAlmostEqual(normalize_window_total(410, 41), 280)
        self.assertEqual(normalize_window_total(0, 41), 0)
        self.assertAlmostEqual(normalize_window_total(100, 28), 100)


class AssignmentOverlapTests(unittest.TestCase):
    def test_unique_assignments_and_inclusive_schedule_overlap(self):
        campaigns = pd.DataFrame([
            {'campaign_id': 1, 'start_day': 10, 'end_day': 20},
            {'campaign_id': 2, 'start_day': 20, 'end_day': 30},
            {'campaign_id': 3, 'start_day': 21, 'end_day': 24},
            {'campaign_id': 4, 'start_day': 5, 'end_day': 9},
        ])
        assignments = pd.DataFrame([
            (1, 1), (1, 2), (1, 4), (2, 1), (2, 3), (3, 1), (4, 2), (4, 3),
            (1, 2),  # duplicated source pair must not inflate counts
        ], columns=['household_key', 'campaign_id'])
        result = campaign_overlap_counts(campaigns, assignments).set_index('campaign_id')
        self.assertEqual(result.loc[1, 'assigned_households'], 3)
        self.assertEqual(result.loc[1, 'households_also_assigned_any'], 2)
        self.assertEqual(result.loc[1, 'households_also_assigned_schedule_overlap'], 1)
        self.assertEqual(result.loc[2, 'assigned_households'], 2)
        self.assertEqual(result.loc[2, 'households_also_assigned_schedule_overlap'], 2)
        self.assertEqual(result.loc[3, 'households_also_assigned_schedule_overlap'], 1)
        self.assertEqual(result.loc[4, 'households_also_assigned_schedule_overlap'], 0)


class DescriptiveSummaryTests(unittest.TestCase):
    def test_zero_purchase_households_stay_in_denominator_and_percentiles(self):
        household_periods = pd.DataFrame([
            {'household_key': 1, 'assignment_group': 'Assigned', 'period_label': 'Pre', 'duration_days': 28,
             'window_spend': 100.0, 'baskets': 2, 'shopping_days': 1},
            {'household_key': 2, 'assignment_group': 'Assigned', 'period_label': 'Pre', 'duration_days': 28,
             'window_spend': 0.0, 'baskets': 0, 'shopping_days': 0},
            {'household_key': 3, 'assignment_group': 'Assigned', 'period_label': 'Pre', 'duration_days': 28,
             'window_spend': 0.0, 'baskets': 0, 'shopping_days': 0},
        ])
        rows, summary = summarize_household_periods(household_periods)
        result = summary.iloc[0]
        self.assertEqual(len(rows), 3)
        self.assertEqual(result['households_including_zeros'], 3)
        self.assertEqual(result['active_households'], 1)
        self.assertEqual(result['zero_purchase_households'], 2)
        self.assertAlmostEqual(result['mean_spend_per_28d_equivalent'], 100 / 3, places=2)
        self.assertEqual(result['p10_spend_per_28d_equivalent'], 0)
        self.assertAlmostEqual(result['mean_baskets_per_28d_equivalent'], 2 / 3, places=2)

    def test_redemption_events_and_unique_redeemers_are_separate(self):
        events = pd.DataFrame([
            (26, 101), (26, 101), (26, 102), (27, 101),
        ], columns=['campaign_id', 'household_key'])
        summary = summarize_redemptions(events).set_index('campaign_id')
        self.assertEqual(summary.loc[26, 'recorded_redemption_events'], 3)
        self.assertEqual(summary.loc[26, 'unique_redeemers'], 2)
        campaigns = pd.DataFrame([
            {'campaign_id': 26, 'campaign_type': 'TypeA', 'start_day': 224, 'end_day': 264},
            {'campaign_id': 27, 'campaign_type': 'TypeC', 'start_day': 237, 'end_day': 300},
        ])
        assignments = pd.DataFrame([(101, 26), (102, 26), (101, 27)],
                                   columns=['household_key', 'campaign_id'])
        overview = build_campaign_overview(campaigns, assignments, events).set_index('campaign_id')
        self.assertEqual(overview.loc[26, 'recorded_redemption_events'], 3)
        self.assertEqual(overview.loc[26, 'unique_redeemers'], 2)

    def test_promotion_coverage_and_conflicting_key_counts_are_reconciled(self):
        counts = {
            'aggregated_product_store_week_keys': 97,
            'source_rows_represented': 100,
            'extra_source_rows_at_repeated_keys': 3,
            'keys_with_multiple_source_rows': 3,
            'keys_with_conflicting_promotion_states': 2,
            'first_promotion_week': 9,
            'last_promotion_week': 10,
            'promotion_weeks': 2,
            'sales_lines': 1000,
            'lines_with_promotion_record': 217,
            'lines_without_promotion_record': 783,
            'matched_lines_on_conflicting_keys': 8,
        }
        key_summary, line_summary = summarize_promotion_quality(counts)
        self.assertEqual(key_summary.loc[0, 'extra_source_rows_at_repeated_keys'], 3)
        self.assertEqual(key_summary.loc[0, 'keys_with_conflicting_promotion_states'], 2)
        self.assertEqual(line_summary.loc[0, 'match_coverage_pct'], 21.7)
        self.assertEqual(line_summary.loc[0, 'unmatched_pct'], 78.3)
        self.assertEqual(line_summary.loc[0, 'matched_lines_on_conflicting_keys'], 8)


if __name__ == '__main__':
    unittest.main()
