"""Reproduce the illustrative Phase 5 power inputs from the existing dbt mart."""

from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from promo_effectiveness import (  # noqa: E402
    CampaignWindow,
    create_readonly_engine,
    estimate_household_window_sd,
    estimate_max_window_sd,
    fetch_household_window_sales,
    load_database_config,
    minimum_detectable_effect,
    power_scenarios,
    verify_readonly,
)


def main() -> None:
    windows = tuple(
        CampaignWindow(
            period_id=f"planning_{start_day}",
            period_label=f"Days {start_day}-{start_day + 41}",
            start_day=start_day,
            end_day=start_day + 41,
        )
        for start_day in (98, 140, 182)
    )
    config = load_database_config(PROJECT_ROOT / "secrets" / "retail-analytics.env")
    engine = create_readonly_engine(config)
    try:
        if not verify_readonly(engine):
            raise RuntimeError("Database session did not report read-only mode")
        household_windows = fetch_household_window_sales(engine, windows)
    finally:
        engine.dispose()

    household_windows["window_spend"] = pd.to_numeric(
        household_windows["window_spend"], errors="raise"
    )
    window_summary = (
        household_windows.groupby("period_label")["window_spend"]
        .agg(households="size", mean="mean", sd="std")
    )
    pooled_descriptive_sd = estimate_household_window_sd(household_windows)
    sigma = estimate_max_window_sd(household_windows)
    reference_mean = float(window_summary["mean"].mean())
    scenarios = power_scenarios(sigma, reference_mean)
    illustrative_frame_arm = 2500 // 2
    frame_mde = minimum_detectable_effect(sigma, illustrative_frame_arm, illustrative_frame_arm)

    print("Database transaction mode: read-only")
    print("Historical planning input only; not Endeavour statistics or a treatment effect.")
    print(window_summary.round(2).to_string())
    print(f"Reference mean (average of three window means): {reference_mean:.2f}")
    print(
        "Pooled SD across repeated household-window rows (descriptive only): "
        f"{pooled_descriptive_sd:.2f}"
    )
    print(f"Planning sigma (largest single-window household SD): {sigma:.2f}")
    print("\nEqual-allocation two-sided normal-approximation scenarios:")
    print(scenarios.round({"mde_per_household": 2}).to_string(index=False))
    print(
        "\nIllustrative 2,500-household frame, 1:1 allocation: "
        f"80%-power / 5%-alpha MDE={frame_mde:.2f} "
        f"({100 * frame_mde / reference_mean:.2f}% of reference mean)."
    )


if __name__ == "__main__":
    main()
