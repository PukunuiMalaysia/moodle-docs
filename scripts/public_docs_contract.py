#!/usr/bin/env python3
"""Validate the single-page public documentation contract for one or more products."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any

try:
    from scripts.image_checks import validate_image
except ModuleNotFoundError:  # Direct execution adds scripts/, not its parent, to sys.path.
    from image_checks import validate_image


PUBLIC_AVAILABILITIES = frozenset(
    {"commercial-active", "commercial-legacy", "pre-release", "public-free"}
)
MARKETPLACE_AVAILABILITIES = frozenset(
    {"commercial-active", "commercial-legacy", "public-free"}
)
PRODUCT_DOC_AVAILABILITIES = PUBLIC_AVAILABILITIES
REQUIRED_HEADINGS = (
    "Key features",
    "Screenshots",
    "Requirements",
    "Installation",
    "Configuration and use",
    "Privacy and permissions",
    "Troubleshooting",
    "Support and licence",
)
CATEGORY_ORDER = (
    "Blocks",
    "Activities",
    "Course formats",
    "Local plugins",
    "Reports",
    "Themes",
    "Related tools",
)
IMAGE_SUFFIXES = frozenset({".gif", ".jpeg", ".jpg", ".png", ".webp"})
FRONT_MATTER = re.compile(r"\A---\r?\n(?P<header>.*?)\r?\n---\r?\n", re.DOTALL)
H1 = re.compile(r"^# (?P<title>.+?)\s*$", re.MULTILINE)
H2 = re.compile(r"^## (?P<title>.+?)\s*$", re.MULTILINE)
IMAGE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<target>[^)\s]+)(?:\s+[^)]*)?\)")
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\((?P<target>https?://[^)\s]+)(?:\s+[^)]*)?\)")
KEBAB_IMAGE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\.(?:gif|jpe?g|png|webp)")
CANONICAL_SUPPORT_URL = "https://pukunui.com/location/malaysia/"
PRODUCT_ISSUE_URL = (
    "https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml"
)
DOCUMENTATION_ISSUE_URL = (
    "https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml"
)
BROWSER_STORES = {
    "chrome_tab_organizer": (
        "https://chromewebstore.google.com/detail/chrome-tab-organizer-prod/"
        "npiekcbklimcbgghdlomjmenhobmlbea"
    ),
    "quicknav-lms": (
        "https://chromewebstore.google.com/detail/quicknav-lms-by-pukunui/"
        "hdgmpngamakcijgdghonfkglggbbcjgg"
    ),
}
SPECIAL_CATEGORIES = {
    "chrome_tab_organizer": "Related tools",
    "quicknav-lms": "Related tools",
    "moodle-configurable_reports-custom_sql_queries": "Related tools",
}
PLUGIN_CATEGORIES = {
    "block": "Blocks",
    "format": "Course formats",
    "local": "Local plugins",
    "mod": "Activities",
    "report": "Reports",
    "theme": "Themes",
}


@dataclass
class ContractResult:
    """Validation findings and parsed navigation metadata."""

    repository: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    title: str | None = None
    category: str | None = None
    nav_order: int | None = None


def category_for_repository(repository: str) -> str | None:
    """Return the canonical navigation category for a repository."""
    if repository in SPECIAL_CATEGORIES:
        return SPECIAL_CATEGORIES[repository]
    match = re.fullmatch(r"moodle-([a-z]+)_.+", repository)
    if not match:
        return None
    return PLUGIN_CATEGORIES.get(match.group(1))


def marketplace_url(repository: str) -> str | None:
    """Return the canonical Marketplace URL for a Moodle plugin repository."""
    if repository in SPECIAL_CATEGORIES:
        return None
    if not repository.startswith("moodle-"):
        return None
    component = repository.removeprefix("moodle-")
    return f"https://marketplace.moodle.com/plugins/{component}"


def parse_simple_front_matter(header: str) -> tuple[dict[str, str], list[str]]:
    """Parse the contract's deliberately small scalar-only front matter."""
    values: dict[str, str] = {}
    errors: list[str] = []
    for line in header.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"([a-z_]+):\s*(.*?)\s*", line)
        if not match:
            errors.append(f"unsupported front matter line: {line}")
            continue
        key, value = match.groups()
        if key in values:
            errors.append(f"front matter defines {key} more than once")
            continue
        if len(value) >= 2 and value[0] == value[-1] == '"':
            try:
                decoded = json.loads(value)
            except json.JSONDecodeError:
                errors.append(f"front matter contains invalid quoted {key}")
                continue
            if not isinstance(decoded, str):
                errors.append(f"front matter {key} must be a string")
                continue
            value = decoded
        elif len(value) >= 2 and value[0] == value[-1] == "'":
            value = value[1:-1].replace("''", "'")
        values[key] = value.strip()
    return values, errors


def section(text: str, heading: str, next_heading: str | None) -> str:
    """Return the Markdown body between two required H2 headings."""
    start = re.search(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE)
    if not start:
        return ""
    body_start = start.end()
    if next_heading is None:
        return text[body_start:]
    end = re.search(
        rf"^## {re.escape(next_heading)}\s*$", text[body_start:], re.MULTILINE
    )
    return text[body_start : body_start + end.start()] if end else text[body_start:]


def normalized_image_target(target: str) -> PurePosixPath | None:
    """Return a safe relative image target or None."""
    if target.startswith(("/", "http://", "https://")):
        return None
    pure = PurePosixPath(target)
    if not pure.parts or pure.parts[0] != "images" or ".." in pure.parts:
        return None
    return pure


def validate_docs_tree(
    product_root: Path,
    repository: str,
    availability: str,
) -> ContractResult:
    """Validate one central product source against the single-page contract."""
    result = ContractResult(repository=repository)
    index = product_root / "index.md"

    if not product_root.is_dir() or product_root.is_symlink():
        result.errors.append("missing required central product directory")
        return result
    if not index.is_file() or index.is_symlink():
        result.errors.append("missing required central index.md")

    for path in sorted(product_root.rglob("*")):
        relative = path.relative_to(product_root)
        if path.is_symlink():
            result.errors.append(f"symlink is not allowed beneath central product content: {relative}")
            continue
        if path.is_dir():
            continue
        if relative == Path("index.md"):
            continue
        if (
            len(relative.parts) >= 2
            and relative.parts[:1] == ("images",)
            and path.suffix.lower() in IMAGE_SUFFIXES
        ):
            if not KEBAB_IMAGE.fullmatch(path.name):
                result.errors.append(f"image filename must be descriptive kebab-case: {relative}")
            image_errors, image_warnings = validate_image(path)
            result.errors.extend(f"{relative}: {error}" for error in image_errors)
            result.warnings.extend(f"{relative}: {warning}" for warning in image_warnings)
            continue
        result.errors.append(f"prohibited documentation file: {relative}")

    if not index.is_file() or index.is_symlink():
        return result
    try:
        text = index.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        result.errors.append("central index.md is not valid UTF-8")
        return result

    front_match = FRONT_MATTER.match(text)
    if not front_match:
        result.errors.append("index requires YAML front matter")
        return result
    front, front_errors = parse_simple_front_matter(front_match.group("header"))
    result.errors.extend(front_errors)
    required_front = {"title", "category", "nav_order"}
    missing_front = sorted(required_front - set(front))
    extra_front = sorted(set(front) - required_front)
    if missing_front:
        result.errors.append("missing front matter: " + ", ".join(missing_front))
    if extra_front:
        result.errors.append("unsupported front matter: " + ", ".join(extra_front))

    result.title = front.get("title") or None
    result.category = front.get("category") or None
    raw_nav = front.get("nav_order", "")
    if raw_nav.isdigit() and int(raw_nav) > 0 and int(raw_nav) % 10 == 0:
        result.nav_order = int(raw_nav)
    else:
        result.errors.append("nav_order must be a positive multiple of 10")

    expected_category = category_for_repository(repository)
    if expected_category is None:
        result.errors.append("cannot derive a canonical category from the repository name")
    elif result.category != expected_category:
        result.errors.append(
            f"category must be {expected_category!r}, found {result.category!r}"
        )

    body = text[front_match.end() :]
    h1s = H1.findall(body)
    if len(h1s) != 1:
        result.errors.append("index must contain exactly one H1")
    elif result.title and h1s[0].strip() != result.title:
        result.errors.append("H1 must exactly match the front matter title")

    h2s = tuple(value.strip() for value in H2.findall(body))
    if h2s != REQUIRED_HEADINGS:
        result.errors.append(
            "H2 headings must appear exactly in the required order: "
            + " | ".join(REQUIRED_HEADINGS)
        )

    screenshot_body = section(body, "Screenshots", "Requirements")
    images = list(IMAGE.finditer(screenshot_body))
    if not images:
        result.errors.append("Screenshots must contain at least one local product image")
    for image in images:
        alt = image.group("alt").strip()
        target = image.group("target")
        if not alt:
            result.errors.append(f"screenshot has empty alt text: {target}")
        pure = normalized_image_target(target)
        if pure is None:
            result.errors.append(f"screenshot must use a safe images path: {target}")
        else:
            source = product_root.joinpath(*pure.parts)
            if not source.is_file() or source.is_symlink():
                result.errors.append(f"referenced screenshot does not exist: {target}")
        following = screenshot_body[image.end() :]
        next_line = next((line.strip() for line in following.splitlines() if line.strip()), "")
        if not re.fullmatch(r"\*[^*].+\*", next_line):
            result.errors.append(f"screenshot requires an italic caption: {target}")
    if "fictional demonstration data" not in screenshot_body.lower():
        result.errors.append("Screenshots must disclose fictional demonstration data")

    required_urls = (CANONICAL_SUPPORT_URL, PRODUCT_ISSUE_URL, DOCUMENTATION_ISSUE_URL)
    for url in required_urls:
        if url not in body:
            result.errors.append(f"missing canonical public link: {url}")

    forbidden_patterns = {
        "deprecated Malaysia support URL": r"https://pukunui\.com/home/location/malaysia/?",
        "legacy Moodle plugins URL": r"https?://moodle\.org/plugins/",
        "source revision": r"\bSource revision\b",
        "source commit link": r"github\.com/PukunuiMalaysia/[^\s)]+/commit/",
        "source branch link": r"github\.com/PukunuiMalaysia/[^\s)]+/blob/",
        "publication branch name": r"\bMOODLE_[0-9]+_STABLE\b",
        "Git checkout instruction": r"\bgit\s+(?:clone|checkout|switch)\b",
        "Composer instruction": r"\bComposer\b",
        "npm instruction": r"\bnpm\b",
        "filesystem deployment instruction": r"\bfilesystem deployment\b",
    }
    for label, pattern in forbidden_patterns.items():
        if re.search(pattern, body, re.IGNORECASE):
            result.errors.append(f"public documentation contains {label}")

    for link in MARKDOWN_LINK.finditer(body):
        target = link.group("target")
        if target.startswith("https://github.com/PukunuiMalaysia/") and not target.startswith(
            "https://github.com/PukunuiMalaysia/moodle-docs/issues/"
        ):
            result.errors.append(f"source repository link is not public documentation: {target}")

    installation = section(body, "Installation", "Configuration and use")
    if repository in BROWSER_STORES:
        expected_store = BROWSER_STORES[repository]
        if expected_store not in installation:
            result.errors.append(f"Installation must link to the official Chrome Web Store: {expected_store}")
    elif repository == "moodle-configurable_reports-custom_sql_queries":
        dependency = "https://marketplace.moodle.com/plugins/block_configurable_reports"
        if dependency not in installation:
            result.errors.append(
                "SQL library installation must link to the Configurable Reports Marketplace page"
            )
    else:
        if "ZIP" not in installation:
            result.errors.append("Moodle installation must describe the plugin ZIP")
        if "Site administration > Plugins > Install plugins" not in installation:
            result.errors.append(
                "Moodle installation must use Site administration > Plugins > Install plugins"
            )
        if availability == "pre-release" and not (
            re.search(r"Marketplace", installation, re.IGNORECASE)
            and re.search(r"awaiting|not yet|pending", installation, re.IGNORECASE)
        ):
            result.errors.append(
                "Pre-release installation must state that Marketplace publication is pending"
            )
        expected_marketplace = marketplace_url(repository)
        if (
            expected_marketplace
            and availability in MARKETPLACE_AVAILABILITIES
            and expected_marketplace not in installation
        ):
            result.errors.append(
                f"Installation does not link to the verified Marketplace page: {expected_marketplace}"
            )

    licence = section(body, "Support and licence", None)
    if not re.search(r"\blicen[cs]", licence, re.IGNORECASE):
        result.errors.append("Support and licence must state the software and documentation licences")

    return result


def availability_from_inventory(entry: dict[str, Any]) -> str | None:
    """Return product_availability from supported inventory shapes."""
    direct = entry.get("availability") or entry.get("product_availability")
    if isinstance(direct, str):
        return direct
    properties = entry.get("properties", {})
    if isinstance(properties, dict):
        value = properties.get("product_availability")
        return value if isinstance(value, str) else None
    if isinstance(properties, list):
        for item in properties:
            if (
                isinstance(item, dict)
                and item.get("property_name") == "product_availability"
                and isinstance(item.get("value"), str)
            ):
                return item["value"]
    return None


def repository_from_inventory(entry: dict[str, Any]) -> str | None:
    """Return a repository name from supported inventory shapes."""
    value = entry.get("repository") or entry.get("repository_name") or entry.get("name")
    return value if isinstance(value, str) else None


def validate_navigation_order(results: list[ContractResult]) -> list[str]:
    """Validate alphabetical navigation order in increments of ten by category."""
    errors: list[str] = []
    for category in CATEGORY_ORDER:
        entries = sorted(
            (
                result
                for result in results
                if result.category == category and result.title is not None
            ),
            key=lambda result: (result.title or "").casefold(),
        )
        for position, result in enumerate(entries, start=1):
            expected = position * 10
            if result.nav_order != expected:
                errors.append(
                    f"{result.repository}: nav_order must be {expected} for alphabetical {category} navigation"
                )
    return errors


def print_results(results: list[ContractResult], navigation_errors: list[str]) -> int:
    """Print validation findings and return an exit status."""
    for result in results:
        for error in result.errors:
            print(f"ERROR {result.repository}: {error}", file=sys.stderr)
        for warning in result.warnings:
            print(f"WARNING {result.repository}: {warning}", file=sys.stderr)
    for error in navigation_errors:
        print(f"ERROR {error}", file=sys.stderr)
    error_count = sum(len(result.errors) for result in results) + len(navigation_errors)
    warning_count = sum(len(result.warnings) for result in results)
    if error_count:
        print(
            f"Public documentation contract failed: {error_count} error(s), {warning_count} warning(s)",
            file=sys.stderr,
        )
        return 1
    print(
        f"Public documentation contract passed: {len(results)} product(s), {warning_count} warning(s)"
    )
    return 0


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    single = parser.add_argument_group("single product")
    single.add_argument("--source", type=Path, help="central product source directory")
    single.add_argument("--repository", help="product repository identity")
    single.add_argument("--availability", help="product_availability value")
    inventory = parser.add_argument_group("inventory audit")
    inventory.add_argument("--content-root", type=Path, help="central content/products directory")
    inventory.add_argument("--inventory", type=Path, help="reviewed JSON inventory")
    return parser.parse_args()


def main() -> int:
    """Run one repository check or a reviewed local inventory audit."""
    args = parse_args()
    if args.source or args.repository or args.availability:
        if not (args.source and args.repository and args.availability):
            raise SystemExit("--source, --repository and --availability must be used together")
        result = validate_docs_tree(args.source, args.repository, args.availability)
        return print_results([result], [])
    if not (args.content_root and args.inventory):
        raise SystemExit("use either the single-product arguments or --content-root with --inventory")
    try:
        raw = json.loads(args.inventory.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"cannot read inventory: {error}") from error
    if not isinstance(raw, list):
        raise SystemExit("inventory must contain a JSON list")
    results: list[ContractResult] = []
    for entry in raw:
        if not isinstance(entry, dict):
            raise SystemExit("inventory entries must be objects")
        repository = repository_from_inventory(entry)
        availability = availability_from_inventory(entry)
        if not repository or not availability:
            raise SystemExit("inventory entries require repository and product_availability")
        if availability not in PRODUCT_DOC_AVAILABILITIES:
            continue
        results.append(
            validate_docs_tree(args.content_root / repository, repository, availability)
        )
    return print_results(results, validate_navigation_order(results))


if __name__ == "__main__":
    raise SystemExit(main())
