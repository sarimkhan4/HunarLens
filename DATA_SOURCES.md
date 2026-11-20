# Data sources and licences

The latest 60-second URL checks, including failed and incomplete retrievals, are recorded in [source_link_recheck.md](docs/source_link_recheck.md).

HTTP checks: 2026-11-19; a status outside the successful range or a timeout is flagged. A reachable URL does not establish redistribution rights.

The [older PBS policy](https://www.pbs.gov.pk/wp-content/uploads/2020/07/Data-Dissemination-Policy.pdf) states: “The user shall acknowledge the source of data and supply copies of the research work/articles (published/unpublished) to PBS.” It also describes restrictions on onward supply of data. The [current PBS dissemination page](https://www.pbs.gov.pk/data-dissemination/) describes open licensing for classified products; the licence and interaction of the policies for these particular files remain **VERIFY with PBS**. Redistribution permission for each file has not been established.

## Datasets and survey documentation

The source URL, access date, size and SHA-256 in each entry below are read directly from the local download manifest. `python scripts/00_download_data.py` discovers and downloads these resources from PBS landing pages.

### Labour Force Survey 2024–25 Stata microdata

- Publisher: Pakistan Bureau of Statistics. Period/year: 2024–25 survey; publication year VERIFY.
- Use: Survey label and youth skills analysis; raw person records are not redistributed.
- Landing page: https://www.pbs.gov.pk/labour-force-statistics/
- Direct download: https://www.pbs.gov.pk/wp-content/uploads/2020/07/LFS-2024-25-STATA.zip (HTTP 200).
- Accessed: 2026-11-15; format: ZIP; size: 9,243,553 bytes; SHA-256: `9757b798cdf8d7bc8322e28c9452fb1f7825b3e547410cbd53c6089a5ae7c363`.
- Terms: specific redistribution licence unverified; do not include the raw file in the submission.
- Suggested citation: Pakistan Bureau of Statistics. Labour Force Survey 2024–25 Stata microdata. https://www.pbs.gov.pk/wp-content/uploads/2020/07/LFS-2024-25-STATA.zip (accessed 2026-11-15).
- Download: `python scripts/00_download_data.py`.

### LFS 2024–25 coding scheme

- Publisher: Pakistan Bureau of Statistics. Period/year: 2024–25 survey; publication year VERIFY.
- Use: Survey coding, questionnaire routing or published methodology and reproduction checks.
- Landing page: https://www.pbs.gov.pk/labour-force-statistics/
- Direct download: https://www.pbs.gov.pk/wp-content/uploads/2020/07/CODING-SCHEME-LFS-2024-25.pdf (HTTP 200).
- Accessed: 2026-11-15; format: PDF; size: 20,345 bytes; SHA-256: `5d352841b2da5d6f3734ae7662ae7f75890f06eddaf0c0c30f37115bf3ede617`.
- Terms: specific redistribution licence unverified; do not include the raw file in the submission.
- Suggested citation: Pakistan Bureau of Statistics. LFS 2024–25 coding scheme. https://www.pbs.gov.pk/wp-content/uploads/2020/07/CODING-SCHEME-LFS-2024-25.pdf (accessed 2026-11-15).
- Download: `python scripts/00_download_data.py`.

### LFS 2024–25 questionnaire

- Publisher: Pakistan Bureau of Statistics. Period/year: 2024–25 survey; publication year VERIFY.
- Use: Survey coding, questionnaire routing or published methodology and reproduction checks.
- Landing page: https://www.pbs.gov.pk/labour-force-statistics/
- Direct download: https://www.pbs.gov.pk/wp-content/uploads/2020/07/Questionnaire-of-LFS-2024-25-Final.pdf (HTTP 200).
- Accessed: 2026-11-15; format: PDF; size: 1,070,589 bytes; SHA-256: `446b6baeacf7bdb4b744be59cb9348c5b30be8324934cc43ab4cc429f4b248d1`.
- Terms: specific redistribution licence unverified; do not include the raw file in the submission.
- Suggested citation: Pakistan Bureau of Statistics. LFS 2024–25 questionnaire. https://www.pbs.gov.pk/wp-content/uploads/2020/07/Questionnaire-of-LFS-2024-25-Final.pdf (accessed 2026-11-15).
- Download: `python scripts/00_download_data.py`.

### LFS 2024–25 Annual Report

- Publisher: Pakistan Bureau of Statistics. Period/year: 2024–25 survey; publication year VERIFY.
- Use: Survey coding, questionnaire routing or published methodology and reproduction checks.
- Landing page: https://www.pbs.gov.pk/labour-force-statistics/
- Direct download: https://www.pbs.gov.pk/wp-content/uploads/2020/07/LFS-2024-25-Annual-Report.pdf (HTTP 200).
- Accessed: 2026-11-15; format: PDF; size: 9,425,530 bytes; SHA-256: `79950b81ce4d738d48ff64f5e192f7905b112724a71b5d3018f4ff5991a57d48`.
- Terms: specific redistribution licence unverified; do not include the raw file in the submission.
- Suggested citation: Pakistan Bureau of Statistics. LFS 2024–25 Annual Report. https://www.pbs.gov.pk/wp-content/uploads/2020/07/LFS-2024-25-Annual-Report.pdf (accessed 2026-11-15).
- Download: `python scripts/00_download_data.py`.

### Census 2023 Table 1: table_1_national.xlsx

- Publisher: Pakistan Bureau of Statistics. Period/year: 2023 census; publication year VERIFY.
- Use: Census aggregate geography and contextual lookup; district workbooks were downloaded for audit, not district matching.
- Landing page: https://www.pbs.gov.pk/result-excel/
- Direct download: https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_national.xlsx (HTTP 200).
- Accessed: 2026-11-15; format: XLSX; size: 12,843 bytes; SHA-256: `a15954fb456881e7cdb3cd02692183f949a6b46085a9ca8a0df18bb970b62fc6`.
- Terms: specific redistribution licence unverified; do not include the raw file in the submission.
- Suggested citation: Pakistan Bureau of Statistics. Census 2023 Table 1: table_1_national.xlsx. https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_national.xlsx (accessed 2026-11-15).
- Download: `python scripts/00_download_data.py`.

### Census 2023 Table 1: table_1_kp_province.xlsx

- Publisher: Pakistan Bureau of Statistics. Period/year: 2023 census; publication year VERIFY.
- Use: Census aggregate geography and contextual lookup; district workbooks were downloaded for audit, not district matching.
- Landing page: https://www.pbs.gov.pk/result-excel/
- Direct download: https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_kp_province.xlsx (HTTP 200).
- Accessed: 2026-11-15; format: XLSX; size: 33,690 bytes; SHA-256: `dafb290645875d03b23af7d983b89a2677f5e6e27c6c41daaeb48df438fa2b09`.
- Terms: specific redistribution licence unverified; do not include the raw file in the submission.
- Suggested citation: Pakistan Bureau of Statistics. Census 2023 Table 1: table_1_kp_province.xlsx. https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_kp_province.xlsx (accessed 2026-11-15).
- Download: `python scripts/00_download_data.py`.

### Census 2023 Table 1: table_1_kp_districts.xlsx

- Publisher: Pakistan Bureau of Statistics. Period/year: 2023 census; publication year VERIFY.
- Use: Census aggregate geography and contextual lookup; district workbooks were downloaded for audit, not district matching.
- Landing page: https://www.pbs.gov.pk/result-excel/
- Direct download: https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_kp_districts.xlsx (HTTP 200).
- Accessed: 2026-11-15; format: XLSX; size: 62,461 bytes; SHA-256: `8c869da97389e7dd4b58ff59b9fc249acab4578197125ce66f028c8a72e4c432`.
- Terms: specific redistribution licence unverified; do not include the raw file in the submission.
- Suggested citation: Pakistan Bureau of Statistics. Census 2023 Table 1: table_1_kp_districts.xlsx. https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_kp_districts.xlsx (accessed 2026-11-15).
- Download: `python scripts/00_download_data.py`.

### Census 2023 Table 1: table_1_punjab_province.xlsx

- Publisher: Pakistan Bureau of Statistics. Period/year: 2023 census; publication year VERIFY.
- Use: Census aggregate geography and contextual lookup; district workbooks were downloaded for audit, not district matching.
- Landing page: https://www.pbs.gov.pk/result-excel/
- Direct download: https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_punjab_province.xlsx (HTTP 200).
- Accessed: 2026-11-15; format: XLSX; size: 30,093 bytes; SHA-256: `3eb7f99dd49c00598b2ea56ce32c13282d85cc4fc4d79dcb94cd21c77436752a`.
- Terms: specific redistribution licence unverified; do not include the raw file in the submission.
- Suggested citation: Pakistan Bureau of Statistics. Census 2023 Table 1: table_1_punjab_province.xlsx. https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_punjab_province.xlsx (accessed 2026-11-15).
- Download: `python scripts/00_download_data.py`.

### Census 2023 Table 1: table_1_punjab_districts.xlsx

- Publisher: Pakistan Bureau of Statistics. Period/year: 2023 census; publication year VERIFY.
- Use: Census aggregate geography and contextual lookup; district workbooks were downloaded for audit, not district matching.
- Landing page: https://www.pbs.gov.pk/result-excel/
- Direct download: https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_punjab_districts.xlsx (HTTP 200).
- Accessed: 2026-11-15; format: XLSX; size: 69,003 bytes; SHA-256: `e082a05c5485908a3fba22392ae222db084458842e26704b4193352ed768a074`.
- Terms: specific redistribution licence unverified; do not include the raw file in the submission.
- Suggested citation: Pakistan Bureau of Statistics. Census 2023 Table 1: table_1_punjab_districts.xlsx. https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_punjab_districts.xlsx (accessed 2026-11-15).
- Download: `python scripts/00_download_data.py`.

### Census 2023 Table 1: table_1_sindh_province.xlsx

- Publisher: Pakistan Bureau of Statistics. Period/year: 2023 census; publication year VERIFY.
- Use: Census aggregate geography and contextual lookup; district workbooks were downloaded for audit, not district matching.
- Landing page: https://www.pbs.gov.pk/result-excel/
- Direct download: https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_sindh_province.xlsx (HTTP 200).
- Accessed: 2026-11-15; format: XLSX; size: 33,411 bytes; SHA-256: `8cbcf72f5c3c0f52d944a6f2dbec907a19e4f5e2f31f5e61fad56ddffa1674c9`.
- Terms: specific redistribution licence unverified; do not include the raw file in the submission.
- Suggested citation: Pakistan Bureau of Statistics. Census 2023 Table 1: table_1_sindh_province.xlsx. https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_sindh_province.xlsx (accessed 2026-11-15).
- Download: `python scripts/00_download_data.py`.

### Census 2023 Table 1: table_1_sindh_districts.xlsx

- Publisher: Pakistan Bureau of Statistics. Period/year: 2023 census; publication year VERIFY.
- Use: Census aggregate geography and contextual lookup; district workbooks were downloaded for audit, not district matching.
- Landing page: https://www.pbs.gov.pk/result-excel/
- Direct download: https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_sindh_districts.xlsx (HTTP 200).
- Accessed: 2026-11-15; format: XLSX; size: 62,483 bytes; SHA-256: `082e7a735e782ece2380d50f204ee29b1b0222fddbcd772b3d80c073b1757734`.
- Terms: specific redistribution licence unverified; do not include the raw file in the submission.
- Suggested citation: Pakistan Bureau of Statistics. Census 2023 Table 1: table_1_sindh_districts.xlsx. https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_sindh_districts.xlsx (accessed 2026-11-15).
- Download: `python scripts/00_download_data.py`.

### Census 2023 Table 1: table_1_balochistan_province.xlsx

- Publisher: Pakistan Bureau of Statistics. Period/year: 2023 census; publication year VERIFY.
- Use: Census aggregate geography and contextual lookup; district workbooks were downloaded for audit, not district matching.
- Landing page: https://www.pbs.gov.pk/result-excel/
- Direct download: https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_balochistan_province.xlsx (HTTP 200).
- Accessed: 2026-11-15; format: XLSX; size: 28,911 bytes; SHA-256: `58c773b722499fd7bf8d839ac87e24b6016c0f753d8e805772d4c20e22793708`.
- Terms: specific redistribution licence unverified; do not include the raw file in the submission.
- Suggested citation: Pakistan Bureau of Statistics. Census 2023 Table 1: table_1_balochistan_province.xlsx. https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_balochistan_province.xlsx (accessed 2026-11-15).
- Download: `python scripts/00_download_data.py`.

### Census 2023 Table 1: table_1_balochistan_districts.xlsx

- Publisher: Pakistan Bureau of Statistics. Period/year: 2023 census; publication year VERIFY.
- Use: Census aggregate geography and contextual lookup; district workbooks were downloaded for audit, not district matching.
- Landing page: https://www.pbs.gov.pk/result-excel/
- Direct download: https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_balochistan_districts.xlsx (HTTP 200).
- Accessed: 2026-11-15; format: XLSX; size: 61,693 bytes; SHA-256: `318c7182f180b83aa272a9087ed8f62cb3712f85e2f2958c14291ad9a7b797db`.
- Terms: specific redistribution licence unverified; do not include the raw file in the submission.
- Suggested citation: Pakistan Bureau of Statistics. Census 2023 Table 1: table_1_balochistan_districts.xlsx. https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_balochistan_districts.xlsx (accessed 2026-11-15).
- Download: `python scripts/00_download_data.py`.

### Census 2023 Table 1: table_1_islamabad.xlsx

- Publisher: Pakistan Bureau of Statistics. Period/year: 2023 census; publication year VERIFY.
- Use: Census aggregate geography and contextual lookup; district workbooks were downloaded for audit, not district matching.
- Landing page: https://www.pbs.gov.pk/result-excel/
- Direct download: https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_islamabad.xlsx (HTTP 200).
- Accessed: 2026-11-15; format: XLSX; size: 15,913 bytes; SHA-256: `99faf74186fd0c7699ba5df008ed927f5cb4533383715785aad0e23d5e1b22b5`.
- Terms: specific redistribution licence unverified; do not include the raw file in the submission.
- Suggested citation: Pakistan Bureau of Statistics. Census 2023 Table 1: table_1_islamabad.xlsx. https://www.pbs.gov.pk/wp-content/uploads/2020/07/table_1_islamabad.xlsx (accessed 2026-11-15).
- Download: `python scripts/00_download_data.py`.

## Reference documents and other cited resources

These references are linked for methodology or context; they are not downloaded by `scripts/00_download_data.py`. Where retrieval succeeds, the checker hashes the response bytes without saving a local copy; website responses can change. Publication year and redistribution terms are marked unverified where not established. An automated HTTP failure can reflect bot restrictions and does not establish that a browser cannot reach the source.

### hunar-lens.streamlit.app

- Publisher: hunar-lens.streamlit.app; publication year: n.d. / VERIFY; use: Public dashboard deployment; not an external survey dataset.
- Landing/direct URL: https://hunar-lens.streamlit.app/; HTTP status: 200.
- Accessed: 2026-11-19; format: text/html; charset=utf-8; size: 9,782 bytes; SHA-256: `6233840e10d815a87ca8fcc1886c5258f48b11770eb70c5a6d42149688866609` (the response observed on the check date). Terms of reuse: VERIFY.
- Suggested citation: hunar-lens.streamlit.app, hunar-lens.streamlit.app, n.d., https://hunar-lens.streamlit.app/ (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

### only-half-of-workers-worldwide-hold-jobs-corresponding-to-their-level-of-education

- Publisher: International Labour Organization / ILOSTAT; publication year: n.d. / VERIFY; use: Statistical and normative education–occupation mismatch methods.
- Landing/direct URL: https://ilostat.ilo.org/blog/only-half-of-workers-worldwide-hold-jobs-corresponding-to-their-level-of-education/; (Opens in Browser) (accessed: 2026-11-19).
- Terms of reuse: VERIFY.
- Suggested citation: International Labour Organization / ILOSTAT, only-half-of-workers-worldwide-hold-jobs-corresponding-to-their-level-of-education, n.d., https://ilostat.ilo.org/blog/only-half-of-workers-worldwide-hold-jobs-corresponding-to-their-level-of-education/ (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

### result-excel

- Publisher: Pakistan Bureau of Statistics; publication year: n.d. / VERIFY; use: Official Census results landing page.
- Landing/direct URL: https://pbs.gov.pk/result-excel/; HTTP status: 200.
- Accessed: 2026-11-19; format: text/html; charset=UTF-8; size: 1,975,745 bytes; SHA-256: `6b18ebe2e1cc4759346cad8d80ad1f9781893031536acbc40aa768f0dc8cfef0` (the response observed on the check date). Terms of reuse: VERIFY.
- Suggested citation: Pakistan Bureau of Statistics, result-excel, n.d., https://pbs.gov.pk/result-excel/ (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

### Skills Trend Analysis.pdf

- Publisher: tevtreform.jobs.gov.pk; publication year: n.d. / VERIFY; use: Source or methodological reference; VERIFY precise use.
- Landing/direct URL: https://tevtreform.jobs.gov.pk/wp-content/uploads/downloads/governance/Skills%20Trend%20Analysis.pdf; HTTP status: 200.
- Accessed: 2026-11-19; format: application/pdf; size: 3,111,097 bytes; SHA-256: `a95bec7e89b7a7f71f61951423258480e65f4ee2c1df7b4e9c6fac08556ca57b` (the response observed on the check date). Terms of reuse: VERIFY.
- Suggested citation: tevtreform.jobs.gov.pk, Skills Trend Analysis.pdf, n.d., https://tevtreform.jobs.gov.pk/wp-content/uploads/downloads/governance/Skills%20Trend%20Analysis.pdf (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

### ILO_PAPI_LFS_VARIABLE_DERIVATION_GUIDE (A1V2).pdf

- Publisher: International Labour Organization / ILOSTAT; publication year: n.d. / VERIFY; use: ILO labour-force and future-starter derivation guidance.
- Landing/direct URL: https://webapps.ilo.org/ilostat-files/LFS/ILO_PAPI_LFS_VARIABLE_DERIVATION_GUIDE%20%28A1V2%29.pdf; HTTP status: 200.
- Accessed: 2026-11-19; format: application/pdf; size: 726,281 bytes; SHA-256: `0afe9649a57b73d98096ea4d662551d5882ca8ba079618792ec4b5807e469032` (the response observed on the check date). Terms of reuse: VERIFY.
- Suggested citation: International Labour Organization / ILOSTAT, ILO_PAPI_LFS_VARIABLE_DERIVATION_GUIDE (A1V2).pdf, n.d., https://webapps.ilo.org/ilostat-files/LFS/ILO_PAPI_LFS_VARIABLE_DERIVATION_GUIDE%20%28A1V2%29.pdf (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

### skills-mismatch-measurement-etf-partner-countries

- Publisher: European Training Foundation; publication year: n.d. / VERIFY; use: Skills mismatch measurement guidance and limitations.
- Landing/direct URL: https://www.etf.europa.eu/en/publications-and-resources/publications/skills-mismatch-measurement-etf-partner-countries; HTTP status: 200.
- Accessed: 2026-11-19; format: text/html; charset=UTF-8; size: 63,529 bytes; SHA-256: `0075e0bada5ba2bd96d23dabfa1dff44e0a4ff9676fe2be50531a62550355a2d` (the response observed on the check date). Terms of reuse: VERIFY.
- Suggested citation: European Training Foundation, skills-mismatch-measurement-etf-partner-countries, n.d., https://www.etf.europa.eu/en/publications-and-resources/publications/skills-mismatch-measurement-etf-partner-countries (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

### data-dissemination

- Publisher: Pakistan Bureau of Statistics; publication year: n.d. / VERIFY; use: Current PBS data-dissemination and licensing description.
- Landing/direct URL: https://www.pbs.gov.pk/data-dissemination/; HTTP status: 200.
- Accessed: 2026-11-19; format: text/html; charset=UTF-8; size: 211,732 bytes; SHA-256: `1d7f650e4b3741762e29d1a98be7e6edb864ac7094a009643a71645716323cb2` (the response observed on the check date). Terms of reuse: VERIFY.
- Suggested citation: Pakistan Bureau of Statistics, data-dissemination, n.d., https://www.pbs.gov.pk/data-dissemination/ (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

### labour-force-statistics

- Publisher: Pakistan Bureau of Statistics; publication year: n.d. / VERIFY; use: Official LFS download and publication landing page.
- Landing/direct URL: https://www.pbs.gov.pk/labour-force-statistics/; HTTP 200 and complete retrieval on the 60-second recheck. The earlier download timed out.
- Accessed: 2026-11-19; format: web page; size: 1,365,941 bytes; SHA-256: `0733a9c7fb9bf7c5698b05edac5ffe420cf4463dfb07c91029e374a09f67cfa3`. Terms of reuse: VERIFY.
- Suggested citation: Pakistan Bureau of Statistics, labour-force-statistics, n.d., https://www.pbs.gov.pk/labour-force-statistics/ (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

### result-excel

- Publisher: Pakistan Bureau of Statistics; publication year: n.d. / VERIFY; use: Official Census results landing page.
- Landing/direct URL: https://www.pbs.gov.pk/result-excel/; HTTP status: 200.
- Accessed: 2026-11-19; format: text/html; charset=UTF-8; size: 1,975,745 bytes; SHA-256: `f16e48c05ec2fe7cd863fb2847053ceba480cb466c9e36bcc6ca4e5a8341899d` (the response observed on the check date). Terms of reuse: VERIFY.
- Suggested citation: Pakistan Bureau of Statistics, result-excel, n.d., https://www.pbs.gov.pk/result-excel/ (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

### Data-Dissemination-Policy.pdf

- Publisher: Pakistan Bureau of Statistics; publication year: n.d. / VERIFY; use: Older PBS data-access and onward-supply policy.
- Landing/direct URL: https://www.pbs.gov.pk/wp-content/uploads/2020/07/Data-Dissemination-Policy.pdf; HTTP status: 200.
- Accessed: 2026-11-19; format: application/pdf; size: 128,224 bytes; SHA-256: `97957a6fa85e443f47e9fc7b140dedd94740e6639350faea148fa69f25acf4ea` (the response observed on the check date). Terms of reuse: VERIFY.
- Suggested citation: Pakistan Bureau of Statistics, Data-Dissemination-Policy.pdf, n.d., https://www.pbs.gov.pk/wp-content/uploads/2020/07/Data-Dissemination-Policy.pdf (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

### Employment-Trend-Report-2025-Final.pdf

- Publisher: Pakistan Bureau of Statistics; publication year: n.d. / VERIFY; use: PBS historical labour-market context.
- Landing/direct URL: https://www.pbs.gov.pk/wp-content/uploads/2020/07/Employment-Trend-Report-2025-Final.pdf; HTTP status: 200.
- Accessed: 2026-11-19; format: application/pdf; size: 2,652,541 bytes; SHA-256: `b44ee7bc9f1293227c1ed058f682870e962015776604f9c9e11ba3e01a842530` (the response observed on the check date). Terms of reuse: VERIFY.
- Suggested citation: Pakistan Bureau of Statistics, Employment-Trend-Report-2025-Final.pdf, n.d., https://www.pbs.gov.pk/wp-content/uploads/2020/07/Employment-Trend-Report-2025-Final.pdf (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

### MANUAL-of-LFS2024-25-1.pdf

- Publisher: Pakistan Bureau of Statistics; publication year: n.d. / VERIFY; use: Survey enumerator and variable-routing audit.
- Landing/direct URL: https://www.pbs.gov.pk/wp-content/uploads/2020/07/MANUAL-of-LFS2024-25-1.pdf; HTTP status: 200.
- Accessed: 2026-11-19; format: application/pdf; size: 2,640,319 bytes; SHA-256: `077bef543c7b383bfaf715f13debff802be84b13d194169908116f01729a0a90` (the response observed on the check date). Terms of reuse: VERIFY.
- Suggested citation: Pakistan Bureau of Statistics, MANUAL-of-LFS2024-25-1.pdf, n.d., https://www.pbs.gov.pk/wp-content/uploads/2020/07/MANUAL-of-LFS2024-25-1.pdf (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

### Occuptions-Classification-4-digits.pdf

- Publisher: Pakistan Bureau of Statistics; publication year: n.d. / VERIFY; use: Occupation classification audit and version comparison.
- Landing/direct URL: https://www.pbs.gov.pk/wp-content/uploads/2020/07/Occuptions-Classification-4-digits.pdf; HTTP status: 200.
- Accessed: 2026-11-19; format: application/pdf; size: 372,301 bytes; SHA-256: `328c0786bb7344176ccabcb7e4c39d1f848149f9c2797037dd8f911701c38c96` (the response observed on the check date). Terms of reuse: VERIFY.
- Suggested citation: Pakistan Bureau of Statistics, Occuptions-Classification-4-digits.pdf, n.d., https://www.pbs.gov.pk/wp-content/uploads/2020/07/Occuptions-Classification-4-digits.pdf (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

### Report-15.pdf

- Publisher: Pakistan Bureau of Statistics; publication year: n.d. / VERIFY; use: PBS labour-force participation and unemployment by age and sex.
- Landing/direct URL: https://www.pbs.gov.pk/wp-content/uploads/2020/07/Report-15.pdf; HTTP status: 200.
- Accessed: 2026-11-19; format: application/pdf; size: 150,493 bytes; SHA-256: `84c9f3c9c36ba0e8a5e7b7c7446213970df87a925a33a7478c66ae11aa4eccdd` (the response observed on the check date). Terms of reuse: VERIFY.
- Suggested citation: Pakistan Bureau of Statistics, Report-15.pdf, n.d., https://www.pbs.gov.pk/wp-content/uploads/2020/07/Report-15.pdf (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

### Report-17.pdf

- Publisher: Pakistan Bureau of Statistics; publication year: n.d. / VERIFY; use: PBS occupation distribution used for weighted reproduction.
- Landing/direct URL: https://www.pbs.gov.pk/wp-content/uploads/2020/07/Report-17.pdf; HTTP status: 200.
- Accessed: 2026-11-19; format: application/pdf; size: 323,543 bytes; SHA-256: `6a124659ea9657eb6ea469e67156a639b3ab3553223bcde23afdbed924cf85d9` (the response observed on the check date). Terms of reuse: VERIFY.
- Suggested citation: Pakistan Bureau of Statistics, Report-17.pdf, n.d., https://www.pbs.gov.pk/wp-content/uploads/2020/07/Report-17.pdf (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

### Report-7-3.pdf

- Publisher: Pakistan Bureau of Statistics; publication year: n.d. / VERIFY; use: PBS literacy and education distribution used for weighted reproduction.
- Landing/direct URL: https://www.pbs.gov.pk/wp-content/uploads/2020/07/Report-7-3.pdf; HTTP 200 and complete retrieval on the 60-second recheck. The earlier download timed out.
- Accessed: 2026-11-19; format: PDF; size: 346,086 bytes; SHA-256: `deab83c127e941f3c22d33106d275126b7f9e065f90dd50c9432ed1cad1b61a1`. Terms of reuse: VERIFY.
- Suggested citation: Pakistan Bureau of Statistics, Report-7-3.pdf, n.d., https://www.pbs.gov.pk/wp-content/uploads/2020/07/Report-7-3.pdf (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

### TechnicalVocational-Training-Course-Codes.pdf

- Publisher: Pakistan Bureau of Statistics; publication year: n.d. / VERIFY; use: Training-code audit and verified exclusions.
- Landing/direct URL: https://www.pbs.gov.pk/wp-content/uploads/2020/07/TechnicalVocational-Training-Course-Codes.pdf; HTTP status: 200.
- Accessed: 2026-11-19; format: application/pdf; size: 26,784 bytes; SHA-256: `1aa35ee171ce42c896ce6d869f140fd31d6f78cf9135c78bc8f0683f367ba1e9` (the response observed on the check date). Terms of reuse: VERIFY.
- Suggested citation: Pakistan Bureau of Statistics, TechnicalVocational-Training-Course-Codes.pdf, n.d., https://www.pbs.gov.pk/wp-content/uploads/2020/07/TechnicalVocational-Training-Course-Codes.pdf (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

### www.skillingpakistan.gov.pk

- Publisher: NAVTTC / National Skills Information System; publication year: n.d. / VERIFY; use: NAVTTC / NSIS employer-skill information as external context only.
- Landing/direct URL: https://www.skillingpakistan.gov.pk/; 
- Accessed: 2026-11-19; format: page or PDF; size and SHA-256 Terms of reuse: VERIFY.
- Suggested citation: NAVTTC / National Skills Information System, www.skillingpakistan.gov.pk, n.d., https://www.skillingpakistan.gov.pk/ (accessed 2026-11-19).
- Acquisition: open the link; not acquired by the project downloader.

## Submission boundaries

Included, subject to the dry-run review: small aggregate report tables, `data/processed/census_lookup.csv`, `data/processed/rare_combinations.csv` and `models/score_quantiles.json`. Raw microdata and person-level processed files are excluded for confidentiality and because the applicable redistribution terms remain unverified. The intermediate data and local virtual environment are also excluded.
