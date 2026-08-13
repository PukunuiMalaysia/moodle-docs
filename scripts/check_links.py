#!/usr/bin/env python3
"""Check local links and generated assets in the built Jekyll site."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attribute = "href" if tag == "a" else "src" if tag in {"img", "script"} else None
        if not attribute:
            return
        for key, value in attrs:
            if key == attribute and value:
                self.links.append(value)


def target_for(site: Path, page: Path, link: str, baseurl: str) -> Path | None:
    split = urlsplit(link)
    if split.scheme or split.netloc or link.startswith(("mailto:", "tel:", "#")):
        return None
    path = unquote(split.path)
    if not path:
        return None
    if path.startswith(baseurl + "/"):
        target = site / path[len(baseurl) + 1 :]
    elif path.startswith("/"):
        return None
    else:
        target = page.parent / path
    if target.is_dir() or path.endswith("/"):
        target = target / "index.html"
    elif target.suffix.lower() in {".md", ".markdown"}:
        target = target.with_suffix(".html")
    elif not target.suffix:
        html = target.with_suffix(".html")
        if html.exists():
            target = html
    return target


def main() -> int:
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site").resolve()
    baseurl = sys.argv[2] if len(sys.argv) > 2 else "/moodle-docs"
    errors: list[str] = []
    for page in site.rglob("*.html"):
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for link in parser.links:
            target = target_for(site, page, link, baseurl)
            if target is not None and not target.exists():
                errors.append(f"{page.relative_to(site)}: {link}")
    if errors:
        print("Broken local links:", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Local link check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
