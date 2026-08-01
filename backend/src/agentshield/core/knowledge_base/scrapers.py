"""
scrapers.py
-----------
STEP 8 of the RAG pipeline: Continuous Knowledge Base Ingestion (Task 2.2).

Purpose:
    Pull fresh threat intelligence and best-practice documentation
    automatically so the knowledge base doesn't go stale between
    manual PDF drops.

What's automated here:
    - NVD / CVE feed: NVD publishes a public REST API, so this is
      fully automatable — `refresh_nvd_feed()` pulls recently
      published/modified CVEs and writes them as one text file per
      CVE under data_scraped/nvd/. Set NVD_API_KEY in .env for a
      much higher rate limit; unauthenticated calls work too, just
      more slowly.
    - Generic doc downloader: `download_document()` pulls a single
      URL and saves it as plain text under data_scraped/<folder>/.
      Wired up in `run_all_scrapers()` for AWS/Azure/GCP/CIS, driven
      entirely by the URLs in settings.yaml's `ingestion.doc_sources`.

Important — read before filling in doc_sources in settings.yaml:
    AWS / Azure / GCP security best-practice guides and CIS
    Benchmarks are often distributed as licensed PDFs / gated
    downloads, and terms of use generally prohibit bulk scraping of
    those. `download_document()` will happily pull whatever URL
    you give it, so only point `doc_sources` at pages you're
    actually permitted to pull from — e.g. a public best-practices
    HTML page, not a gated benchmark PDF. Leaving a source blank in
    settings.yaml is the safe default; `download_document()` skips
    it and returns False rather than erroring.
    `download_document()` also saves `response.text` — that's fine
    for HTML/plain-text sources, but if you ever point a doc_source
    at a URL serving a PDF, you'll need separate binary-safe logic
    (write `response.content` to a `.pdf` and route it through
    loaders.load_single_pdf instead of load_single_text).
    `refresh_static_doc_folders()` separately reports which PDF
    folders under data/ have new/changed files since the last
    ingest, for the sources you refresh manually.

Add a new automated source by following the `download_document`
pattern: fetch -> save as plain text under data_scraped/<source>/ ->
let update_kb pick it up.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

import requests

from .cache import file_changed
from .config import (
    AWS_DOC_URL,
    AZURE_DOC_URL,
    CIS_DOC_URL,
    DATA_ROOT,
    GCP_DOC_URL,
    NVD_API_KEY,
    NVD_API_URL,
    NVD_RESULTS_PER_PAGE,
    SCRAPED_ROOT,
    SCRAPER_DAYS_BACK,
    SCRAPER_TIMEOUT,
    SUPPORTED_EXTENSIONS,
    USER_AGENT,
    VERIFY_SSL,
)

# Reused across every request in this module instead of opening a new
# TCP/TLS connection per call, and carries a consistent, config-driven
# User-Agent so we're identifiable to the APIs/sites we hit.
session = requests.Session()
session.headers.update(
    {
        "User-Agent": USER_AGENT
    }
)

# NVD API key is optional (unauthenticated calls work, just with a
# lower rate limit) — set NVD_API_KEY in .env to raise it. Never put
# the key itself in settings.yaml or in code.
if NVD_API_KEY:
    session.headers.update(
        {
            "apiKey": NVD_API_KEY
        }
    )

# Defined once so refresh_nvd_feed() doesn't rebuild this Path inline
# every call.
NVD_OUTPUT_DIR = SCRAPED_ROOT / "nvd"


def refresh_nvd_feed(
    days_back: int = SCRAPER_DAYS_BACK,
    max_results: int = NVD_RESULTS_PER_PAGE,
) -> int:
    """
    Pull CVEs published/modified in the last `days_back` days from
    the NVD REST API and write each as a plain-text file under
    data_scraped/nvd/, ready for loaders.load_all_scraped().

    Returns:
        Number of new/updated CVE files written.
    """

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days_back)

    params = {
        "lastModStartDate": start.strftime("%Y-%m-%dT%H:%M:%S.000"),
        "lastModEndDate": end.strftime("%Y-%m-%dT%H:%M:%S.000"),
        "resultsPerPage": max_results,
    }

    try:
        response = session.get(
            NVD_API_URL,
            params=params,
            timeout=SCRAPER_TIMEOUT,
            verify=VERIFY_SSL,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[scrapers] NVD fetch failed: {e}")
        return 0

    data = response.json()
    vulnerabilities = data.get("vulnerabilities", [])

    out_dir = NVD_OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    written = 0

    for entry in vulnerabilities:

        cve = entry.get("cve", {})
        cve_id = cve.get("id", "UNKNOWN-CVE")

        descriptions = cve.get("descriptions", [])
        english_desc = next(
            (d["value"] for d in descriptions if d.get("lang") == "en"),
            "No description available.",
        )

        metrics = cve.get("metrics", {})
        severity = _extract_severity(metrics)

        text = (
            f"CVE ID: {cve_id}\n"
            f"Severity: {severity}\n"
            f"Published: {cve.get('published', 'N/A')}\n"
            f"Last Modified: {cve.get('lastModified', 'N/A')}\n\n"
            f"Description:\n{english_desc}\n"
        )

        out_path = out_dir / f"{cve_id}.txt"

        try:
            out_path.write_text(text, encoding="utf-8")
        except OSError as e:
            print(f"[scrapers] Failed to write {out_path}: {e}")
            continue

        written += 1

    print(f"[scrapers] NVD refresh: wrote {written} CVE record(s) to {out_dir}")

    return written


def _extract_severity(metrics: Dict[str, Any]) -> str:
    """
    Best-effort extraction of a CVSS severity label across the
    various CVSS versions NVD may report (v3.1, v3.0, v2.0).
    """

    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):

        entries = metrics.get(key)

        if entries:
            return entries[0].get("cvssData", {}).get("baseSeverity", "UNKNOWN")

    return "UNKNOWN"


def download_document(
    url: str,
    folder: str,
) -> bool:
    """
    Download documentation from an optional source.
    """
    if not url:
        return False
    try:
        response = session.get(
            url,
            timeout=SCRAPER_TIMEOUT,
            verify=VERIFY_SSL,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(
            f"[scrapers] {folder} download failed: {e}"
        )
        return False

    output_dir = SCRAPED_ROOT / folder
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )
    output_file = output_dir / "latest.txt"

    try:
        output_file.write_text(
            response.text,
            encoding="utf-8",
        )
    except OSError as e:
        print(
            f"[scrapers] Failed to write {output_file}: {e}"
        )
        return False

    print(
        f"[scrapers] Updated {folder}"
    )
    return True


def refresh_static_doc_folders(data_root: Path = DATA_ROOT) -> Dict[str, List[str]]:
    """
    Report which files under data/<folder>/ are new or modified
    since the last ingest, without attempting to auto-scrape them.
    Use this output to flag "manual refresh needed" in a dashboard
    or scheduler log.
    """

    changed: Dict[str, List[str]] = {}

    if not data_root.exists():
        return changed

    for folder in sorted(data_root.iterdir()):

        if not folder.is_dir():
            continue

        stale_files = [
            str(pdf.relative_to(data_root))
            for pdf in folder.rglob("*.pdf")
            if file_changed(pdf)
        ]

        if stale_files:
            changed[folder.name] = stale_files

    return changed


def count_scraped_files() -> int:
    """
    Count how many scraped files (matching SUPPORTED_EXTENSIONS) are
    currently sitting under data_scraped/, across every source
    folder. Cheap sanity signal for the scheduler/dashboard: did the
    last run actually leave anything behind.
    """

    if not SCRAPED_ROOT.exists():
        return 0

    return sum(
        1
        for f in SCRAPED_ROOT.rglob("*")
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def run_all_scrapers() -> Dict[str, Any]:
    """
    Entry point the scheduler calls once a day: refresh every
    automatable source (NVD + any doc_sources URLs configured in
    settings.yaml), and report which static/manual folders need
    attention.
    """

    summary = {
        "aws_updated":
            download_document(
                AWS_DOC_URL,
                "aws",
            ),
        "azure_updated":
            download_document(
                AZURE_DOC_URL,
                "azure",
            ),
        "gcp_updated":
            download_document(
                GCP_DOC_URL,
                "gcp",
            ),
        "cis_updated":
            download_document(
                CIS_DOC_URL,
                "cis",
            ),
        "nvd_records_written":
            refresh_nvd_feed(),
        "static_folders_needing_refresh":
            refresh_static_doc_folders(),
        "scraped_file_count":
            count_scraped_files(),
        "run_at":
            datetime.now(
                timezone.utc
            ).isoformat(),
    }

    print(f"[scrapers] Run summary: {json.dumps(summary, indent=2)}")

    return summary


if __name__ == "__main__":
    run_all_scrapers()