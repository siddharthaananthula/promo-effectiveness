# Promo Effectiveness methodology and decision history

This file curates the decisions specific to Promo Effectiveness. The local `DECISIONS.md` contains the Retail Performance Analytics history and is intentionally excluded from this focused repository. This project extends that repository's PostgreSQL/dbt foundation; shared models remain maintained upstream.

Figures in these decisions come from dunnhumby's public sample dataset, not retailer campaign data.

## 1. Treat the existing campaign records as descriptive

The analysis distinguishes household campaign assignment, recorded coupon redemption and verified exposure. Assignment indicates targeting, redemption indicates a recorded coupon-use event, and the available data do not verify delivery or exposure. Non-assigned households are not randomized controls. Do not infer incremental campaign impact from observed spending differences.

The validated sample has 30 campaign records, 2,318 coupon redemption events and no redemption-to-campaign-assignment mismatches. Campaign 26 has 332 assigned households, 31 unique redeemers and 73 redemption events. Event counts, unique redeemers and assignment counts remain separate.

## 2. Reject the observational causal design

Campaign screening used inclusive 28-day pre and post windows and retained zero-purchase households in baseline features. The initial screen found 25 of 30 campaigns met date coverage; campaigns 8, 13, 11 and 14 received early feasibility attention. The later all-campaign screen identified Campaign 26 as the strongest provisional design candidate, not as a performance winner. Although 277 unique pairs were formed and the 14 reported post-match covariate SMDs were below 0.10, an independent historical spending-trend diagnostic remained imbalanced (slope SMD −1.053). Assignment/notification timing and verified exposure were unavailable, and overlap exclusions could select on later campaign assignment.

**Decision:** stop before treatment-effect estimation. Do not report uplift or difference-in-differences results from this observational assignment data. Campaign 26 is a descriptive example, not a causal winner.

## 3. Use a descriptive campaign report

The notebook reports campaign duration, assigned-household counts, co-assignment and recorded coupon redemptions across all 30 campaigns. Campaign 26 provides the detailed example with 28-day pre/post windows and its 41-day scheduled period. Spending is scaled to a 28-day equivalent for duration comparability, and zero-purchase households remain in denominators.

Promotion data match 21.72% of transaction lines; the remainder have unknown promotion status. Repeated product-store-week records include conflicting promotion states. Do not classify unmatched sales as unpromoted or use these flags as verified household exposure.

## 4. Propose a prospective randomized holdout

The experiment proposal defines a prospective intention-to-treat design. Prefer household randomization when a fixed campaign can be suppressed at a stable household key across targeted channels. Consider store or geographic cluster randomization only when placement cannot be controlled by household and enough independent clusters are available. Assignment, delivery, redemption and transaction records must be logged separately. The proposal has not been implemented; no experimental outcome is reported.

The primary proposed metric is total retailer sales per eligible household during a pre-registered campaign window. Margin, retailer-funded discount, media cost and supplier-funding inputs are required before evaluating profit or ROI.

## 5. Correct the sample-size reference variance

The first power illustration incorrectly treated a pooled set of repeated historical household windows as the planning SD. The same 2,500 households appear in three 42-day windows. The pooled 7,500 household-window observations are not 7,500 independent households; pooled SD 240.75 is descriptive only.

The corrected sensitivity scenarios use the largest single-window cross-household SD, 247.47 dataset sales units, and an illustrative reference mean of 193.12. At two-sided α = 0.05 and 80% power, the normal-approximation totals are 20,622 households for a 5% relative MDE, 5,156 for 10%, and 2,292 for 15%. The estimated MDE for a 2,500-household frame is 27.73 units (14.36% of the reference mean). Assignment timing is unknown, and the scenarios omit clustering, attrition and treatment-delivery dilution.

## 6. Publish a focused extension

The portfolio repository includes the Promo-specific notebook, aggregate outputs, charts, reusable modules, tests, case study and proposed experiment. It excludes raw and processed row-level datasets, credentials, database files and the copied RPA dashboard/dbt pipeline. The source note credits dunnhumby and records that the official source page does not provide a dataset-specific license for derived results. Aggregate publication follows the practical attribution approach used by the upstream portfolio; it is not presented as explicit written permission from dunnhumby.
