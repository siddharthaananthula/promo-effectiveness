"""Read-only extraction from the existing dbt reporting models."""

from collections.abc import Sequence

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from .config import readonly_connection
from .validation import CampaignWindow


def fetch_campaign_dimensions(engine: Engine) -> pd.DataFrame:
    query = text("""
        SELECT campaign_id,campaign_type,start_day,end_day
        FROM dbt_dev.dim_campaign
        ORDER BY campaign_id
    """)
    with readonly_connection(engine) as connection:
        return pd.read_sql_query(query, connection)


def fetch_assignment_pairs(engine: Engine) -> pd.DataFrame:
    query = text("""
        SELECT DISTINCT household_key,campaign_id
        FROM dbt_dev.bridge_household_campaign
        ORDER BY campaign_id,household_key
    """)
    with readonly_connection(engine) as connection:
        return pd.read_sql_query(query, connection)


def fetch_redemption_events(engine: Engine) -> pd.DataFrame:
    """Return the small observed redemption-event set, not inferred exposure."""

    query = text("""
        SELECT campaign_id,household_key
        FROM dbt_dev.fct_coupon_redemptions
        ORDER BY campaign_id,household_key
    """)
    with readonly_connection(engine) as connection:
        return pd.read_sql_query(query, connection)


def fetch_campaign26_household_periods(
    engine: Engine,
    windows: Sequence[CampaignWindow],
    *,
    campaign_id: int = 26,
) -> pd.DataFrame:
    """Aggregate sales and baskets in SQL, preserving zero-activity households."""

    if not windows:
        raise ValueError("At least one campaign window is required")
    value_rows = []
    parameters = {"campaign_id": int(campaign_id)}
    for index, window in enumerate(windows):
        keys = {
            "id": f"period_id_{index}",
            "label": f"period_label_{index}",
            "start": f"start_day_{index}",
            "end": f"end_day_{index}",
            "duration": f"duration_days_{index}",
        }
        value_rows.append(
            "(:{id}, :{label}, :{start}, :{end}, :{duration})".format(**keys)
        )
        parameters.update({
            keys["id"]: window.period_id,
            keys["label"]: window.period_label,
            keys["start"]: window.start_day,
            keys["end"]: window.end_day,
            keys["duration"]: window.duration_days,
        })
    period_values = ",\n           ".join(value_rows)
    query = text(f"""
        WITH population AS (
            SELECT DISTINCT household_key FROM dbt_dev.fct_sales
        ), assigned AS (
            SELECT DISTINCT household_key
            FROM dbt_dev.bridge_household_campaign
            WHERE campaign_id=:campaign_id
        ), periods(period_id,period_label,start_day,end_day,duration_days) AS (
            VALUES {period_values}
        ), household_period_sales AS (
            SELECT s.household_key,p.period_id,
                   SUM(s.sales_value)::numeric AS window_spend,
                   COUNT(DISTINCT s.basket_id) AS baskets,
                   COUNT(DISTINCT s.transaction_day) AS shopping_days
            FROM dbt_dev.fct_sales s
            JOIN periods p ON s.transaction_day BETWEEN p.start_day AND p.end_day
            GROUP BY s.household_key,p.period_id
        )
        SELECT p.period_id,p.period_label,p.start_day,p.end_day,p.duration_days,
               CASE WHEN a.household_key IS NOT NULL THEN 'Assigned to Campaign 26'
                    ELSE 'Not assigned to Campaign 26' END AS assignment_group,
               pop.household_key,
               COALESCE(hps.window_spend,0)::numeric AS window_spend,
               COALESCE(hps.baskets,0)::integer AS baskets,
               COALESCE(hps.shopping_days,0)::integer AS shopping_days
        FROM population pop
        CROSS JOIN periods p
        LEFT JOIN assigned a USING(household_key)
        LEFT JOIN household_period_sales hps
          ON hps.household_key=pop.household_key AND hps.period_id=p.period_id
        ORDER BY p.start_day,assignment_group,pop.household_key
    """)
    with readonly_connection(engine) as connection:
        return pd.read_sql_query(query, connection, params=parameters)


def fetch_household_window_sales(
    engine: Engine,
    windows: Sequence[CampaignWindow],
) -> pd.DataFrame:
    """Return zero-inclusive household sales for named historical windows.

    This compact extract supports planning calculations such as estimating
    household-level outcome variability. All aggregation happens in PostgreSQL.
    """

    if not windows:
        raise ValueError("At least one historical window is required")
    if len({window.period_id for window in windows}) != len(windows):
        raise ValueError("Historical window period IDs must be unique")
    values = []
    parameters = {}
    for index, window in enumerate(windows):
        keys = {
            "id": f"period_id_{index}",
            "label": f"period_label_{index}",
            "start": f"start_day_{index}",
            "end": f"end_day_{index}",
            "duration": f"duration_days_{index}",
        }
        values.append("(:{id}, :{label}, :{start}, :{end}, :{duration})".format(**keys))
        parameters.update({
            keys["id"]: window.period_id,
            keys["label"]: window.period_label,
            keys["start"]: window.start_day,
            keys["end"]: window.end_day,
            keys["duration"]: window.duration_days,
        })
    query = text(f"""
        WITH population AS (
            SELECT DISTINCT household_key FROM dbt_dev.fct_sales
        ), periods(period_id,period_label,start_day,end_day,duration_days) AS (
            VALUES {", ".join(values)}
        ), household_window_sales AS (
            SELECT s.household_key,p.period_id,
                   SUM(s.sales_value)::numeric AS window_spend
            FROM dbt_dev.fct_sales s
            JOIN periods p ON s.transaction_day BETWEEN p.start_day AND p.end_day
            GROUP BY s.household_key,p.period_id
        )
        SELECT pop.household_key,p.period_id,p.period_label,
               p.start_day,p.end_day,p.duration_days,
               COALESCE(hws.window_spend,0)::numeric AS window_spend
        FROM population pop
        CROSS JOIN periods p
        LEFT JOIN household_window_sales hws
          ON hws.household_key=pop.household_key AND hws.period_id=p.period_id
        ORDER BY p.start_day,pop.household_key
    """)
    with readonly_connection(engine) as connection:
        return pd.read_sql_query(query, connection, params=parameters)


def fetch_promotion_quality(engine: Engine) -> dict:
    """Fetch compact promotion coverage/conflict aggregates from dbt marts."""

    query = text("""
        WITH key_quality AS (
            SELECT COUNT(*)::bigint AS aggregated_product_store_week_keys,
                   COALESCE(SUM(source_state_count),0)::bigint AS source_rows_represented,
                   COALESCE(SUM(source_state_count-1),0)::bigint AS extra_source_rows_at_repeated_keys,
                   COUNT(*) FILTER (WHERE source_state_count>1)::bigint AS keys_with_multiple_source_rows,
                   COUNT(*) FILTER (WHERE display_state_count>1 OR mailer_state_count>1)::bigint
                       AS keys_with_conflicting_promotion_states,
                   MIN(week_no) AS first_promotion_week,
                   MAX(week_no) AS last_promotion_week,
                   COUNT(DISTINCT week_no)::integer AS promotion_weeks
            FROM dbt_dev.fct_promotion_week
        ), line_quality AS (
            SELECT COUNT(*)::bigint AS sales_lines,
                   COUNT(*) FILTER (WHERE has_promotion_record)::bigint AS lines_with_promotion_record,
                   COUNT(*) FILTER (WHERE NOT has_promotion_record)::bigint AS lines_without_promotion_record,
                   COUNT(*) FILTER (WHERE has_conflicting_promotion_states)::bigint
                       AS matched_lines_on_conflicting_keys
            FROM dbt_dev.fct_sales_promotion
        )
        SELECT * FROM key_quality CROSS JOIN line_quality
    """)
    with readonly_connection(engine) as connection:
        row = pd.read_sql_query(query, connection).iloc[0]
    return row.to_dict()
