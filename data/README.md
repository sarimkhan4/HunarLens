# Data sources and access

Accessed 2026-11-15. Original URLs, file sizes and SHA-256 hashes are recorded in the ignored `data/raw/MANIFEST.json`.

## Labour Force Survey 2024–25

Source: [PBS Labour Force Statistics](https://www.pbs.gov.pk/labour-force-statistics/). PBS describes the LFS as a household sample survey; its [2024–25 coding scheme](https://www.pbs.gov.pk/wp-content/uploads/2020/07/CODING-SCHEME-LFS-2024-25.pdf) describes selected primary sampling units and households. The Stata archive contains 325,445 records and 167 fields. The questionnaire, coding scheme and annual report were also downloaded.

The Stata schema contains a field labelled household member name (`S4C2`) as well as household and sampling identifiers. Raw files are excluded from Git. No de-identified analysis dataset has been created, and no claim is made that identifiers have been removed from the raw source.

## Population and Housing Census 2023

Source: [PBS detailed Census results](https://pbs.gov.pk/result-excel/), Table 1, downloaded as ten national, provincial, district and Islamabad workbooks. PBS describes the 2023 exercise as its first digital population and housing census; these files are published aggregate tables, not individual census records. No identifiers were removed by this project from the aggregate files.

## Terms and limitations

PBS's [data dissemination page](https://www.pbs.gov.pk/data-dissemination/) describes licensing and confidentiality principles, while an [older PBS policy document](https://www.pbs.gov.pk/wp-content/uploads/2020/07/Data-Dissemination-Policy.pdf) states restrictions on redistribution of supplied microdata. The specific licence applicable to these files and the status of the newer policy need confirmation with PBS. Public accessibility alone does not establish permission to redistribute; keep all raw files out of Git.
