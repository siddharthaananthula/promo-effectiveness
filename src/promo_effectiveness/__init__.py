"""Reusable descriptive campaign-analysis components."""

from .config import DatabaseConfig, create_readonly_engine, load_database_config, readonly_connection, verify_readonly
from .charts import campaign26_spending_svg, campaign_assignment_overlap_svg, save_svg
from .descriptive import (
    build_campaign_overview,
    summarize_household_periods,
    summarize_promotion_quality,
    summarize_redemptions,
)
from .extract import (
    fetch_assignment_pairs,
    fetch_campaign26_household_periods,
    fetch_campaign_dimensions,
    fetch_household_window_sales,
    fetch_promotion_quality,
    fetch_redemption_events,
)
from .validation import CampaignWindow, build_campaign_windows, campaign_overlap_counts, normalize_window_total
from .power import (
    TwoArmSampleSize,
    estimate_household_window_sd,
    estimate_max_window_sd,
    minimum_detectable_effect,
    power_scenarios,
    two_arm_sample_size,
)

__all__ = [
    "CampaignWindow",
    "DatabaseConfig",
    "build_campaign_overview",
    "build_campaign_windows",
    "campaign26_spending_svg",
    "campaign_assignment_overlap_svg",
    "campaign_overlap_counts",
    "create_readonly_engine",
    "fetch_assignment_pairs",
    "fetch_campaign26_household_periods",
    "fetch_campaign_dimensions",
    "fetch_household_window_sales",
    "fetch_promotion_quality",
    "fetch_redemption_events",
    "load_database_config",
    "normalize_window_total",
    "readonly_connection",
    "save_svg",
    "summarize_household_periods",
    "summarize_promotion_quality",
    "summarize_redemptions",
    "verify_readonly",
    "TwoArmSampleSize",
    "estimate_household_window_sd",
    "estimate_max_window_sd",
    "minimum_detectable_effect",
    "power_scenarios",
    "two_arm_sample_size",
]
