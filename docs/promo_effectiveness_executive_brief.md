# Executive brief: measuring Retail Media incrementality

**Decision requested:** Treat the current campaign data as descriptive only. Before making an incrementality or supplier-ROI claim, approve a prospective randomised holdout for one defined campaign package, subject to audience, suppression, logging and economics readiness.

## Evidence from this portfolio analysis

The figures use dunnhumby's public *The Complete Journey* sample and the repository's existing PostgreSQL/dbt reporting models; they are not any retailer's campaign results.

- The sample contains 30 campaigns, 2,500 purchasing households and 2.60 million transaction lines. Campaign and redemption validation found 2,318 recorded coupon events, 434 unique redeemers across all campaigns, and zero redemption-to-assignment mismatches. A redemption is not an exposure.
- Promotion records match **21.72%** of transaction lines; **78.28%** have unknown promotion status. Conflicting promotion states remain on 15,245 product-store-week keys, so an unmatched line must not be called unpromoted or unexposed.
- Campaign 26 has 332 assigned households, 31 recorded redeemers and 73 redemption events. Assigned households spent more on average than the non-assigned group before the campaign as well as during and after it. The groups are observational; these gaps and period changes are not campaign impact.
- Matching balanced 14 measured covariates for 277 pairs, but an independent historical spending-trend diagnostic remained materially different (slope SMD −1.053). Assignment timing and verified household exposure are unavailable. The observational causal design was rejected before effect estimation.

## Recommended next step

For an addressable campaign, randomise eligible, consented, linkable households 1:1 before delivery. Treatment receives a fixed campaign package; holdout is suppressed from that package but remains in business-as-usual. If shared store/geographic media cannot be suppressed by household, use enough randomised clusters and power for clustering. Keep all households in their assigned arm for intention-to-treat analysis, including delivery failures, crossovers and zero-purchase households.

Use total retailer sales per eligible household during a pre-registered 42-day campaign as the primary outcome, with a 28-day purchasing follow-up. Log eligibility, assignment time, delivery events, redemptions and transactions separately. Obtain product margin, retailer-funded discounts, media costs and supplier-funding terms before claiming profit or ROI.

## Power and readiness

An illustrative calculation from historical sample-dataset windows uses the largest single-window household-spend SD (247.47 dataset sales units). At two-sided α=0.05 and 80% power, a 10% relative MDE requires about **5,156 households**; a 5% MDE requires **20,622**. The power input is from one 2,500-household cross-section; the repeated-window rows are not counted as 7,500 independent households. Actual audience size, variability, clustering and data loss must be assessed before launch.

**Readiness:** design direction is clear; experiment launch is not yet approved. Confirm household suppression and identity linkage, eligible audience size, timestamped assignment and delivery logs, concurrent-campaign rules, privacy controls, and Finance-approved break-even economics. See the [full case study](promo_effectiveness_case_study.md) and [experiment proposal](experiment_design.md).
