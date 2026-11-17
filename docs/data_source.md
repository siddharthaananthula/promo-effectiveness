# Data source, attribution and publication boundary

This analysis uses dunnhumby's *The Complete Journey* sample dataset, obtained separately from the official [dunnhumby Source Files page](https://www.dunnhumby.com/source-files/). That page describes *The Complete Journey* as a representation of household transactions and customer attributes and lists advanced classroom work and academic research on direct marketing among its intended uses.

The [Retail Performance Analytics data-source note](https://github.com/siddharthaananthula/retail-performance-analytics/blob/main/docs/data_source.md) identifies the same dataset, links to its source page, keeps original CSVs local and records that redistribution rights were not cleared there. Promo Effectiveness extends that project's PostgreSQL/dbt foundation and follows its practical portfolio publication approach: provide source attribution and publish aggregate analysis while excluding raw and processed row-level data.

## Terms and limits

The current official Source Files page does not state a dataset-specific license or explicitly grant redistribution rights for *The Complete Journey* data or derived results. The page's currently linked [User Guide](https://assets.ctfassets.net/psj0p18eh7z1/2SYO8T89Pxfd65nr6HQEbR/ce6c475e1bf15d503141bbd1fcc3b0a2/Let_s-Get-Sort-of-Real-User-Guide-dunnhumby.pdf) documents *Let's Get Sort-of-Real*, a different dataset. The general [dunnhumby Terms & Conditions](https://www.dunnhumby.com/terms-and-conditions/) discuss limited use of website materials and reserve other rights, but the pages reviewed do not clearly resolve the downloaded Complete Journey dataset or its derived analytical outputs.

This project follows the same practical aggregate-publication approach as Retail Performance Analytics, with attribution and clear limitations. That practice is not represented as an explicit license or written permission from dunnhumby. The project does not assert public-domain, CC BY or other redistribution rights. If the terms attached to the exact downloaded copy prohibit publication of aggregate outputs, those terms govern and the outputs must be removed. For clarification, contact `sourcefiles@dunnhumby.com`.

## Data handling

- Raw CSVs, processed row-level data, database files and credentials are not included.
- The notebook uses the existing PostgreSQL `retail_analytics` database and `dbt_dev` reporting models from the Retail Performance Analytics foundation. Queries use the project's read-only SQLAlchemy connection.
- Assignment, recorded coupon redemption and verified exposure are distinct measures. The source does not provide verified media-delivery exposure for this analysis.
- This data attribution does not license the project code. No code license has been selected.
