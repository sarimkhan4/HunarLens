# Data sources and access

Source links, collection methods, recorded dates and terms are listed in [DATA_SOURCES.md](../DATA_SOURCES.md);

## Labour Force Survey 2024–25

Source: [PBS Labour Force Statistics](https://www.pbs.gov.pk/labour-force-statistics/). PBS describes the LFS as a household sample survey; its [2024–25 coding scheme](https://www.pbs.gov.pk/wp-content/uploads/2020/07/CODING-SCHEME-LFS-2024-25.pdf) describes selected primary sampling units and households. The Stata archive contains 325,445 records and 167 fields. The questionnaire, coding scheme and annual report were also downloaded.

The Stata schema contains a field labelled household member name (`S4C2`) as well as household and sampling identifiers. Raw files are excluded from Git and remain unmodified. The processed modelling dataset **has been created**: `scripts/build_modeling_dataset.py` exports only the 19 allowed predictors, `is_unemployed` and `group_id`. Names, addresses, phone numbers and original person identifiers do not enter that export. `src/hunarlens/data.py` creates the numeric household grouping key for splitting; it is not a predictor. Removing direct identifiers does not establish complete anonymisation, so person-level processed data also remains excluded from Git.

PBS collected the original household survey. The project acquired its official archive and supporting documents through `scripts/download_data.py`, which discovers links on the PBS landing page and records downloads in the manifest. The final model dataset has 26,653 eligible youth rows, as recorded in `reports/tables/row_waterfall.csv`.

## Population and Housing Census 2023

Source: [PBS detailed Census results](https://pbs.gov.pk/result-excel/), Table 1, downloaded as ten national, provincial, district and Islamabad workbooks. PBS describes the 2023 exercise as its first digital population and housing census; these files are published aggregate tables, not individual census records. No identifiers were removed by this project from the aggregate files.

The project downloads the official workbooks using `scripts/download_data.py`. Province workbooks supply the Census lookup used in modelling; downloading district workbooks does not mean district matching was used. `scripts/build_modeling_dataset.py` joins the lookup using `province` and `area`. The small aggregate `data/processed/census_lookup.csv` is retained for the app.

## Terms and limitations

See [DATA_SOURCES.md](../DATA_SOURCES.md) for the reviewed PBS policy links and source-specific reuse status. The documented category-level permissions do not settle the particular microdata file's classification or override file-specific conditions. Public accessibility alone does not establish permission to redistribute; raw and person-level files stay out of Git.
