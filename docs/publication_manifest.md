# Publication manifest

This manifest defines the focused Promo Effectiveness repository and its first local commit. The project owner has chosen the practical attributed-aggregate publication approach used by Retail Performance Analytics: publish the analysis narrative and aggregate outputs while excluding raw/processed row-level data, credentials and local database state. This is not a claim that dunnhumby issued a dataset-specific license for derived results; see [data_source.md](data_source.md).

## Exact first-commit file list (23 files)

Stage only these paths:

```text
.gitignore
README.md
requirements-analysis.txt
docs/data_source.md
docs/experiment_design.md
docs/figures/campaign26_observed_spending.svg
docs/figures/campaign_assignment_overlap.svg
docs/promo_effectiveness_case_study.md
docs/promo_effectiveness_decisions.md
docs/promo_effectiveness_executive_brief.md
docs/promo_effectiveness_reproduction.md
docs/publication_manifest.md
notebooks/01_promo_effectiveness.ipynb
scripts/experiment_power_scenarios.py
src/promo_effectiveness/__init__.py
src/promo_effectiveness/charts.py
src/promo_effectiveness/config.py
src/promo_effectiveness/descriptive.py
src/promo_effectiveness/extract.py
src/promo_effectiveness/power.py
src/promo_effectiveness/validation.py
tests/test_experiment_design.py
tests/test_promo_effectiveness.py
```

This is a focused analysis repository, not a copy of the raw-to-dashboard Retail Performance Analytics project. The notebook and Python package use that project's existing `retail_analytics` PostgreSQL database and populated `dbt_dev` models.

## Shared foundation to reuse, not duplicate

Retail Performance Analytics remains the source of truth for the database, dbt models and shared data pipeline. Promo Effectiveness uses that existing environment; it does not recreate dbt transformations. It requires access to a compatible `retail-dbt` Python environment and populated database. See [reproduction instructions](promo_effectiveness_reproduction.md).

The following copied local files are excluded and ignored so they are not swept into the focused commit:

```text
.github/workflows/dbt-quality.yml
compose.yaml
dbt/**
requirements-pipeline.txt
scripts/ingest.py
tests/integration/**
tests/test_fixture_ci.py
tests/test_ingest.py
```

The full local suite passed 39 tests. The first commit includes the 12 Promo-specific test cases in its two test modules. The other 27 cases exercise copied ingestion and fixture-CI code; those tests and their supporting files remain in the local workspace but are excluded from this focused commit as upstream duplicates.

## Excluded inherited portfolio material

These files remain local but do not belong in the Promo Effectiveness first commit:

```text
DECISIONS.md
data/raw/.gitkeep
data/processed/.gitkeep
docs/architecture.md
docs/assets/**
docs/business_insights.md
docs/dashboard_guide.md
docs/data_quality.md
docs/index.html
powerbi/**
screenshots/**
```

The seven root dashboard screenshots and the seven `docs/assets/screenshots/` copies are byte-identical to the original repository's screenshots. The three trend screenshots are also inherited dashboard material. The full `DECISIONS.md` mixes core-project history with Promo entries; project-specific decisions are curated in [promo_effectiveness_decisions.md](promo_effectiveness_decisions.md).

## Notebook and chart inspection

The saved notebook has 62 cells, 66 output objects and 39 rendered HTML tables. The tables contain campaign/group summaries or schema metadata. No output table has a `household_key` data column, no household identifier values or raw transaction records are displayed, and output text contains no database URI, password-shaped value or private-key material. The string `household_key` appears only as a schema field label. Six inline SVG outputs show group distributions or aggregate trends.

The two standalone SVG charts contain campaign-level assignment/co-assignment counts and Campaign 26 group quantiles. They show no household IDs, raw rows, external image references or scripts. Their plots summarize household-level observations without exposing individual records. All results remain descriptive; neither the notebook nor charts estimate uplift or claim a causal effect.

The repository includes no raw transaction/promotion CSVs, processed row-level exports, database files/dumps or PBIX/PBIT files. `.gitignore` excludes these along with secrets/environment files, local dbt profiles, keys/certificates, logs, caches and editor settings. The local `secrets/retail-analytics.env` and dbt profile are ignored; the secret file was not opened. The ignored profile uses environment-variable substitution and has no literal password.

## Dataset attribution and terms

The original [Retail Performance Analytics data-source note](https://github.com/siddharthaananthula/retail-performance-analytics/blob/main/docs/data_source.md) credits dunnhumby, links to Source Files, excludes raw CSVs and says dataset redistribution rights were not cleared there. Its public release is not evidence of permission for this project.

The official [dunnhumby Source Files page](https://www.dunnhumby.com/source-files/) describes *The Complete Journey* as intended for advanced classroom work and academic research on direct marketing. It does not state a dataset-specific license or explicitly authorize publication of derived analysis. Its currently linked [User Guide](https://assets.ctfassets.net/psj0p18eh7z1/2SYO8T89Pxfd65nr6HQEbR/ce6c475e1bf15d503141bbd1fcc3b0a2/Let_s-Get-Sort-of-Real-User-Guide-dunnhumby.pdf) covers *Let's Get Sort-of-Real*, a different dataset. The general [dunnhumby Terms & Conditions](https://www.dunnhumby.com/terms-and-conditions/) cover website materials, but the pages reviewed do not clearly resolve the downloaded *Complete Journey* archive or derived outputs. This project follows the chosen attribution-and-aggregate practice without representing it as a license or written permission. No CC BY or public-domain rights are asserted. The [data-source note](data_source.md) records this caveat and the contact for clarification.

## Original repository and sensitive-file audit

The original repository's ignore rules exclude raw/processed data, PBIX files, environment files and generated artefacts. They do not ignore `secrets/` or `dbt/profiles.yml`; the latter is Git-tracked and uses an environment-variable expression rather than a literal password. This is a configuration-hygiene weakness in the original project; no files there were changed. No PBIX was found in either repository. The copied dashboard screenshots are excluded here.

The Promo `.gitignore` excludes `secrets/`, environment files, local dbt profiles, raw/processed data, database files, logs, caches and Power BI binaries. `git check-ignore` confirmed the local credentials file and dbt profile are ignored. No credential values were opened or copied into source.

## Public repository structure

```text
README.md
requirements-analysis.txt
docs/
  data_source.md
  experiment_design.md
  figures/*.svg
  promo_effectiveness_case_study.md
  promo_effectiveness_decisions.md
  promo_effectiveness_executive_brief.md
  promo_effectiveness_reproduction.md
  publication_manifest.md
notebooks/01_promo_effectiveness.ipynb
scripts/experiment_power_scenarios.py
src/promo_effectiveness/*.py
tests/test_experiment_design.py
tests/test_promo_effectiveness.py
```

The project code has no separate license file. Choose a code license independently from dataset terms before inviting code reuse. No remote is configured; this is a local-commit plan only.
