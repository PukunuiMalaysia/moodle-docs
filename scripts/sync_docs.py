#!/usr/bin/env python3
"""Publish central product docs using the GitHub App inventory as the lifecycle gate."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from typing import Any

try:
    from .public_docs_contract import ContractResult, validate_docs_tree, validate_navigation_order
except ImportError:  # Direct script execution.
    from public_docs_contract import ContractResult, validate_docs_tree, validate_navigation_order


ORGANIZATION = "PukunuiMalaysia"
PRODUCT_AVAILABILITY_PROPERTY = "product_availability"
DOCS_BRANCH_PROPERTY = "docs_branch"
PUBLIC_AVAILABILITIES = frozenset(
    {"commercial-active", "commercial-legacy", "pre-release", "public-free"}
)
PRODUCT_AVAILABILITIES = PUBLIC_AVAILABILITIES | frozenset(
    {"in-development", "internal-only", "retired", "not-a-product"}
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
ALLOWED_SUFFIXES = {
    ".gif",
    ".jpeg",
    ".jpg",
    ".markdown",
    ".md",
    ".pdf",
    ".png",
    ".svg",
    ".txt",
    ".webp",
}
MARKDOWN_SUFFIXES = {".md", ".markdown"}
FRONT_MATTER = re.compile(r"\A---\r?\n(?P<header>.*?)\r?\n---\r?\n", re.DOTALL)
TITLE = re.compile(r"^title:\s*(?P<title>.+?)\s*$", re.MULTILINE)
REPOSITORY_NAME = re.compile(r"[A-Za-z0-9_.-]+")
BRANCH_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]*")
TRANSIENT_GITHUB_ERRORS = (
    "error connecting to api.github.com",
    "http 502",
    "http 503",
    "http 504",
    "connection reset",
    "timed out",
)


class SyncError(RuntimeError):
    """A validation or synchronization failure."""


def run(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    """Run a command without echoing credentials and retry transient GitHub failures."""
    attempts = 3 if command and command[0] == "gh" else 1
    for attempt in range(attempts):
        result = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if not result.returncode:
            return result.stdout.strip()
        message = result.stderr.strip() or result.stdout.strip() or "command failed"
        transient = any(marker in message.lower() for marker in TRANSIENT_GITHUB_ERRORS)
        if not transient or attempt == attempts - 1:
            raise SyncError(f"{command[0]} failed: {message}")
        time.sleep(2**attempt)
    raise AssertionError("unreachable")


def load_json(path: Path, default: Any = None) -> Any:
    """Load JSON, which is also valid YAML for Jekyll data files."""
    if not path.exists() and default is not None:
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SyncError(f"Cannot read {path}: {error}") from error


def command_json(command: list[str], *, env: dict[str, str]) -> Any:
    """Run a command and parse its JSON output."""
    output = run(command, env=env)
    try:
        return json.loads(output)
    except json.JSONDecodeError as error:
        raise SyncError(f"{command[0]} returned invalid JSON: {error}") from error


def property_map(raw: Any, repository: str) -> dict[str, Any]:
    """Normalize GitHub's custom-property response or inventory shorthand."""
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, list):
        raise SyncError(f"Invalid custom properties for {repository}")
    properties: dict[str, Any] = {}
    for item in raw:
        if not isinstance(item, dict) or not isinstance(item.get("property_name"), str):
            raise SyncError(f"Invalid custom property entry for {repository}")
        properties[item["property_name"]] = item.get("value")
    return properties


def normalize_inventory(raw: Any) -> list[dict[str, Any]]:
    """Validate and normalize the App-visible repository inventory."""
    if not isinstance(raw, list):
        raise SyncError("Expected the App-visible repository inventory to be a list")

    inventory: list[dict[str, Any]] = []
    names: set[str] = set()
    for entry in raw:
        if not isinstance(entry, dict):
            raise SyncError("Each App-visible repository entry must be an object")
        repository = entry.get("repository") or entry.get("name")
        if not isinstance(repository, str) or not REPOSITORY_NAME.fullmatch(repository):
            raise SyncError(f"Invalid repository name: {repository!r}")
        if repository in names:
            raise SyncError(f"Duplicate App-visible repository: {repository}")
        names.add(repository)

        properties = property_map(entry.get("properties", {}), repository)
        availability = entry.get(
            PRODUCT_AVAILABILITY_PROPERTY,
            properties.get(PRODUCT_AVAILABILITY_PROPERTY),
        )
        if availability is not None and availability not in PRODUCT_AVAILABILITIES:
            raise SyncError(
                f"{repository} has an invalid {PRODUCT_AVAILABILITY_PROPERTY}; expected one of: "
                + ", ".join(sorted(PRODUCT_AVAILABILITIES))
            )

        docs_branch = entry.get(DOCS_BRANCH_PROPERTY, properties.get(DOCS_BRANCH_PROPERTY))
        if docs_branch == "":
            docs_branch = None
        if docs_branch is not None:
            if (
                not isinstance(docs_branch, str)
                or not BRANCH_NAME.fullmatch(docs_branch)
                or ".." in docs_branch
                or docs_branch.endswith(".lock")
            ):
                raise SyncError(f"Invalid docs_branch for {repository}: {docs_branch!r}")

        default_branch = entry.get("default_branch")
        if not isinstance(default_branch, str) or not default_branch:
            raise SyncError(f"Missing default_branch for {repository}")

        visibility = entry.get("visibility")
        if visibility is None:
            private = entry.get("private")
            if not isinstance(private, bool):
                raise SyncError(f"Missing repository visibility for {repository}")
            visibility = "private" if private else "public"
        if visibility not in {"public", "private", "internal"}:
            raise SyncError(f"Invalid repository visibility for {repository}: {visibility!r}")

        inventory.append(
            {
                "repository": repository,
                "availability": availability,
                "branch": docs_branch or default_branch,
                "default_branch": default_branch,
                "docs_branch": docs_branch,
                "source_public": visibility == "public",
            }
        )
    return sorted(inventory, key=lambda item: item["repository"])


def discover_all_repositories(env: dict[str, str]) -> list[dict[str, Any]]:
    """Discover every repository covered by the source App installation."""
    installation = command_json(["gh", "api", "installation"], env=env)
    if not isinstance(installation, dict):
        raise SyncError("GitHub returned an invalid source App installation response")
    if installation.get("repository_selection") != "all":
        raise SyncError(
            "The source App installation must grant access to all repositories; "
            "update its repository access before synchronizing."
        )

    pages = command_json(
        [
            "gh",
            "api",
            "--paginate",
            "--slurp",
            "installation/repositories?per_page=100",
        ],
        env=env,
    )
    if not isinstance(pages, list):
        raise SyncError("GitHub returned an invalid installation repository response")

    return inventory_from_repository_pages(pages, env)


def discover_org_repositories(env: dict[str, str]) -> list[dict[str, Any]]:
    """Discover repositories visible to a user's organization token for local checks."""
    pages = command_json(
        [
            "gh",
            "api",
            "--paginate",
            "--slurp",
            f"orgs/{ORGANIZATION}/repos?per_page=100&type=all",
        ],
        env=env,
    )
    if not isinstance(pages, list):
        raise SyncError("GitHub returned an invalid organization repository response")
    return inventory_from_repository_pages(pages, env)


def inventory_from_repository_pages(
    pages: list[Any], env: dict[str, str]
) -> list[dict[str, Any]]:
    """Read properties and normalize repositories returned by GitHub."""
    raw_inventory: list[dict[str, Any]] = []
    for page in pages:
        repositories = page.get("repositories") if isinstance(page, dict) else page
        if not isinstance(repositories, list):
            raise SyncError("GitHub returned an invalid repository page")
        for repository in repositories:
            if not isinstance(repository, dict):
                raise SyncError("GitHub returned an invalid installation repository")
            owner_data = repository.get("owner")
            owner = owner_data.get("login") if isinstance(owner_data, dict) else None
            name = repository.get("name")
            if owner != ORGANIZATION or not isinstance(name, str):
                raise SyncError("GitHub returned a repository outside its organization")
            properties = command_json(
                ["gh", "api", f"repos/{ORGANIZATION}/{name}/properties/values"],
                env=env,
            )
            raw_inventory.append(
                {
                    "repository": name,
                    "default_branch": repository.get("default_branch"),
                    "visibility": repository.get("visibility"),
                    "private": repository.get("private"),
                    "properties": properties,
                }
            )
    return normalize_inventory(raw_inventory)


def local_inventory(repo_root: Path, local_root: Path) -> list[dict[str, Any]]:
    """Provide offline reconciliation from the current public catalog."""
    catalog_path = repo_root / "_data" / "repositories.yml"
    catalog = load_json(catalog_path)
    if not isinstance(catalog, list):
        raise SyncError(f"Expected a repository list in {catalog_path}")
    provenance = load_json(repo_root / "_data" / "provenance.yml", default={})
    if not isinstance(provenance, dict):
        raise SyncError("Expected _data/provenance.yml to contain an object")

    raw_inventory: list[dict[str, Any]] = []
    for item in catalog:
        if not isinstance(item, dict) or not isinstance(item.get("repository"), str):
            raise SyncError(f"Invalid repository entry in {catalog_path}")
        repository = item["repository"]
        source = local_root / repository
        branch = item.get("branch") or item.get("docs_branch")
        if not branch and source.is_dir():
            try:
                upstream = run(
                    ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
                    cwd=source,
                )
                branch = upstream.removeprefix("origin/")
            except SyncError:
                branch = run(["git", "branch", "--show-current"], cwd=source)
        if not branch:
            raise SyncError(f"Cannot resolve a branch for {repository}")
        previous = provenance.get(repository, {})
        raw_inventory.append(
            {
                "repository": repository,
                "default_branch": branch,
                "visibility": "public" if previous.get("source_url") else "private",
                PRODUCT_AVAILABILITY_PROPERTY: item.get(
                    "availability", "commercial-active"
                ),
                DOCS_BRANCH_PROPERTY: branch,
            }
        )
    return normalize_inventory(raw_inventory)


def content_commit(repo_root: Path, repository: str) -> str:
    """Return the most recent central commit that changed one product source."""
    relative = Path("content") / "products" / repository
    commit = run(["git", "log", "-1", "--format=%H", "--", str(relative)], cwd=repo_root)
    return commit or run(["git", "rev-parse", "HEAD"], cwd=repo_root)


def content_digest(public_root: Path) -> str:
    """Hash paths and bytes so unchanged docs keep stable provenance."""
    digest = hashlib.sha256()
    for path in sorted(public_root.rglob("*")):
        if path.is_file() and not path.is_symlink():
            digest.update(path.relative_to(public_root).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()


def validate_public_tree(public_root: Path) -> list[Path]:
    """Validate the explicit publication boundary and return files."""
    if not public_root.is_dir():
        raise SyncError(f"Missing required directory: {public_root}")
    index = public_root / "index.md"
    if not index.is_file() or index.is_symlink():
        raise SyncError(f"Missing required file: {index}")

    files: list[Path] = []
    for path in sorted(public_root.rglob("*")):
        relative = path.relative_to(public_root)
        if path.is_symlink():
            raise SyncError(f"Symlinks are not publishable: {relative}")
        if path.is_dir():
            continue
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            raise SyncError(f"File type is not publishable: {relative}")
        if any(part.startswith(".") for part in relative.parts):
            raise SyncError(f"Hidden paths are not publishable: {relative}")
        if path.suffix.lower() in MARKDOWN_SUFFIXES:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError as error:
                raise SyncError(f"Markdown is not valid UTF-8: {relative}") from error
            match = FRONT_MATTER.match(text)
            if not match or not TITLE.search(match.group("header")):
                raise SyncError(f"Markdown requires front matter with a title: {relative}")
        files.append(path)
    return files


def front_matter_value(header: str, key: str, repository: str) -> str:
    """Read one simple scalar from source front matter."""
    matches = re.findall(rf"^{re.escape(key)}:\s*(.+?)\s*$", header, re.MULTILINE)
    if len(matches) != 1:
        raise SyncError(f"{repository} index.md must define {key} exactly once")
    value = matches[0].strip()
    if value.startswith('"'):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError as error:
            raise SyncError(f"Invalid quoted {key} for {repository}") from error
        if not isinstance(decoded, str):
            raise SyncError(f"Invalid {key} for {repository}")
        return decoded.strip()
    if len(value) >= 2 and value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'").strip()
    return value


def source_metadata(public_root: Path, repository: str) -> dict[str, Any]:
    """Read title and navigation metadata from the central product index."""
    text = (public_root / "index.md").read_text(encoding="utf-8")
    match = FRONT_MATTER.match(text)
    if not match:
        raise SyncError(f"{repository} index.md requires front matter")
    header = match.group("header")
    title = front_matter_value(header, "title", repository)
    category = front_matter_value(header, "category", repository)
    raw_nav_order = front_matter_value(header, "nav_order", repository)
    if not title:
        raise SyncError(f"{repository} title must not be empty")
    if category not in CATEGORY_ORDER:
        raise SyncError(
            f"Invalid category for {repository}: {category!r}; expected one of "
            + ", ".join(CATEGORY_ORDER)
        )
    if not raw_nav_order.isdigit() or int(raw_nav_order) < 1:
        raise SyncError(f"Invalid nav_order for {repository}: {raw_nav_order!r}")
    return {"title": title, "category": category, "nav_order": int(raw_nav_order)}


def validate_navigation(items: list[dict[str, Any]]) -> None:
    """Reject ambiguous navigation coordinates."""
    coordinates: dict[tuple[str, int], str] = {}
    for item in items:
        coordinate = (item["category"], item["nav_order"])
        if coordinate in coordinates:
            raise SyncError(
                f"Duplicate nav_order {item['nav_order']} in {item['category']}: "
                f"{coordinates[coordinate]} and {item['repository']}"
            )
        coordinates[coordinate] = item["repository"]


def inject_navigation(
    text: str,
    *,
    repository: str,
    title: str,
    category: str,
    nav_order: int,
    relative: Path,
    availability: str,
    has_children: bool,
) -> str:
    """Add deterministic Just the Docs navigation and safe provenance."""
    match = FRONT_MATTER.match(text)
    if not match:
        raise SyncError(f"Missing front matter: {relative}")
    header = match.group("header")
    for key in ("parent", "grand_parent", "nav_order", "has_children", "permalink"):
        header = re.sub(rf"^{key}:.*\r?\n?", "", header, flags=re.MULTILINE)

    if relative.as_posix() == "index.md":
        additions = [
            f"parent: {json.dumps(category)}",
            f"nav_order: {nav_order}",
            f"permalink: /products/{repository}/",
        ]
        if has_children:
            additions.append("has_children: true")
    else:
        additions = [
            f"parent: {json.dumps(title)}",
            f"grand_parent: {json.dumps(category)}",
        ]
    rendered = f"---\n{header.rstrip()}\n" + "\n".join(additions) + "\n---\n"
    body = text[match.end():]
    if relative.as_posix() == "index.md" and availability == "commercial-legacy":
        body = (
            "\n> **Legacy product:** This documentation is retained for supported existing "
            "installations. Contact Pukunui before planning a new deployment.\n\n"
            + body.lstrip()
        )
    elif relative.as_posix() == "index.md" and availability == "pre-release":
        body = (
            "\n> **Pre-release product:** This product is ready for release and awaiting "
            "Marketplace publication. Its Marketplace listing may not yet be available.\n\n"
            + body.lstrip()
        )
    rendered += body
    return rendered


def sync_repository(
    item: dict[str, Any],
    public_root: Path,
    destination: Path,
    old_provenance: dict[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    """Validate and render one centrally owned product source."""
    files = validate_public_tree(public_root)
    contract = validate_docs_tree(public_root, item["repository"], item["availability"])
    if contract.errors:
        raise SyncError(
            f"{item['repository']} public documentation contract failed: "
            + "; ".join(contract.errors)
        )
    digest = content_digest(public_root)
    current_content_commit = content_commit(repo_root, item["repository"])
    previous = old_provenance.get(item["repository"], {})
    if (
        previous.get("content_sha256") == digest
        and previous.get("branch") == item["branch"]
        and previous.get("content_commit") == current_content_commit
    ):
        synced_at = previous["synced_at"]
    else:
        synced_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

    markdown_files = [path for path in files if path.suffix.lower() in MARKDOWN_SUFFIXES]
    for path in files:
        relative = path.relative_to(public_root)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() in MARKDOWN_SUFFIXES:
            rendered = inject_navigation(
                path.read_text(encoding="utf-8"),
                repository=item["repository"],
                title=item["title"],
                category=item["category"],
                nav_order=item["nav_order"],
                relative=relative,
                availability=item["availability"],
                has_children=len(markdown_files) > 1,
            )
            target.write_text(rendered, encoding="utf-8")
        else:
            shutil.copy2(path, target)

    provenance = {
        "availability": item["availability"],
        "branch": item["branch"],
        "category": item["category"],
        "content_commit": current_content_commit,
        "content_sha256": digest,
        "nav_order": item["nav_order"],
        "synced_at": synced_at,
        "title": item["title"],
    }
    if item["source_public"]:
        provenance["source_url"] = f"https://github.com/{ORGANIZATION}/{item['repository']}"
    return provenance


def catalog_entry(item: dict[str, Any]) -> dict[str, Any]:
    """Return the public navigation record generated from source metadata."""
    return {
        "availability": item["availability"],
        "branch": item["branch"],
        "category": item["category"],
        "nav_order": item["nav_order"],
        "repository": item["repository"],
        "title": item["title"],
    }


def classify_changes(
    old_provenance: dict[str, Any],
    provenance: dict[str, Any],
    inventory: list[dict[str, Any]],
) -> dict[str, Any]:
    """Classify a generated snapshot, including safe retirement-only changes."""
    old_names = set(old_provenance)
    new_names = set(provenance)
    added = sorted(new_names - old_names)
    removed = sorted(old_names - new_names)
    comparable = (
        "availability",
        "branch",
        "category",
        "content_commit",
        "content_sha256",
        "nav_order",
        "source_url",
        "title",
    )
    updated = sorted(
        repository
        for repository in old_names & new_names
        if any(
            old_provenance[repository].get(key) != provenance[repository].get(key)
            for key in comparable
        )
    )
    unchanged = sorted((old_names & new_names) - set(updated))
    availability = {item["repository"]: item["availability"] for item in inventory}
    return {
        "accessible_repository_count": len(inventory),
        "added": added,
        "published_repository_count": len(provenance),
        "removed": removed,
        "removed_states": {repository: availability[repository] for repository in removed},
        "retirement_only": bool(removed) and not added and not updated,
        "unchanged": unchanged,
        "updated": updated,
    }


def write_json(path: Path, value: Any) -> None:
    """Write stable JSON for both machine output and Jekyll data."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def install_snapshot(
    repo_root: Path,
    generated: Path,
    provenance_file: Path,
    catalog_file: Path,
    temp_root: Path,
) -> None:
    """Atomically replace generated products and both generated data files."""
    targets = {
        repo_root / "products": generated,
        repo_root / "_data" / "provenance.yml": provenance_file,
        repo_root / "_data" / "repositories.yml": catalog_file,
    }
    backups: dict[Path, Path] = {}
    installed: list[Path] = []
    try:
        for index, target in enumerate(targets):
            if target.is_symlink():
                raise SyncError(f"Refusing to replace symlinked generated target: {target}")
            if target.exists():
                backup = temp_root / f"snapshot-backup-{index}"
                target.rename(backup)
                backups[target] = backup
        for target, source in targets.items():
            source.rename(target)
            installed.append(target)
    except Exception:
        for target in reversed(installed):
            if target.is_dir():
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()
        for target, backup in backups.items():
            if backup.exists():
                backup.rename(target)
        raise


def synchronize(
    repo_root: Path,
    local_root: Path | None = None,
    inventory_path: Path | None = None,
    *,
    dry_run: bool = False,
    result_file: Path | None = None,
    user_token_discovery: bool = False,
) -> dict[str, Any]:
    """Build, classify, and optionally install a complete generated snapshot."""
    old_provenance = load_json(repo_root / "_data" / "provenance.yml", default={})
    if not isinstance(old_provenance, dict):
        raise SyncError("Expected _data/provenance.yml to contain an object")

    token = os.environ.get("GH_TOKEN", "")
    if inventory_path is None and local_root is None and not token:
        raise SyncError("GH_TOKEN is required for remote inventory discovery")
    env = dict(os.environ)
    env["GH_TOKEN"] = token

    if inventory_path is not None:
        inventory = normalize_inventory(load_json(inventory_path))
    elif local_root is not None:
        inventory = local_inventory(repo_root, local_root)
    elif user_token_discovery:
        inventory = discover_org_repositories(env)
    else:
        inventory = discover_all_repositories(env)

    accessible = {item["repository"] for item in inventory}
    inaccessible_published = sorted(set(old_provenance) - accessible)
    if inaccessible_published:
        raise SyncError(
            "Previously published repositories are no longer accessible to the source App: "
            + ", ".join(inaccessible_published)
            + ". Restore access, synchronize an explicit nonpublic state, and remove App access only after the deletion merges."
        )

    selected = [
        item for item in inventory if item["availability"] in PUBLIC_AVAILABILITIES
    ]
    if any(item["repository"] == "moodle-docs" for item in selected):
        raise SyncError("moodle-docs cannot publish itself as a product")

    with tempfile.TemporaryDirectory(prefix=".moodle-docs-sync-", dir=repo_root) as temporary:
        temp_root = Path(temporary)
        generated = temp_root / "products"
        generated.mkdir()
        source_items: list[tuple[dict[str, Any], Path]] = []
        contract_results: list[ContractResult] = []
        central_products = repo_root / "content" / "products"

        for selected_item in selected:
            item = dict(selected_item)
            repository = item["repository"]
            public_root = central_products / repository
            validate_public_tree(public_root)
            contract = validate_docs_tree(public_root, repository, item["availability"])
            if contract.errors:
                raise SyncError(
                    f"{repository} public documentation contract failed: "
                    + "; ".join(contract.errors)
                )
            item.update(source_metadata(public_root, repository))
            source_items.append((item, public_root))
            contract_results.append(contract)

        validate_navigation([item for item, _source in source_items])
        navigation_errors = validate_navigation_order(contract_results)
        if navigation_errors:
            raise SyncError("Central product navigation failed: " + "; ".join(navigation_errors))
        category_position = {category: index for index, category in enumerate(CATEGORY_ORDER)}
        source_items.sort(
            key=lambda pair: (
                category_position[pair[0]["category"]],
                pair[0]["nav_order"],
                pair[0]["repository"],
            )
        )

        provenance: dict[str, Any] = {}
        catalog: list[dict[str, Any]] = []
        for item, public_root in source_items:
            repository = item["repository"]
            provenance[repository] = sync_repository(
                item,
                public_root,
                generated / repository,
                old_provenance,
                repo_root,
            )
            catalog.append(catalog_entry(item))

        result = classify_changes(old_provenance, provenance, inventory)
        provenance_file = temp_root / "provenance.yml"
        catalog_file = temp_root / "repositories.yml"
        write_json(provenance_file, provenance)
        write_json(catalog_file, catalog)
        if not dry_run:
            install_snapshot(repo_root, generated, provenance_file, catalog_file, temp_root)
        if result_file is not None:
            write_json(result_file, result)
        return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="moodle-docs repository root",
    )
    parser.add_argument(
        "--local-root",
        type=Path,
        help="optional checkout parent used for offline catalog branch fallback",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        help="JSON inventory for staged comparison or local validation",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate central sources without replacing generated files",
    )
    parser.add_argument(
        "--result-file",
        type=Path,
        help="write the synchronization classification as JSON",
    )
    parser.add_argument(
        "--user-token-discovery",
        action="store_true",
        help="for local checks, discover the organisation repository list using GH_TOKEN instead of the App installation",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = synchronize(
            args.repo_root.resolve(),
            args.local_root.resolve() if args.local_root else None,
            args.inventory.resolve() if args.inventory else None,
            dry_run=args.dry_run,
            result_file=args.result_file.resolve() if args.result_file else None,
            user_token_discovery=args.user_token_discovery,
        )
    except SyncError as error:
        print(f"sync error: {error}", file=os.sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
