#!/usr/bin/env python3
"""Describe the generated snapshot in a Pages artifact, never unpublished sources."""

import argparse
import json
from pathlib import Path
import re


def build_manifest(root: Path, site: Path, commit: str) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("A full deployment commit SHA is required")
    provenance = json.loads((root / "_data/provenance.yml").read_text())
    catalog = json.loads((root / "_data/repositories.yml").read_text())
    expected = {item["repository"] for item in catalog}
    if expected != set(provenance):
        raise ValueError("Catalog and provenance disagree")
    products = {}
    for name, item in sorted(provenance.items()):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", name) or name in {".", ".."}:
            raise ValueError("Unsafe repository name")
        digest = item.get("content_sha256", "")
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"Missing source digest: {name}")
        route = f"products/{name}/"
        if not (site / route / "index.html").is_file():
            raise ValueError(f"Missing rendered product route: {name}")
        products[name] = {
            "source_sha256": digest,
            "availability": item["availability"],
            "route": route,
        }
    return {"schema_version": 1, "commit": commit, "products": products}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--site", type=Path, default=Path("_site"))
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    manifest = build_manifest(args.root, args.site, args.commit)
    (args.site / "release-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
