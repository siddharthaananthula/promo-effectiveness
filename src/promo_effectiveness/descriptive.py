"""Pure descriptive calculations built over existing reporting-model outputs."""

import math

import pandas as pd

from .validation import campaign_overlap_counts, normalize_window_total


def summarize_redemptions(events: pd.DataFrame) -> pd.DataFrame:
    """Count redemption events separately from households that redeemed."""

    required = {"campaign_id", "household_key"}
    if not required.issubset(events.columns):
        raise ValueError("Redemption events require campaign_id and household_key")
    if events.empty:
        return pd.DataFrame({
            "campaign_id": pd.Series(dtype="int64"),
            "recorded_redemption_events": pd.Series(dtype="int64"),
            "unique_redeemers": pd.Series(dtype="int64"),
        })
    return (
        events.groupby("campaign_id", as_index=False)
        .agg(recorded_redemption_events=("household_key", "size"),
             unique_redeemers=("household_key", "nunique"))
    )


def build_campaign_overview(
    campaigns: pd.DataFrame,
    assignments: pd.DataFrame,
    redemption_events: pd.DataFrame,
) -> pd.DataFrame:
    """Build the 30-campaign assignment, schedule-overlap and redemption table."""

    required = {"campaign_id", "campaign_type", "start_day", "end_day"}
    if not required.issubset(campaigns.columns):
        raise ValueError("Campaign metadata is missing required columns")
    calendar = campaigns.copy()
    if calendar["campaign_id"].duplicated().any():
        raise ValueError("Campaign metadata must have one row per campaign")
    calendar["duration_days"] = calendar["end_day"] - calendar["start_day"] + 1
    if (calendar["duration_days"] <= 0).any():
        raise ValueError("Campaign durations must be positive")

    assignment_counts = campaign_overlap_counts(calendar, assignments)
    redemption_counts = summarize_redemptions(redemption_events)
    overview = (
        calendar.merge(assignment_counts, on="campaign_id", how="left", validate="one_to_one")
        .merge(redemption_counts, on="campaign_id", how="left", validate="one_to_one")
    )
    count_columns = [
        "assigned_households", "households_also_assigned_any",
        "households_also_assigned_schedule_overlap", "recorded_redemption_events", "unique_redeemers",
    ]
    overview[count_columns] = overview[count_columns].fillna(0).astype("int64")
    overview["share_assigned_also_assigned_any"] = (
        overview["households_also_assigned_any"] / overview["assigned_households"].where(overview["assigned_households"] != 0)
    ).fillna(0.0)
    overview["share_assigned_schedule_overlap"] = (
        overview["households_also_assigned_schedule_overlap"]
        / overview["assigned_households"].where(overview["assigned_households"] != 0)
    ).fillna(0.0)
    overview["share_assigned_also_assigned_any_pct"] = (
        100 * overview["share_assigned_also_assigned_any"]
    ).round(1)
    overview["share_assigned_schedule_overlap_pct"] = (
        100 * overview["share_assigned_schedule_overlap"]
    ).round(1)
    return overview.sort_values("campaign_id").reset_index(drop=True)


def summarize_household_periods(
    household_periods: pd.DataFrame,
    *,
    target_days: int = 28,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Keep all cohort rows, including zeros, and summarize spend/frequency."""

    required = {
        "household_key", "assignment_group", "period_label", "duration_days",
        "window_spend", "baskets", "shopping_days",
    }
    if not required.issubset(household_periods.columns):
        raise ValueError("Household-period data is missing required columns")
    rows = household_periods.copy()
    if rows.duplicated(["household_key", "period_label"]).any():
        raise ValueError("Household-period rows must be unique")
    rows["duration_days"] = pd.to_numeric(rows["duration_days"], errors="raise").astype(int)
    if (rows["duration_days"] <= 0).any():
        raise ValueError("Window duration must be positive")
    for column in ("window_spend", "baskets", "shopping_days"):
        rows[column] = pd.to_numeric(rows[column], errors="raise").fillna(0)
    rows["window_spend"] = rows["window_spend"].astype(float)
    if (rows[["window_spend", "baskets", "shopping_days"]] < 0).any().any():
        raise ValueError("Observed spend and shopping counts must be nonnegative")

    rows["spend_per_28d_equivalent"] = normalize_window_total(
        rows["window_spend"], rows["duration_days"], target_days
    )
    rows["baskets_per_28d_equivalent"] = normalize_window_total(
        rows["baskets"], rows["duration_days"], target_days
    )
    rows["active_in_window"] = rows["baskets"] > 0

    summary_rows = []
    for (group, period), values in rows.groupby(["assignment_group", "period_label"], sort=False):
        spend = values["spend_per_28d_equivalent"]
        frequency = values["baskets_per_28d_equivalent"]
        summary_rows.append({
            "assignment_group": group,
            "period": period,
            "days": int(values["duration_days"].iloc[0]),
            "households_including_zeros": len(values),
            "active_households": int(values["active_in_window"].sum()),
            "zero_purchase_households": int((~values["active_in_window"]).sum()),
            "active_rate_pct": round(100 * values["active_in_window"].mean(), 1),
            "mean_spend_actual_window_per_household": round(float(values["window_spend"].mean()), 2),
            "mean_spend_per_28d_equivalent": round(float(spend.mean()), 2),
            "p10_spend_per_28d_equivalent": round(float(spend.quantile(.10)), 2),
            "p25_spend_per_28d_equivalent": round(float(spend.quantile(.25)), 2),
            "p50_spend_per_28d_equivalent": round(float(spend.quantile(.50)), 2),
            "p75_spend_per_28d_equivalent": round(float(spend.quantile(.75)), 2),
            "p90_spend_per_28d_equivalent": round(float(spend.quantile(.90)), 2),
            "mean_baskets_actual_window_per_household": round(float(values["baskets"].mean()), 2),
            "mean_baskets_per_28d_equivalent": round(float(frequency.mean()), 2),
            "median_baskets_per_28d_equivalent": round(float(frequency.quantile(.50)), 2),
        })
    return rows, pd.DataFrame(summary_rows)


def summarize_promotion_quality(counts: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Format SQL aggregates and derive match rates without scanning raw rows in Python."""

    sales_lines = int(counts["sales_lines"])
    matched = int(counts["lines_with_promotion_record"])
    unmatched = int(counts["lines_without_promotion_record"])
    if min(sales_lines, matched, unmatched) < 0 or matched + unmatched != sales_lines:
        raise ValueError("Promotion match counts must be nonnegative and reconcile to sales lines")
    if matched > sales_lines:
        raise ValueError("Matched promotion lines cannot exceed total sales lines")
    keys = pd.DataFrame([{
        "aggregated_product_store_week_keys": int(counts["aggregated_product_store_week_keys"]),
        "source_rows_represented": int(counts["source_rows_represented"]),
        "extra_source_rows_at_repeated_keys": int(counts["extra_source_rows_at_repeated_keys"]),
        "keys_with_multiple_source_rows": int(counts["keys_with_multiple_source_rows"]),
        "keys_with_conflicting_promotion_states": int(counts["keys_with_conflicting_promotion_states"]),
        "first_promotion_week": int(counts["first_promotion_week"]),
        "last_promotion_week": int(counts["last_promotion_week"]),
        "promotion_weeks": int(counts["promotion_weeks"]),
    }])
    lines = pd.DataFrame([{
        "sales_lines": sales_lines,
        "lines_with_promotion_record": matched,
        "lines_without_promotion_record": unmatched,
        "match_coverage_pct": round(100 * matched / sales_lines, 2) if sales_lines else math.nan,
        "unmatched_pct": round(100 * unmatched / sales_lines, 2) if sales_lines else math.nan,
        "matched_lines_on_conflicting_keys": int(counts["matched_lines_on_conflicting_keys"]),
    }])
    if keys.loc[0, "extra_source_rows_at_repeated_keys"] != keys.loc[0, "source_rows_represented"] - keys.loc[0, "aggregated_product_store_week_keys"]:
        raise ValueError("Promotion source rows do not reconcile to aggregated keys")
    if keys.loc[0, "keys_with_conflicting_promotion_states"] > keys.loc[0, "aggregated_product_store_week_keys"]:
        raise ValueError("Conflicting promotion keys exceed the number of aggregate keys")
    return keys, lines
