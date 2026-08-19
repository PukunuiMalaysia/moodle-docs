from __future__ import annotations

import json
from pathlib import Path
import struct
import tempfile
import unittest

from scripts import check_links, sync_docs


class SyncDocsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.public = self.root / "docs" / "public"
        self.public.mkdir(parents=True)
        self.write_valid_index(self.root)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_valid_index(self, repository_root: Path, title: str = "Example") -> None:
        public = repository_root / "docs" / "public"
        images = public / "images"
        images.mkdir(parents=True, exist_ok=True)
        images.joinpath("example-overview.png").write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + struct.pack(">I", 13)
            + b"IHDR"
            + struct.pack(">II", 1280, 800)
            + b"\x08\x02\x00\x00\x00"
        )
        public.joinpath("index.md").write_text(
            f"""---
title: {title}
category: Blocks
nav_order: 10
---

# {title}

Example helps Moodle administrators complete a documented workflow.

## Key features

- Provides one clear example capability.

## Screenshots

![Example product overview](images/example-overview.png)
*The example workflow shown in Moodle.*

All people and content shown are fictional demonstration data.

## Requirements

- A supported Moodle site.

## Installation

Download the ZIP from the [Moodle Marketplace](https://marketplace.moodle.com/plugins/block_example), then install it through **Site administration > Plugins > Install plugins**.

## Configuration and use

Configure the example from its Moodle settings page.

## Privacy and permissions

The example stores no personal data and uses Moodle capabilities.

## Troubleshooting

- Confirm the plugin is enabled if the example is unavailable.

## Support and licence

- [Report a product problem](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Report a documentation problem](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml)
- [Pukunui Malaysia support](https://pukunui.com/location/malaysia/)

The software is licensed under the GNU General Public License v3 or later. Documentation is licensed under CC BY 4.0.
""",
            encoding="utf-8",
        )

    def inventory_entry(
        self,
        repository: str,
        availability: str,
        *,
        visibility: str = "private",
        branch: str = "main",
    ) -> dict[str, object]:
        return {
            "repository": repository,
            "default_branch": "main",
            "visibility": visibility,
            "properties": {
                "product_availability": availability,
                "docs_branch": branch,
            },
        }

    def matching_provenance(
        self,
        repository: str,
        public: Path,
        *,
        availability: str = "commercial-active",
    ) -> dict[str, object]:
        return {
            "availability": availability,
            "branch": "main",
            "category": "Blocks",
            "content_sha256": sync_docs.content_digest(public),
            "nav_order": 10,
            "source_commit": "b" * 40,
            "synced_at": "2026-08-13T00:00:00+00:00",
            "title": "Example",
        }

    def test_public_tree_requires_index(self) -> None:
        (self.public / "index.md").unlink()
        with self.assertRaisesRegex(sync_docs.SyncError, "Missing required file"):
            sync_docs.validate_public_tree(self.public)

    def test_public_tree_rejects_symlink(self) -> None:
        (self.public / "link.md").symlink_to(self.public / "index.md")
        with self.assertRaisesRegex(sync_docs.SyncError, "Symlinks are not publishable"):
            sync_docs.validate_public_tree(self.public)

    def test_public_tree_rejects_unapproved_file_type(self) -> None:
        (self.public / "secret.env").write_text("TOKEN=value\n", encoding="utf-8")
        with self.assertRaisesRegex(sync_docs.SyncError, "File type is not publishable"):
            sync_docs.validate_public_tree(self.public)

    def test_markdown_requires_title_front_matter(self) -> None:
        (self.public / "bad.md").write_text("# Missing front matter\n", encoding="utf-8")
        with self.assertRaisesRegex(sync_docs.SyncError, "requires front matter"):
            sync_docs.validate_public_tree(self.public)

    def test_index_requires_source_owned_navigation_metadata(self) -> None:
        (self.public / "index.md").write_text(
            "---\ntitle: Example\nnav_order: 10\n---\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(sync_docs.SyncError, "category exactly once"):
            sync_docs.source_metadata(self.public, "moodle-block_example")

    def test_digest_changes_for_addition_update_and_deletion(self) -> None:
        initial = sync_docs.content_digest(self.public)
        page = self.public / "guide.md"
        page.write_text("---\ntitle: Guide\n---\nOne\n", encoding="utf-8")
        added = sync_docs.content_digest(self.public)
        page.write_text("---\ntitle: Guide\n---\nTwo\n", encoding="utf-8")
        updated = sync_docs.content_digest(self.public)
        page.unlink()
        deleted = sync_docs.content_digest(self.public)
        self.assertNotEqual(initial, added)
        self.assertNotEqual(added, updated)
        self.assertEqual(initial, deleted)

    def test_navigation_omits_repository_provenance(self) -> None:
        rendered = sync_docs.inject_navigation(
            (self.public / "index.md").read_text(encoding="utf-8"),
            repository="moodle-block_example",
            title="Example",
            category="Blocks",
            nav_order=10,
            relative=Path("index.md"),
            availability="commercial-active",
            has_children=False,
        )
        self.assertIn('parent: "Blocks"', rendered)
        self.assertIn("permalink: /products/moodle-block_example/", rendered)
        self.assertNotIn("Source revision", rendered)
        self.assertNotIn("moodle-block_example/commit", rendered)

    def test_legacy_source_gets_public_status_notice(self) -> None:
        rendered = sync_docs.inject_navigation(
            (self.public / "index.md").read_text(encoding="utf-8"),
            repository="moodle-block_example",
            title="Example",
            category="Blocks",
            nav_order=10,
            relative=Path("index.md"),
            availability="commercial-legacy",
            has_children=False,
        )
        self.assertIn("**Legacy product:**", rendered)
        self.assertNotIn("moodle-block_example/commit/", rendered)

    def test_inventory_requires_known_product_availability(self) -> None:
        with self.assertRaisesRegex(sync_docs.SyncError, "must define product_availability"):
            sync_docs.normalize_inventory(
                [
                    {
                        "repository": "moodle-block_example",
                        "default_branch": "main",
                        "visibility": "private",
                    }
                ]
            )

    def test_inventory_rejects_invalid_docs_branch(self) -> None:
        entry = self.inventory_entry("moodle-block_example", "commercial-active")
        entry["properties"]["docs_branch"] = "../unsafe"  # type: ignore[index]
        with self.assertRaisesRegex(sync_docs.SyncError, "Invalid docs_branch"):
            sync_docs.normalize_inventory([entry])

    def test_duplicate_navigation_order_is_rejected(self) -> None:
        with self.assertRaisesRegex(sync_docs.SyncError, "Duplicate nav_order"):
            sync_docs.validate_navigation(
                [
                    {
                        "repository": "moodle-block_one",
                        "category": "Blocks",
                        "nav_order": 10,
                    },
                    {
                        "repository": "moodle-block_two",
                        "category": "Blocks",
                        "nav_order": 10,
                    },
                ]
            )

    def test_previous_provenance_is_reused_for_unchanged_content(self) -> None:
        destination = self.root / "output"
        old = {"moodle-block_example": self.matching_provenance("moodle-block_example", self.public)}
        result = sync_docs.sync_repository(
            {
                "repository": "moodle-block_example",
                "title": "Example",
                "category": "Blocks",
                "nav_order": 10,
                "availability": "commercial-active",
                "branch": "main",
                "source_public": False,
            },
            self.root,
            destination,
            old,
        )
        self.assertEqual("b" * 40, result["source_commit"])
        self.assertEqual("2026-08-13T00:00:00+00:00", result["synced_at"])

    def test_explicit_nonpublic_state_deletes_docs_and_is_retirement_only(self) -> None:
        central = self.root / "central"
        data = central / "_data"
        products = central / "products"
        sources = self.root / "sources"
        data.mkdir(parents=True)
        products.mkdir()
        source_root = sources / "moodle-block_example"
        self.write_valid_index(source_root)
        source_public = source_root / "docs" / "public"
        (products / "moodle-block_example").mkdir()
        (products / "moodle-block_retired").mkdir()
        old = {
            "moodle-block_example": self.matching_provenance(
                "moodle-block_example", source_public
            ),
            "moodle-block_retired": {
                "availability": "commercial-legacy",
                "branch": "main",
                "category": "Blocks",
                "content_sha256": "c" * 64,
                "nav_order": 20,
                "source_commit": "c" * 40,
                "synced_at": "2026-08-13T00:00:00+00:00",
                "title": "Retired",
            },
        }
        data.joinpath("provenance.yml").write_text(json.dumps(old), encoding="utf-8")
        data.joinpath("repositories.yml").write_text("[]", encoding="utf-8")
        inventory = self.root / "inventory.json"
        inventory.write_text(
            json.dumps(
                [
                    self.inventory_entry("moodle-block_example", "commercial-active"),
                    self.inventory_entry("moodle-block_retired", "retired"),
                ]
            ),
            encoding="utf-8",
        )

        result = sync_docs.synchronize(central, sources, inventory)

        self.assertTrue(result["retirement_only"])
        self.assertEqual(["moodle-block_retired"], result["removed"])
        self.assertEqual(
            {"moodle-block_retired": "retired"}, result["removed_states"]
        )
        self.assertTrue((products / "moodle-block_example" / "index.md").is_file())
        self.assertFalse((products / "moodle-block_retired").exists())

    def test_lost_app_access_fails_without_deleting_existing_docs(self) -> None:
        central = self.root / "central"
        data = central / "_data"
        products = central / "products" / "moodle-block_retired"
        sources = self.root / "sources"
        data.mkdir(parents=True)
        products.mkdir(parents=True)
        data.joinpath("provenance.yml").write_text(
            json.dumps(
                {
                    "moodle-block_retired": {
                        "availability": "commercial-active",
                        "branch": "main",
                        "content_sha256": "c" * 64,
                        "source_commit": "c" * 40,
                        "synced_at": "2026-08-13T00:00:00+00:00",
                    }
                }
            ),
            encoding="utf-8",
        )
        data.joinpath("repositories.yml").write_text("[]", encoding="utf-8")
        inventory = self.root / "inventory.json"
        inventory.write_text("[]", encoding="utf-8")

        with self.assertRaisesRegex(sync_docs.SyncError, "no longer accessible"):
            sync_docs.synchronize(central, sources, inventory)

        self.assertTrue(products.is_dir())

    def test_public_metadata_change_is_not_retirement_only(self) -> None:
        old = {
            "moodle-block_example": {
                "availability": "commercial-active",
                "branch": "main",
            }
        }
        new = {
            "moodle-block_example": {
                "availability": "commercial-legacy",
                "branch": "main",
            }
        }
        inventory = sync_docs.normalize_inventory(
            [self.inventory_entry("moodle-block_example", "commercial-legacy")]
        )
        result = sync_docs.classify_changes(old, new, inventory)
        self.assertFalse(result["retirement_only"])
        self.assertEqual(["moodle-block_example"], result["updated"])

    def test_markdown_link_targets_generated_html(self) -> None:
        site = self.root / "_site"
        page = site / "products" / "example" / "index.html"
        page.parent.mkdir(parents=True)
        target = check_links.target_for(site, page, "guide.md", "/moodle-docs")
        self.assertEqual(page.parent / "guide.html", target)


if __name__ == "__main__":
    unittest.main()
