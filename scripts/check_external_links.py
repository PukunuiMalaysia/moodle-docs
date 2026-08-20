#!/usr/bin/env python3
"""Check external links and fail only for stable not-found responses."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


MARKDOWN_URL = re.compile(r"(?<!!)\[[^\]]+\]\((https?://[^)\s]+)(?:\s+[^)]*)?\)")
STABLE_FAILURES = frozenset({404, 410})


class ExternalURLParser(HTMLParser):
    """Collect rendered external links without auditing page metadata."""

    def __init__(self) -> None:
        super().__init__()
        self.urls: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value for key, value in attrs if value is not None}
        if tag.lower() == "link" and "canonical" in values.get("rel", "").lower().split():
            return
        for attribute in ("href", "src"):
            value = values.get(attribute, "")
            if value.startswith(("http://", "https://")):
                self.urls.add(value.replace("&amp;", "&"))


def extract_urls(path: Path) -> set[str]:
    """Extract external links from Markdown or rendered HTML."""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".html", ".htm"}:
        parser = ExternalURLParser()
        parser.feed(text)
        return parser.urls
    return {match.group(1).replace("&amp;", "&") for match in MARKDOWN_URL.finditer(text)}


def collect_urls(paths: list[Path]) -> dict[str, list[Path]]:
    """Collect unique URLs and the files that reference them."""
    collected: dict[str, list[Path]] = {}
    for root in paths:
        candidates = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in candidates:
            if not path.is_file() or path.suffix.lower() not in {".md", ".markdown", ".html", ".htm"}:
                continue
            for url in extract_urls(path):
                collected.setdefault(url, []).append(path)
    return collected


def classify_status(status: int) -> str:
    """Classify an HTTP response as ok, stable error, or transient warning."""
    if status in STABLE_FAILURES:
        return "error"
    if 200 <= status < 400:
        return "ok"
    return "warning"


def check_url(url: str, *, timeout: float = 20.0, retries: int = 2) -> tuple[str, str]:
    """Check one URL with bounded retries and conservative failure handling."""
    request = Request(
        url,
        headers={
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.8,*/*;q=0.5",
            "User-Agent": "PukunuiDocsLinkCheck/1.0 (+https://pukunuimalaysia.github.io/moodle-docs/)",
        },
        method="GET",
    )
    last_warning = "request failed"
    for attempt in range(retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                status = response.status
            classification = classify_status(status)
            return classification, f"HTTP {status}"
        except HTTPError as error:
            classification = classify_status(error.code)
            if classification == "error":
                return classification, f"HTTP {error.code}"
            last_warning = f"HTTP {error.code}"
        except (URLError, TimeoutError, OSError) as error:
            last_warning = str(getattr(error, "reason", error))
        if attempt < retries:
            time.sleep(0.5 * (attempt + 1))
    return "warning", last_warning


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Markdown or HTML files/directories")
    parser.add_argument("--workers", type=int, default=8, help="maximum concurrent requests")
    parser.add_argument("--timeout", type=float, default=20.0, help="per-request timeout")
    parser.add_argument("--retries", type=int, default=2, help="retries after transient failures")
    return parser.parse_args()


def main() -> int:
    """Check discovered links and report stable failures separately."""
    args = parse_args()
    collected = collect_urls(args.paths)
    if not collected:
        print("No external links found")
        return 0
    errors: list[str] = []
    warnings: list[str] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        checks = {
            url: executor.submit(
                check_url, url, timeout=args.timeout, retries=max(0, args.retries)
            )
            for url in sorted(collected)
        }
        for url, future in checks.items():
            classification, detail = future.result()
            locations = ", ".join(str(path) for path in collected[url])
            message = f"{url} ({detail}; {locations})"
            if classification == "error":
                errors.append(message)
            elif classification == "warning":
                warnings.append(message)
    for message in warnings:
        print(f"WARNING {message}", file=sys.stderr)
    for message in errors:
        print(f"ERROR {message}", file=sys.stderr)
    if errors:
        print(
            f"External link check failed: {len(errors)} stable failure(s), {len(warnings)} warning(s)",
            file=sys.stderr,
        )
        return 1
    print(f"External link check passed: {len(collected)} URL(s), {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
