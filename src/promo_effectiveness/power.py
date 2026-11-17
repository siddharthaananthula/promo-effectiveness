"""Transparent, normal-approximation power calculations for two-arm designs."""

from dataclasses import dataclass
from math import ceil, isfinite, sqrt
from statistics import NormalDist

import pandas as pd


@dataclass(frozen=True)
class TwoArmSampleSize:
    """Required independent household counts for a two-sided mean comparison."""

    treatment_n: int
    control_n: int
    total_n: int


def _validate_design_inputs(sigma, alpha: float, power: float) -> tuple[float, float, float]:
    try:
        sigma = float(sigma)
        alpha = float(alpha)
        power = float(power)
    except (TypeError, ValueError) as exc:
        raise ValueError("sigma, alpha and power must be numeric") from exc
    if not isfinite(sigma) or sigma <= 0:
        raise ValueError("sigma must be finite and positive")
    if not isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be between zero and one")
    if not isfinite(power) or not 0 < power < 1:
        raise ValueError("power must be between zero and one")
    return sigma, alpha, power


def estimate_household_window_sd(household_window_spend: pd.DataFrame) -> float:
    """Return a pooled descriptive SD across household-window rows.

    Input rows must be one row per household and historical window. The data
    extract should explicitly include zero-purchase households; missing values
    are rejected rather than silently interpreted as zero. If households recur
    across windows, this pooled SD is not based on independent rows and should
    not be described as a 1-row-per-person variance estimate.
    """

    rows = _validated_household_window_spend(household_window_spend)
    return float(rows["window_spend"].std(ddof=1))


def estimate_max_window_sd(household_window_spend: pd.DataFrame) -> float:
    """Return the largest cross-household SD among historical windows.

    Each window's SD uses one row per household. Selecting the largest recent
    window is a transparent planning sensitivity when the same households recur
    across periods and time-specific variability differs.
    """

    rows = _validated_household_window_spend(household_window_spend)
    counts = rows.groupby("period_id")["window_spend"].size()
    if (counts < 2).any():
        raise ValueError("Each historical window needs at least two households")
    return float(rows.groupby("period_id")["window_spend"].std(ddof=1).max())


def _validated_household_window_spend(household_window_spend: pd.DataFrame) -> pd.DataFrame:
    required = {"household_key", "period_id", "window_spend"}
    if not required.issubset(household_window_spend.columns):
        raise ValueError("Historical sales require household_key, period_id and window_spend")
    rows = household_window_spend.loc[:, ["household_key", "period_id", "window_spend"]].copy()
    if rows[["household_key", "period_id", "window_spend"]].isna().any().any():
        raise ValueError("Historical household-window rows cannot contain missing values")
    if rows.duplicated(["household_key", "period_id"]).any():
        raise ValueError("Historical sales must be unique per household and window")
    rows["window_spend"] = pd.to_numeric(rows["window_spend"], errors="raise").astype(float)
    if not rows["window_spend"].map(isfinite).all():
        raise ValueError("Historical sales must be finite")
    if rows["window_spend"].size < 2:
        raise ValueError("At least two household-window observations are required")
    return rows


def two_arm_sample_size(
    sigma: float,
    minimum_detectable_effect: float,
    *,
    alpha: float = 0.05,
    power: float = 0.80,
    control_to_treatment_ratio: float = 1.0,
) -> TwoArmSampleSize:
    """Calculate normal-approximation counts for an independent mean contrast.

    `control_to_treatment_ratio` is the number of control households per
    treatment household. Counts are rounded up; this is a planning calculation,
    not a substitute for a cluster design effect or a final protocol review.
    """

    sigma, alpha, power = _validate_design_inputs(sigma, alpha, power)
    try:
        effect = float(minimum_detectable_effect)
        ratio = float(control_to_treatment_ratio)
    except (TypeError, ValueError) as exc:
        raise ValueError("Effect and allocation ratio must be numeric") from exc
    if not isfinite(effect) or effect <= 0:
        raise ValueError("minimum_detectable_effect must be finite and positive")
    if not isfinite(ratio) or ratio <= 0:
        raise ValueError("control_to_treatment_ratio must be finite and positive")

    z_alpha = NormalDist().inv_cdf(1 - alpha / 2)
    z_power = NormalDist().inv_cdf(power)
    treatment_n = ceil((1 + 1 / ratio) * ((z_alpha + z_power) * sigma / effect) ** 2)
    control_n = ceil(treatment_n * ratio)
    return TwoArmSampleSize(treatment_n, control_n, treatment_n + control_n)


def minimum_detectable_effect(
    sigma: float,
    treatment_n: int,
    control_n: int,
    *,
    alpha: float = 0.05,
    power: float = 0.80,
) -> float:
    """Return the absolute detectable mean difference at specified design inputs."""

    sigma, alpha, power = _validate_design_inputs(sigma, alpha, power)
    if (isinstance(treatment_n, bool) or not isinstance(treatment_n, int) or treatment_n <= 0
            or isinstance(control_n, bool) or not isinstance(control_n, int) or control_n <= 0):
        raise ValueError("treatment_n and control_n must be positive integers")
    z_alpha = NormalDist().inv_cdf(1 - alpha / 2)
    z_power = NormalDist().inv_cdf(power)
    return (z_alpha + z_power) * sigma * sqrt(1 / treatment_n + 1 / control_n)


def power_scenarios(
    sigma: float,
    reference_mean: float,
    *,
    relative_mdes=(0.05, 0.10, 0.15),
    alpha_values=(0.05, 0.01),
    power_values=(0.80, 0.90),
) -> pd.DataFrame:
    """Build a reproducible grid of equal-allocation sample-size scenarios."""

    sigma, _, _ = _validate_design_inputs(sigma, 0.05, 0.80)
    try:
        reference_mean = float(reference_mean)
    except (TypeError, ValueError) as exc:
        raise ValueError("reference_mean must be numeric") from exc
    if not isfinite(reference_mean) or reference_mean <= 0:
        raise ValueError("reference_mean must be finite and positive")

    rows = []
    for relative_mde in relative_mdes:
        relative_mde = float(relative_mde)
        if not isfinite(relative_mde) or relative_mde <= 0:
            raise ValueError("Relative MDEs must be finite and positive")
        effect = reference_mean * relative_mde
        for alpha in alpha_values:
            for target_power in power_values:
                result = two_arm_sample_size(
                    sigma,
                    effect,
                    alpha=float(alpha),
                    power=float(target_power),
                )
                rows.append({
                    "relative_mde_pct": 100 * relative_mde,
                    "mde_per_household": effect,
                    "two_sided_alpha": float(alpha),
                    "target_power": float(target_power),
                    "treatment_n": result.treatment_n,
                    "control_n": result.control_n,
                    "total_n": result.total_n,
                })
    return pd.DataFrame(rows)
