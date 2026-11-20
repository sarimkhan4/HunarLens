# What: downloads the data acquisition files linked from official PBS pages.
# Why: files must come from the current PBS landing pages. Viva: links can change.
from html.parser import HTMLParser
from datetime import date
import hashlib
import json
from pathlib import Path
import zipfile
from urllib.error import URLError
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

LANDING_PAGES = (
    "https://www.pbs.gov.pk/labour-force-statistics/",
    "https://pbs.gov.pk/result-excel/",
)
TIMEOUT_SECONDS = 30
RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
LFS_FILES = {
    "lfs-2024-25-stata.zip", "coding-scheme-lfs-2024-25.pdf",
    "questionnaire-of-lfs-2024-25-final.pdf", "lfs-2024-25-annual-report.pdf",
}


class LinkParser(HTMLParser):
    """Collect links from the official pages without guessing file URLs."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)


def discover_links(page_url: str) -> list[str]:
    """Read a landing page before choosing any download links."""
    request = Request(page_url, headers={"User-Agent": "HunarLens/1.0"})
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        html = response.read().decode("utf-8", errors="replace")
    parser = LinkParser()
    parser.feed(html)
    return [urljoin(page_url, link) for link in parser.links]


def select_files(pages: list[list[str]]) -> list[str]:
    """Select named LFS resources and Census Table 1 from discovered links."""
    lfs = [link for link in pages[0] if Path(urlparse(link).path).name.lower() in LFS_FILES]
    census = [link for link in pages[1] if Path(urlparse(link).path).name.lower().startswith("table_1_") and link.lower().endswith(".xlsx")]
    selected = list(dict.fromkeys(lfs + census))
    if len({Path(urlparse(link).path).name.lower() for link in lfs}) != len(LFS_FILES) or len(census) < 5:
        raise ValueError("Required PBS links were not all found; inspect the landing pages manually.")
    return selected


def download(url: str) -> dict[str, str | int]:
    """Save one official file and return its provenance and checksum."""
    if urlparse(url).hostname not in {"pbs.gov.pk", "www.pbs.gov.pk"}:
        raise ValueError(f"Non-PBS download rejected: {url}")
    name = unquote(Path(urlparse(url).path).name)
    request = Request(url, headers={"User-Agent": "HunarLens/1.0"})
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        if urlparse(response.url).hostname not in {"pbs.gov.pk", "www.pbs.gov.pk"}:
            raise ValueError("Download redirected outside PBS.")
        content = response.read()
    path = RAW / name
    path.write_bytes(content)
    return {"file": name, "url": url, "access_date": date.today().isoformat(),
            "size_bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}


def extract_zip(path: Path) -> None:
    """Reject archive paths outside the raw directory before extraction."""
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            if not (RAW / member.filename).resolve().is_relative_to(RAW.resolve()):
                raise ValueError(f"Unsafe archive path: {member.filename}")
        archive.extractall(RAW)


def main() -> int:
    """Stop on network or extraction failures and retain the partial manifest."""
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = []
    try:
        links = select_files([discover_links(page) for page in LANDING_PAGES])
        for link in links:
            entry = download(link)
            manifest.append(entry)
            (RAW / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            print(f"Downloaded {entry['file']} ({entry['size_bytes']} bytes)")
            if str(entry["file"]).lower().endswith(".zip"):
                extract_zip(RAW / str(entry["file"]))
    except (OSError, URLError, ValueError, zipfile.BadZipFile) as error:
        print(f"PBS acquisition stopped: {error}")
        print("Download or extract the required PBS files manually into data/raw/.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
