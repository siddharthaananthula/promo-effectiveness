# Prospective Retail Media incrementality experiment

**Status:** proposal only. No experiment has been run. The existing retail dataset is used only to illustrate outcome variability for planning; no treatment effect or uplift is estimated.

## Executive experiment specification

| Item | Proposed specification |
|---|---|
| Business decision | Decide whether to scale a defined supplier-funded, retailer-addressable campaign package after measuring incremental retailer sales and its fully loaded economics. |
| Population | All unique, consented loyalty households eligible for that campaign under rules frozen before assignment, in supported channels and locations. Include eligible households with no prior-period purchases. |
| Randomisation | Household, 1:1, stratified by pre-period sales/activity and primary market or channel, where campaign delivery can be suppressed by household. |
| Treatment / holdout | Assignment to the complete specified campaign package / assignment to business-as-usual with that targeted package suppressed. |
| Primary estimand | Intention-to-treat (ITT): mean difference in total retailer sales per eligible household over the 42-day campaign window. All randomised households remain in their assigned arm. |
| Duration | 42 campaign days, followed by 28 days for purchasing and return/repeat diagnostics. Freeze eligibility and randomise before the first delivery. |
| Primary test | Two-sided 5% significance level, 80% power as the initial planning convention; report the ITT estimate and 95% confidence interval. Commercial minimum effect is to be set with Finance before launch. |
| Readiness gate | Confirm addressable suppression, stable household linkage, assignment and delivery logs, a sufficiently large eligible frame, margin/cost feeds, and no unresolvable competing campaign. |

This design addresses the evidence gap in the current portfolio data: targeting assignments are not verified exposure, recorded redemptions are not exposure, promotion records have incomplete transaction-line coverage, and non-assigned households are not randomised controls. A prospective holdout measures the effect of offering a defined media package under real operating conditions. It does not make past observational assignment data causal.

## 1. Decision, hypothesis and population

The decision is whether Endeavour should scale a specified, repeatable retail-media package for a defined supplier, product set, channel and audience. The protocol must name the creative, placement, offer, flight dates, frequency cap, eligible SKUs, stores/regions and delivery rules before assignment. Changing these during the test creates a different treatment.

The primary null is that assignment to the package does not change mean total retailer sales per eligible household during the campaign window. The primary alternative is a non-zero difference. A two-sided test avoids treating a potentially harmful sales change as impossible; the expected commercial direction can still be positive. The test does not establish profit unless margin and cost data are also complete.

The target population is the set of unique, consented and linkable loyalty households meeting written campaign eligibility rules at a fixed eligibility snapshot. Those rules may use information available before randomisation, such as product/category eligibility, channel reachability, market and pre-period activity. They must not depend on post-assignment delivery, redemption or purchasing. Include eligible households with zero observed sales. State clearly that results generalise to this eligible, measurable population, not necessarily to anonymous shoppers or all Endeavour customers.

## 2. Randomisation unit and groups

### Household randomisation (preferred when addressable)

Randomise a stable household/account key, not individual transactions, if the campaign can be suppressed across all targeted channels at that key. Assign households 1:1 to maximise power under equal costs and a fixed frame. Keep every linked household member in one arm. Stratify assignment using a short, frozen list of pre-randomisation variables (for example prior-period sales/activity, primary market/store group and eligible channel); record the allocation probability and randomisation seed/version. A reproducible hash-based assignment or a centrally audited randomisation service is acceptable.

The treatment group is assigned the complete targeted media package and is eligible for delivery. The holdout group receives normal business-as-usual activity but is suppressed from this package and any directly bundled targeted offer. The primary analysis remains by assignment even if delivery fails or a household does not redeem.

Household assignment is not appropriate if placement is visible to everyone in a store, the campaign cannot be suppressed across devices/accounts, linked household identities are unreliable, or one household's assignment changes another household's access. These are pre-launch feasibility checks, not reasons to remove crossovers after observing outcomes.

### Store or geographic cluster randomisation (when media is shared)

Use a store, non-overlapping geography or other delivery cluster when in-store media, local broadcast or other placement cannot be assigned at household level. Randomise enough independent clusters to both arms, stratifying or pairing on pre-period sales, store size, format and market using pre-test data. Households must be assigned analytically to a cluster using a rule frozen before treatment; cross-shopping and boundary exposure should be measured.

Cluster assignment reduces effective sample size. Before launch, estimate the intracluster correlation (ICC), cluster-size distribution and number of independent clusters, then power the design with the design effect `1 + (average cluster size - 1) * ICC` or, preferably, simulation using the actual cluster structure. Analyse at the randomised cluster level with small-sample-appropriate cluster-robust inference or randomisation inference. Many household records do not compensate for too few randomised clusters. If there are too few independent geographies/stores or severe spillovers, do not present the test as adequately powered; redesign as a longer phased or wait-list randomised rollout.

## 3. Estimand and metrics

Let `Z_h` be household `h`'s random assignment and `Y_h(z)` be its outcome under assignment `z`. The primary estimand is the finite-population ITT:

`mean_h[Y_h(1) - Y_h(0)]` among all eligible households randomised at baseline.

### Primary metric

**Total retailer sales per eligible household over the 42 campaign days**, calculated from transaction-level sales linked to the eligible household and aggregated before comparing arms. Specify with Finance whether the sales field is net of discounts, returns, tax and cancellations, and how online and in-store orders are deduplicated. A household with no linked purchase contributes zero only when transaction capture is known to be complete for that household/channel; missing linkage is a separate missing-data state, not zero.

### Secondary outcomes

- Sales and units for the pre-specified promoted product/SKU set.
- Sales for non-promoted products, other categories and the rest of the basket, to reveal substitution or basket expansion.
- Basket count/value, purchase incidence and repeat purchasing during the 28-day follow-up.
- Delivery/serve/send counts and timestamps, frequency, channel and delivery failures as implementation metrics.
- Recorded redemptions, reported only as redemption activity. Redemption is not exposure and is not an inclusion criterion.
- Contribution and profitability outcomes only if verified product margin, discounts, media costs and supplier-funding data are joined with agreed accounting rules.

The primary window and outcome hierarchy must be registered before the first assignment. Avoid choosing a favourable category or follow-up period after seeing results. Secondary outcomes should be labelled exploratory or adjusted for multiplicity if used for confirmatory claims.

## 4. Eligibility, timing and logging

1. **Pre-flight (before assignment):** agree the question, treatment bundle, eligible products, geography/channels, consent and privacy rules, deduplication key, outcome definition, minimum commercially meaningful effect, guardrails, analysis code and maximum acceptable contamination/missing-log rates. Check the holdout can actually be suppressed.
2. **Eligibility freeze:** create one row per eligible household with the rule version and snapshot timestamp. Use only pre-randomisation information. Do not remove households later for low delivery, no redemption, overlapping post-assignment campaigns or zero sales.
3. **Randomisation:** assign once before the first campaign activation. Store experiment/campaign IDs, pseudonymous household key, arm, assignment timestamp, allocation probability, stratum, randomisation algorithm/version, eligibility snapshot and any pre-existing competing campaign status. Do not use campaign start day as a proxy for assignment time.
4. **Delivery and exposure telemetry:** log assignment-to-channel mapping, attempted/sent/served/delivered/viewable events where supported, timestamps, placement, creative, frequency and delivery failure. Keep a coverage/status reason for every assigned treatment household. An impression, send or platform delivery is a recorded delivery event; it does not prove attention. Keep these fields distinct from assignment and coupon redemption.
5. **Treatment period:** run the fixed 42-day flight. Log campaign changes, outages, stock availability, price/promotion changes, media spend and every other campaign eligible for either arm. Use the same normal business-as-usual policies in both arms where possible.
6. **Follow-up:** continue outcome capture for 28 days after the flight. Freeze the extract only after agreed late transaction/return refreshes. The primary outcome remains the campaign window; follow-up is secondary.

No personal information should be placed in source code or the public analysis artefacts. Use governed pseudonymous IDs and approved linkage/access controls. Assignment and delivery logs should be access-controlled and retained only under the applicable policy.

## 5. Overlap, spillovers and missing delivery data

Identify planned competing campaigns before randomisation. Prefer a single isolated campaign slot or ensure business-as-usual competing activity follows the same rules in both arms. If multiple offers must run, either randomise within pre-specified competing-campaign eligibility strata or design a factorial test; do not silently exclude households based on campaign assignments that occur after randomisation. Log other campaign assignments and delivered media by arm.

Holdout suppression should cover all campaign channels and linked accounts. Track confirmed holdout delivery as contamination, treatment delivery failures as non-compliance, and cross-store/geographic exposure as spillover. Preserve all such households in their assigned arm for ITT. Report contamination and delivery rates by arm. Per-delivered or per-protocol comparisons are selected and are not the primary causal result; any complier effect would require a separately justified instrumental-variable estimand and assumptions.

Missing delivery records mean **unknown delivery**, not no exposure. Keep assignment records as the denominator, reconcile expected and received event counts, and publish telemetry completeness by channel and arm. If sales linkage is incomplete, quantify missingness by arm and channel and distinguish missing outcomes from genuine zero purchases. Define pre-launch stop/retest gates for logging completeness and control contamination. If those gates fail, report the ITT with the operational failure clearly and treat delivery-based interpretation as inconclusive; do not repair it by dropping affected households.

## 6. Illustrative sample-size assessment

### Data input and boundaries

The project queried the existing `dbt_dev.fct_sales` model read-only. It aggregated household sales, with zero-purchase households retained, over three consecutive 42-day historical windows ending before Campaign 26's scheduled start: transaction days **98–139**, **140–181** and **182–223**. Each window contains the same 2,500 households. Their means are 188.38, 197.28 and 193.72 dataset sales units per household; their cross-household sample standard deviations are 227.04, 247.19 and 247.47. The mean across these window means is **193.12**.

The pooled standard deviation across all 7,500 household-window rows is 240.75, but those rows are not 7,500 independent households: the same households recur in all three windows, and the windows have different means. It is therefore reported only as a pooled descriptive spread and is **not** used as the power input. Instead, the planning calculation uses the largest cross-household SD from one window, **247.47**. That input is a cross-sectional spread from one 2,500-household window; repeated rows are not treated as additional independent households. This is a conservative choice among these three windows, not a formal upper confidence bound or a guarantee about future variance. The earlier days 56–97 window has SD 181.78, signalling temporal/panel composition variation.

All figures are from the portfolio's existing retail dataset, not Endeavour Group statistics, a forecast, a target, or a treatment effect. Assignment/notification timestamps are unavailable, so even these pre-launch-scheduled windows are **not verified to precede assignment**. No Campaign 26 during/post sales or group differences enter the calculation. Because the same households recur, uncertainty around the historical variance estimate should not be calculated as if there were 7,500 independent units; a real protocol should use the current eligible Endeavour population and empirical or simulation-based power analysis.

### Method and scenarios

For a household-level, equal-allocation, independent two-arm difference in means, the module uses the normal approximation:

`n per arm = ceil(2 * (z[1-alpha/2] + z[power])^2 * sigma^2 / MDE^2)`.

The scenarios below use the illustrative mean 193.12 only to express MDEs as 5%, 10% or 15% of a reference 42-day sales value; the reference mean is not an assumed control outcome. Counts use sigma=247.47 and are households per arm and total; tests are two-sided. These are unadjusted independent-household counts. They do not include clustering, attrition/linkage loss, delivery non-compliance, finite population correction, or any precision gain from pre-period covariate adjustment.

| Relative MDE | Absolute MDE / household | Alpha | Power | Treatment n | Holdout n | Total n |
|---:|---:|---:|---:|---:|---:|---:|
| 5% | 9.66 | 0.05 | 80% | 10,311 | 10,311 | 20,622 |
| 5% | 9.66 | 0.05 | 90% | 13,803 | 13,803 | 27,606 |
| 5% | 9.66 | 0.01 | 80% | 15,342 | 15,342 | 30,684 |
| 5% | 9.66 | 0.01 | 90% | 19,546 | 19,546 | 39,092 |
| 10% | 19.31 | 0.05 | 80% | 2,578 | 2,578 | 5,156 |
| 10% | 19.31 | 0.05 | 90% | 3,451 | 3,451 | 6,902 |
| 10% | 19.31 | 0.01 | 80% | 3,836 | 3,836 | 7,672 |
| 10% | 19.31 | 0.01 | 90% | 4,887 | 4,887 | 9,774 |
| 15% | 28.97 | 0.05 | 80% | 1,146 | 1,146 | 2,292 |
| 15% | 28.97 | 0.05 | 90% | 1,534 | 1,534 | 3,068 |
| 15% | 28.97 | 0.01 | 80% | 1,705 | 1,705 | 3,410 |
| 15% | 28.97 | 0.01 | 90% | 2,172 | 2,172 | 4,344 |

If a future trial had only **2,500 eligible households** and split them 1:1, the normal approximation gives an 80%-power, 5%-alpha MDE of about **27.73 dataset sales units per household**, or **14.4%** of the illustrative reference mean. This is a size illustration using this dataset's household count; it says nothing about Endeavour's addressable audience. A 10% MDE would require 5,156 total households under these assumptions; a 5% MDE would require 20,622.

Reproduce the database input and scenario table from the repository root with the existing `retail-dbt` environment:

```powershell
$Python = 'S:\venvs\retail-dbt\Scripts\python.exe'
& $Python scripts/experiment_power_scenarios.py
```

The script uses `secrets/retail-analytics.env` through the existing secure loader, performs read-only queries against the existing dbt mart, prints only aggregate statistics, and never prints credential values. The calculation functions are in `src/promo_effectiveness/power.py`; their unit tests are in `tests/test_experiment_design.py`.

Before final protocol approval, replace this benchmark with a governed extract of the proposed Endeavour eligible population, the exact planned campaign window and endpoint; assess skew and outliers without post hoc exclusions; simulate the actual randomisation/strata; and increase counts for any cluster design, linkage loss or delivery dilution. Confirm whether the commercially useful MDE is attainable before launching.

## 7. Analysis plan and checks

- Publish the protocol, eligibility logic, outcomes, exclusions (all pre-randomisation), MDE, alpha, power, guardrails and decision thresholds before assignment.
- Validate one randomisation row per eligible household, no duplicate IDs across arms, correct allocation probabilities/strata and successful holdout suppression. Report arm counts and a descriptive balance table for pre-period sales, purchase frequency, recency, category activity, market/channel and available demographics. Randomisation checks diagnose implementation; do not use significance tests to re-randomise or drop households.
- Analyse by assigned arm (ITT). Estimate the difference in mean household-level sales with a 95% confidence interval. Use pre-specified randomisation-stratum fixed effects and a short list of pre-treatment covariates (e.g. prior-window sales, baskets, activity/recency, promoted-category sales) for precision. Do not use delivery, redemption, campaign-period behaviour or follow-up behaviour as adjustment/matching covariates.
- Use household-level heteroskedasticity-robust uncertainty for household randomisation. If randomisation is clustered, respect the cluster unit in inference and power; with few clusters use an appropriate small-sample method/randomisation inference.
- Report the unadjusted ITT alongside the covariate-adjusted ITT, sample sizes, standard errors, confidence intervals, zero-purchase share, data-linkage coverage, delivery and contamination rates. Any adjusted result is still an assignment effect, not an effect among exposed households.
- Treat prespecified secondary metrics as supportive; distinguish sales from margin/profit. Report missing outcomes, stock-outs, delivery outages, crossovers and campaign changes by arm.

## 8. Success and decision rules

Before launch, Finance and the campaign owner should set a minimum commercially worthwhile ITT and the fully loaded break-even contribution. Proposed decision logic:

- **Scale or expand to a monitored rollout** only if the primary ITT is positive with a 95% interval excluding zero, the point estimate meets the pre-agreed commercial threshold, net contribution is positive under verified accounting inputs, and customer/operational guardrails are acceptable.
- **Retest or refine** if the point estimate is directionally promising but uncertainty spans both no effect and the useful-effect threshold, or if delivery/holdout suppression quality misses pre-agreed gates without evidence of harm. Base a retest on the observed uncertainty and a revised power plan, not the favourable point estimate alone.
- **Stop or redesign** if the data credibly indicate a harmful primary outcome, economics remain below break-even, or the campaign cannot be delivered/logged with a valid holdout. An underpowered or operationally compromised result is inconclusive, not proof of no effect.

Do not set a numerical ROI threshold until campaign costs, margin and supplier-funding treatment are agreed. Do not make scale decisions on redemption counts, gross sales alone or a positive point estimate with a wide interval.

## 9. Profitability data required

To evaluate whether incremental sales create value, obtain product/store/time-specific gross margin or contribution margin and a documented mapping from each promoted SKU to that margin. Also capture:

- retailer-funded discounts, coupon liability, price markdowns, refunds/returns and any supplier-funded discount share;
- actual media delivery costs by placement/channel, agency/platform fees, creative/production and fulfilment costs where attributable;
- supplier media fees/funding, invoices, timing, contract terms and whether each amount is incremental revenue, reimbursement or cost offset;
- relevant incremental variable costs and a consistent tax/accounting basis.

Define net incremental contribution and break-even rules with Finance before the trial. Supplier funding must not be double-counted as both reduced campaign cost and additional revenue. Revenue-based ROAS is not profit or incrementality by itself.

## 10. Open questions and limitations

The current project cannot answer whether household targeting/suppression is technically available at Endeavour, the size and composition of an eligible campaign audience, the actual channel exposure rate, the correct randomisation cluster/ICC, the assignment timestamp, or the economic break-even threshold. It also cannot establish whether the current transaction/promotion data map to current Endeavour customer identifiers, prices, margins or media logs. These require confirmation from Retail Media, loyalty, campaign operations, data engineering, privacy and Finance owners.

This proposal is not a claim that any campaign is incremental or profitable. Current observational campaign assignment, coupon redemption and incomplete promotion records remain descriptive evidence only. No matching, uplift calculation or causal analysis of that dataset is part of Phase 5.
