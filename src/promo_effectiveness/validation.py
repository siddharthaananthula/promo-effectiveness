"""Window definitions and validation for descriptive campaign inputs."""

from dataclasses import dataclass
from numbers import Integral

import pandas as pd


@dataclass(frozen=True)
class CampaignWindow:
    period_id: str
    period_label: str
    start_day: int
    end_day: int

    @property
    def duration_days(self) -> int:
        return self.end_day - self.start_day + 1


def _positive_integer(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return int(value)


def build_campaign_windows(
    campaign_start_day: int,
    campaign_end_day: int,
    *,
    pre_days: int = 28,
    post_days: int = 28,
) -> tuple[CampaignWindow, CampaignWindow, CampaignWindow]:
    """Return contiguous inclusive pre, campaign and post day windows."""

    if isinstance(campaign_start_day, bool) or not isinstance(campaign_start_day, Integral):
        raise ValueError("campaign_start_day must be an integer")
    if isinstance(campaign_end_day, bool) or not isinstance(campaign_end_day, Integral):
        raise ValueError("campaign_end_day must be an integer")
    if campaign_start_day < 1 or campaign_end_day < campaign_start_day:
        raise ValueError("Campaign day boundaries are invalid")
    pre_days = _positive_integer(pre_days, "pre_days")
    post_days = _positive_integer(post_days, "post_days")
    start, end = int(campaign_start_day), int(campaign_end_day)
    return (
        CampaignWindow("pre", "Pre", start - pre_days, start - 1),
        CampaignWindow("during", "Campaign", start, end),
        CampaignWindow("post", "Post", end + 1, end + post_days),
    )


def normalize_window_total(value, duration_days: int, target_days: int = 28):
    """Scale a window total to a target-day equivalent without dropping zeros."""

    target_days = _positive_integer(target_days, "target_days")
    if isinstance(duration_days, Integral) and not isinstance(duration_days, bool):
        duration_days = _positive_integer(duration_days, "duration_days")
    else:
        duration_days = pd.to_numeric(duration_days, errors="raise")
        if duration_days.isna().any() or (duration_days <= 0).any():
            raise ValueError("duration_days must contain only positive integers")
    return value * target_days / duration_days


def unique_assignment_pairs(assignments: pd.DataFrame) -> pd.DataFrame:
    """Validate assignment keys and remove duplicate household-campaign pairs."""

    required = {"household_key", "campaign_id"}
    if not required.issubset(assignments.columns):
        raise ValueError("Assignments require household_key and campaign_id")
    pairs = assignments.loc[:, ["household_key", "campaign_id"]].dropna().drop_duplicates().copy()
    if pairs.empty:
        return pairs.astype({"household_key": "int64", "campaign_id": "int64"})
    pairs["household_key"] = pd.to_numeric(pairs["household_key"], errors="raise").astype("int64")
    pairs["campaign_id"] = pd.to_numeric(pairs["campaign_id"], errors="raise").astype("int64")
    return pairs.reset_index(drop=True)


def campaign_overlap_counts(campaigns: pd.DataFrame, assignments: pd.DataFrame) -> pd.DataFrame:
    """Count unique assignments and co-assignments, using schedule ranges only."""

    required_campaign_columns = {"campaign_id", "start_day", "end_day"}
    if not required_campaign_columns.issubset(campaigns.columns):
        raise ValueError("Campaigns require campaign_id, start_day and end_day")
    calendar = campaigns.loc[:, ["campaign_id", "start_day", "end_day"]].copy()
    if calendar["campaign_id"].duplicated().any():
        raise ValueError("Campaign IDs must be unique")
    calendar["campaign_id"] = pd.to_numeric(calendar["campaign_id"], errors="raise").astype("int64")
    calendar["start_day"] = pd.to_numeric(calendar["start_day"], errors="raise").astype("int64")
    calendar["end_day"] = pd.to_numeric(calendar["end_day"], errors="raise").astype("int64")
    if (calendar["end_day"] < calendar["start_day"]).any():
        raise ValueError("Campaign end_day must not precede start_day")

    pairs = unique_assignment_pairs(assignments)
    known_campaigns = set(calendar["campaign_id"])
    unknown = set(pairs["campaign_id"]) - known_campaigns
    if unknown:
        raise ValueError("Assignments contain campaign IDs absent from campaign metadata")

    household_campaigns = pairs.groupby("household_key")["campaign_id"].agg(set).to_dict()
    assigned_by_campaign = pairs.groupby("campaign_id")["household_key"].agg(set).to_dict()
    schedule = calendar.set_index("campaign_id")[["start_day", "end_day"]].to_dict("index")
    rows = []
    for campaign in calendar.itertuples(index=False):
        campaign_id = int(campaign.campaign_id)
        assigned = assigned_by_campaign.get(campaign_id, set())
        other_scheduled_ids = {
            other_id for other_id, bounds in schedule.items()
            if other_id != campaign_id
            and bounds["start_day"] <= int(campaign.end_day)
            and bounds["end_day"] >= int(campaign.start_day)
        }
        any_other = {
            household for household in assigned
            if household_campaigns.get(household, set()) - {campaign_id}
        }
        schedule_overlap = {
            household for household in assigned
            if household_campaigns.get(household, set()) & other_scheduled_ids
        }
        rows.append({
            "campaign_id": campaign_id,
            "assigned_households": len(assigned),
            "households_also_assigned_any": len(any_other),
            "households_also_assigned_schedule_overlap": len(schedule_overlap),
        })
    return pd.DataFrame(rows).sort_values("campaign_id").reset_index(drop=True)
