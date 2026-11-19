# What: checks the project source and citation URLs without downloading datasets.
# Why: the submission should distinguish accessible sources from unverified ones.
# Viva: a reachable page is not, by itself, a redistribution licence.
from concurrent.futures import ThreadPoolExecutor
from datetime import date
import hashlib
import json
from pathlib import Path
import re

import requests

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data/interim/submission_link_checks.json"


def check(item):
    url, in_manifest = item
    result = None
    try:
        response = requests.head(url, allow_redirects=True, timeout=18)
        if response.status_code in (403, 405, 501):
            response = requests.get(url, headers={"Range": "bytes=0-0"}, stream=True, timeout=18)
        result = {"url": url, "status": response.status_code, "final_url": response.url}
        response.close()
        if not in_manifest and 200 <= result["status"] < 300:
            response = requests.get(url, stream=True, timeout=30)
            if response.ok:
                digest, size = hashlib.sha256(), 0
                for chunk in response.iter_content(chunk_size=65536):
                    digest.update(chunk)
                    size += len(chunk)
                result.update(content_type=response.headers.get("Content-Type", ""), size_bytes=size, sha256=digest.hexdigest())
            else:
                result["status"] = response.status_code
            response.close()
        return result
    except requests.RequestException as error:
        if result is not None:
            result["content_error"] = type(error).__name__
            return result
        return {"url": url, "status": "unreachable", "error": type(error).__name__}


def main():
    sources = list((ROOT / "docs").glob("*.md")) + list((ROOT / "reports/tables").glob("*.csv")) + [ROOT / "README.md", ROOT / "data/README.md", ROOT / "app/prototype.html"]
    manifest_urls = {entry["url"] for entry in json.loads((ROOT / "data/raw/MANIFEST.json").read_text(encoding="utf-8"))}
    urls = set(manifest_urls)
    for source in sources:
        urls.update(match.rstrip(".,;\"'") for match in re.findall(r"https?://[^\s)<>\]`,\"']+", source.read_text(encoding="utf-8")) if not match.startswith("http://localhost"))
    urls.update(["https://www.pbs.gov.pk/data-dissemination/", "https://www.pbs.gov.pk/wp-content/uploads/2020/07/Data-Dissemination-Policy.pdf", "https://www.pbs.gov.pk/result-excel/", "https://www.pbs.gov.pk/labour-force-statistics/"])
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(check, [(url, url in manifest_urls) for url in sorted(urls)]))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"checked_on": date.today().isoformat(), "results": results}, indent=2), encoding="utf-8")
    for result in results:
        print(result["status"], result["url"])


if __name__ == "__main__":
    main()
