# Promo Effectiveness

A retail campaign measurement case study and prospective experiment proposal. This focused Data Science project extends the PostgreSQL and dbt foundation from [Retail Performance Analytics](https://github.com/siddharthaananthula/retail-performance-analytics). It reuses that project's `retail_analytics` database and `dbt_dev` reporting models; the upstream repository remains the source of truth for shared infrastructure.

## Decision and evidence

The completed analysis supports descriptive reporting of campaign assignment, recorded coupon redemption, sales patterns and promotion-data coverage. It does not establish verified campaign exposure or incremental impact. The observational causal design was rejected, and the randomised holdout below is a proposal only. The sample is not Endeavour Group campaign data and this project does not measure Endeavour's actual performance.

The project follows the practical portfolio publication approach used by Retail Performance Analytics: attribute the sample source, publish aggregated analytical summaries, and exclude raw/processed row-level data and credentials. This is a publication practice, not a claim that dunnhumby has granted a specific license for derived results. See [data source and publication notes](docs/data_source.md).

## Portfolio deliverables

- [One-page executive brief](docs/promo_effectiveness_executive_brief.md)
- [Full case study](docs/promo_effectiveness_case_study.md)
- [Proposed randomised holdout experiment and power scenarios](docs/experiment_design.md)
- [Campaign assignment and co-assignment chart](docs/figures/campaign_assignment_overlap.svg)
- [Campaign 26 observed spending chart](docs/figures/campaign26_observed_spending.svg)
- [Validated notebook with aggregate outputs](notebooks/01_promo_effectiveness.ipynb)
- [Promo Effectiveness methodology and decision history](docs/promo_effectiveness_decisions.md)
- [Reproduction instructions](docs/promo_effectiveness_reproduction.md)
- [Publication manifest and file-scope audit](docs/publication_manifest.md)

The notebook distinguishes assignment, redemption and exposure, includes zero-purchase households, and retains the rejected causal-design audit. Campaign 26 spending comparisons are descriptive only. No experiment was conducted, no uplift was estimated, and no household-level source records are published.

## Code and tests

`src/promo_effectiveness/` contains secure read-only database configuration, SQL extraction, campaign validation, descriptive calculations, chart generation and power calculations. `scripts/experiment_power_scenarios.py` reproduces the sample-size scenarios from the existing reporting data. The committed tests focus on Promo calculations and experiment-design logic.

## Reproduce

Reproduction requires the existing Retail Performance Analytics PostgreSQL environment with the populated `dbt_dev` models. This project does not create a database or container, ingest source data, or rebuild dbt models. Set up an authorized local environment and credentials as described in the [reproduction guide](docs/promo_effectiveness_reproduction.md). Raw data, local profiles and credentials remain excluded.

## Dataset attribution and limitations

The analysis uses dunnhumby's *The Complete Journey* sample dataset, obtained separately from the [official Source Files page](https://www.dunnhumby.com/source-files/). The official page describes classroom and academic research uses but does not publish a dataset-specific license for derived outputs. The project records this uncertainty; see [data source and publication notes](docs/data_source.md).

The project code has no separate license declaration yet. The source-data terms and code licensing are separate matters.
