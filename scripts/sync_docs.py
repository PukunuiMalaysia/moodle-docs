#!/usr/bin/env python3
"""Synchronize explicitly public documentation from allowlisted repositories."""

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
from typing import Any


ORGANIZATION = "PukunuiMalaysia"
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


class SyncError(RuntimeError):
    """A validation or synchronization failure."""


def run(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    """Run a command without echoing credentials and return stdout."""
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode:
        message = result.stderr.strip() or result.stdout.strip() or "command failed"
        raise SyncError(f"{command[0]} failed: {message}")
    return result.stdout.strip()


def load_json(path: Path, default: Any = None) -> Any:
    """Load JSON, which is also valid YAML for Jekyll data files."""
    if not path.exists() and default is not None:
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SyncError(f"Cannot read {path}: {error}") from error


def validate_config(config: list[dict[str, Any]]) -> None:
    """Validate the public repository allowlist."""
    if len(config) != 22:
        raise SyncError(f"Expected exactly 22 repositories, found {len(config)}")
    names: set[str] = set()
    for item in config:
        required = {"repository", "title", "category", "nav_order"}
        missing = required.difference(item)
        if missing:
            raise SyncError(f"Repository entry is missing: {', '.join(sorted(missing))}")
        name = item["repository"]
        if not isinstance(name, str) or not re.fullmatch(r"moodle-[a-z0-9_-]+", name):
            raise SyncError(f"Invalid repository name: {name!r}")
        if name == "moodle-docs" or name in names:
            raise SyncError(f"Duplicate or recursive repository: {name}")
        names.add(name)


def resolve_branch(repository: str, configured: str | None, env: dict[str, str]) -> str:
    """Resolve an explicit override or the live GitHub default branch."""
    if configured:
        return configured
    return run(
        ["gh", "api", f"repos/{ORGANIZATION}/{repository}", "--jq", ".default_branch"],
        env=env,
    )


def clone_source(repository: str, branch: str, destination: Path, env: dict[str, str]) -> None:
    """Clone one source without placing the token in command arguments."""
    run(
        [
            "gh",
            "repo",
            "clone",
            f"{ORGANIZATION}/{repository}",
            str(destination),
            "--",
            "--branch",
            branch,
            "--single-branch",
            "--filter=blob:none",
        ],
        env=env,
    )


def docs_commit(source: Path) -> str:
    """Return the most recent commit that changed the public subtree."""
    try:
        return run(["git", "log", "-1", "--format=%H", "--", "docs/public"], cwd=source)
    except SyncError:
        return run(["git", "rev-parse", "HEAD"], cwd=source)


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
            text = path.read_text(encoding="utf-8")
            match = FRONT_MATTER.match(text)
            if not match or not TITLE.search(match.group("header")):
                raise SyncError(f"Markdown requires front matter with a title: {relative}")
        files.append(path)
    return files


def inject_navigation(
    text: str,
    *,
    repository: str,
    title: str,
    category: str,
    nav_order: int,
    relative: Path,
    source_commit: str,
    has_children: bool,
) -> str:
    """Add deterministic Just the Docs navigation and source provenance."""
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
    rendered += text[match.end():]
    if relative.as_posix() == "index.md":
        source_url = f"https://github.com/{ORGANIZATION}/{repository}/commit/{source_commit}"
        rendered = rendered.rstrip() + (
            "\n\n---\n\n"
            f"Source: [{repository} at `{source_commit[:12]}`]({source_url}). "
            "[Report a documentation issue]"
            f"(https://github.com/{ORGANIZATION}/moodle-docs/issues/new?template=documentation.yml).\n"
        )
    return rendered


def sync_repository(
    item: dict[str, Any],
    source: Path,
    destination: Path,
    old_provenance: dict[str, Any],
    branch: str,
) -> dict[str, Any]:
    """Validate and render one source repository."""
    public_root = source / "docs" / "public"
    files = validate_public_tree(public_root)
    digest = content_digest(public_root)
    previous = old_provenance.get(item["repository"], {})
    if previous.get("content_sha256") == digest:
        source_commit = previous["source_commit"]
        synced_at = previous["synced_at"]
    else:
        source_commit = docs_commit(source)
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
                source_commit=source_commit,
                has_children=len(markdown_files) > 1,
            )
            target.write_text(rendered, encoding="utf-8")
        else:
            shutil.copy2(path, target)

    return {
        "branch": branch,
        "content_sha256": digest,
        "source_commit": source_commit,
        "source_url": f"https://github.com/{ORGANIZATION}/{item['repository']}",
        "synced_at": synced_at,
    }


def synchronize(repo_root: Path, local_root: Path | None = None) -> None:
    """Build and atomically install a complete generated snapshot."""
    config_path = repo_root / "_data" / "repositories.yml"
    config = load_json(config_path)
    if not isinstance(config, list):
        raise SyncError(f"Expected a repository list in {config_path}")
    validate_config(config)
    old_provenance = load_json(repo_root / "_data" / "provenance.yml", default={})

    token = os.environ.get("GH_TOKEN", "")
    if local_root is None and not token:
        raise SyncError("GH_TOKEN is required for remote synchronization")
    env = dict(os.environ)
    env["GH_TOKEN"] = token

    with tempfile.TemporaryDirectory(prefix=".moodle-docs-sync-", dir=repo_root) as temporary:
        temp_root = Path(temporary)
        generated = temp_root / "products"
        sources = temp_root / "sources"
        generated.mkdir()
        provenance: dict[str, Any] = {}

        for item in config:
            repository = item["repository"]
            branch = item.get("branch")
            if local_root is None:
                branch = resolve_branch(repository, branch, env)
                source = sources / repository
                clone_source(repository, branch, source, env)
            else:
                source = local_root / repository
                if not source.is_dir():
                    raise SyncError(f"Missing local source repository: {source}")
                if not branch:
                    try:
                        upstream = run(
                            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
                            cwd=source,
                        )
                        branch = upstream.removeprefix("origin/")
                    except SyncError:
                        branch = run(["git", "branch", "--show-current"], cwd=source)
                if not branch:
                    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=source)
            provenance[repository] = sync_repository(
                item,
                source,
                generated / repository,
                old_provenance,
                branch,
            )

        products = repo_root / "products"
        backup = temp_root / "products-backup"
        if products.exists():
            products.rename(backup)
        try:
            generated.rename(products)
            provenance_target = repo_root / "_data" / "provenance.yml"
            provenance_temp = temp_root / "provenance.yml"
            provenance_temp.write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            os.replace(provenance_temp, provenance_target)
        except Exception:
            if products.exists():
                shutil.rmtree(products)
            if backup.exists():
                backup.rename(products)
            raise


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
        help="parent directory containing local source repositories",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        synchronize(args.repo_root.resolve(), args.local_root.resolve() if args.local_root else None)
    except SyncError as error:
        print(f"sync error: {error}", file=os.sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
