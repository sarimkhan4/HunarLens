# What: generates the submission source catalogue from the recorded download manifest.
# Why: source URLs, sizes and checksums should not be manually transcribed.
# Viva: a link check confirms access at one time, not a redistribution licence.
from datetime import date
import json
from pathlib import Path
from urllib.parse import unquote, urlparse

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/raw/MANIFEST.json"
CHECKS = ROOT / "data/interim/submission_link_checks.json"


def source_name(filename):
    names = {"LFS-2024-25-STATA.zip": "Labour Force Survey 2024–25 Stata microdata",
             "CODING-SCHEME-LFS-2024-25.pdf": "LFS 2024–25 coding scheme",
             "Questionnaire-of-LFS-2024-25-Final.pdf": "LFS 2024–25 questionnaire",
             "LFS-2024-25-Annual-Report.pdf": "LFS 2024–25 Annual Report"}
    return names.get(filename, "Census 2023 Table 1: " + filename)


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks = json.loads(CHECKS.read_text(encoding="utf-8"))
    statuses = {item["url"]: item["status"] for item in checks["results"]}
    pd.DataFrame(checks["results"]).to_csv(ROOT / "reports/tables/submission_link_checks.csv", index=False)
    pbs_landing = next(url for url in statuses if url.endswith("/labour-force-statistics/"))
    census_landing = next(url for url in statuses if url == "https://www.pbs.gov.pk/result-excel/")
    old_policy = next(url for url in statuses if url.endswith("/Data-Dissemination-Policy.pdf"))
    new_policy = next(url for url in statuses if url.endswith("/data-dissemination/"))
    lines = ["# Data sources and licences", "",
             f"HTTP checks: {checks['checked_on']}; a status outside the successful range or a timeout is flagged. A reachable URL does not establish redistribution rights.", "",
             f"The [older PBS policy]({old_policy}) states: “The user shall acknowledge the source of data and supply copies of the research work/articles (published/unpublished) to PBS.” It also describes restrictions on onward supply of data. The [current PBS dissemination page]({new_policy}) describes open licensing for classified products; the licence and interaction of the policies for these particular files remain **VERIFY with PBS**. Redistribution permission for each file has not been established.", "",
             "## Datasets and survey documentation", "",
             "The source URL, access date, size and SHA-256 in each entry below are read directly from the local download manifest. `python scripts/00_download_data.py` discovers and downloads these resources from PBS landing pages.", ""]
    for item in manifest:
        name = source_name(item["file"])
        census = item["file"].startswith("table_1_")
        use = ("Census aggregate geography and contextual lookup; district workbooks were downloaded for audit, not district matching." if census else
               "Survey label and youth skills analysis; raw person records are not redistributed." if item["file"].endswith(".zip") else
               "Survey coding, questionnaire routing or published methodology and reproduction checks.")
        year = "2023 census; publication year VERIFY" if census else "2024–25 survey; publication year VERIFY"
        lines += [f"### {name}", "", f"- Publisher: Pakistan Bureau of Statistics. Period/year: {year}.",
                  f"- Use: {use}", f"- Landing page: {census_landing if census else pbs_landing}",
                  f"- Direct download: {item['url']} (HTTP {statuses.get(item['url'], 'not checked')}).",
                  f"- Accessed: {item['access_date']}; format: {Path(item['file']).suffix.lstrip('.').upper()}; size: {item['size_bytes']:,} bytes; SHA-256: `{item['sha256']}`.",
                  "- Terms: specific redistribution licence unverified; do not include the raw file in the submission.",
                  f"- Suggested citation: Pakistan Bureau of Statistics. {name}. {item['url']} (accessed {item['access_date']}).",
                  "- Download: `python scripts/00_download_data.py`.", ""]
    manifest_urls = {item["url"] for item in manifest}
    lines += ["## Reference documents and other cited resources", "", "These references are linked for methodology or context; they are not downloaded by `scripts/00_download_data.py`. Where retrieval succeeds, the checker hashes the response bytes without saving a local copy; website responses can change. Publication year and redistribution terms are marked unverified where not established. An automated HTTP failure can reflect bot restrictions and does not establish that a browser cannot reach the source.", ""]
    for item in checks["results"]:
        url = item["url"]
        if url in manifest_urls:
            continue
        host = urlparse(url).netloc.lower()
        publisher = ("Pakistan Bureau of Statistics" if "pbs.gov.pk" in host else "International Labour Organization / ILOSTAT" if "ilo.org" in host else "European Training Foundation" if "etf.europa.eu" in host else "NAVTTC / National Skills Information System" if "skillingpakistan.gov.pk" in host else host)
        label = unquote(urlparse(url).path.rstrip("/").split("/")[-1]) or host
        status = item["status"]
        flag = "" if isinstance(status, int) and 200 <= status < 400 else " **VERIFY: automated check failed**"
        description = (f"format: {item.get('content_type', 'unknown')}; size: {item['size_bytes']:,} bytes; SHA-256: `{item['sha256']}` (the response observed on the check date)."
                       if item.get("sha256") else "format: page or PDF; size and SHA-256 unavailable because the automated check did not retrieve the content.")
        lines += [f"### {label}", "", f"- Publisher: {publisher}; publication year: n.d. / VERIFY; use: methodology, survey audit, source landing page or contextual reference.",
                  f"- Landing/direct URL: {url}; HTTP status: {status}.{flag}",
                  f"- Accessed: {checks['checked_on']}; {description} Terms of reuse: VERIFY.",
                  f"- Suggested citation: {publisher}, {label}, n.d., {url} (accessed {checks['checked_on']}).",
                  "- Acquisition: open the link; not acquired by the project downloader.", ""]
    lines += ["## Submission boundaries", "", "Included, subject to the dry-run review: small aggregate report tables, `data/processed/census_lookup.csv`, `data/processed/rare_combinations.csv` and `models/score_quantiles.json`. Raw microdata and person-level processed files are excluded for confidentiality and because the applicable redistribution terms remain unverified. The intermediate data and local virtual environment are also excluded.", ""]
    (ROOT / "DATA_SOURCES.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated DATA_SOURCES.md with {len(manifest)} manifest entries and {len(checks['results'])} checked links.")


if __name__ == "__main__":
    main()
