# Reproduce the Promo Effectiveness calculations

## Required shared data foundation

This repository contains the Promo analysis, not a separate retail data platform. To reproduce database-backed calculations, you need access to a PostgreSQL `retail_analytics` database with the existing `dbt_dev` reporting models from [Retail Performance Analytics](https://github.com/siddharthaananthula/retail-performance-analytics). This project reads those models; it does not create a database or container, load source CSVs, run `dbt build`, or modify models. The shared upstream project is the source of truth for the loader and dbt definitions.

The dataset must be obtained separately from dunnhumby and used under the terms that apply to that exact copy. See [data source and publication boundary](data_source.md). No raw data or credentials are included here.

## Python dependencies and tests

Use the existing compatible `retail-dbt` Python interpreter on the current workstation, or an equivalent Python environment on another workstation. In VS Code, select the kernel associated with that interpreter. Do not copy a workstation-specific virtual-environment path into the repository.

From the repository root in PowerShell, set `$Python` to the interpreter path already registered for `retail-dbt`, then install the analysis requirements and run the database-independent unit tests:

```powershell
$Python = '<path-to-existing-retail-dbt>\Scripts\python.exe'
& $Python -m pip install -r requirements-analysis.txt
& $Python -m unittest discover -s tests -v
```

The pinned requirements cover the analysis modules and notebook runtime. SVG charts use the Python standard library. The reused pipeline dependencies are maintained in the upstream repository, not duplicated here.

## Database credentials and read-only access

Create `secrets/retail-analytics.env` locally and populate it with your own authorized values. The directory is ignored by Git. Never place credentials in a notebook cell, source file, command shared with others or report.

```text
POSTGRES_USER=<local database user>
POSTGRES_PASSWORD=<local password>
POSTGRES_DB=retail_analytics
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

Host and port default to the values shown. The connection helper hides the password from its representation, configures PostgreSQL transactions as read-only and explicitly marks each query transaction read-only. Larger sales and promotion tables are aggregated in SQL before returning summaries to Python.

Run the historical power calculation from the repository root after configuring credentials and confirming the shared database is available:

```powershell
& $Python scripts/experiment_power_scenarios.py
```

The script reads three historical 42-day windows from `dbt_dev.fct_sales`. The same households recur in each window. The pooled household-window SD is descriptive only; the power scenarios use the largest single-window cross-household SD and do not treat repeated household windows as independent people. These sample-derived values are planning illustrations, not Endeavour statistics or verified pre-assignment outcomes.

## Notebook and publication status

The validated notebook and its aggregate outputs are included at `notebooks/01_promo_effectiveness.ipynb`; the summary charts and results documents are included alongside it. Outputs contain campaign-level and group-level summaries, not household IDs or raw transaction records. The publication approach and dataset terms caveat are recorded in [data source and publication notes](data_source.md) and the [publication manifest](publication_manifest.md).

The analysis is descriptive: assignment is targeting, redemption is recorded coupon use, and verified household exposure is not observed. The non-assigned group is not randomized. Do not interpret spending gaps as impact, uplift or a difference-in-differences estimate. The randomised holdout described in this repository is a proposal only; no experiment has been run.
