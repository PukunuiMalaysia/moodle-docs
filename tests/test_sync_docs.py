from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_docs.py"
SPEC = importlib.util.spec_from_file_location("sync_docs", SCRIPT)
sync_docs = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(sync_docs)

LINK_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_links.py"
LINK_SPEC = importlib.util.spec_from_file_location("check_links", LINK_SCRIPT)
check_links = importlib.util.module_from_spec(LINK_SPEC)
assert LINK_SPEC.loader is not None
LINK_SPEC.loader.exec_module(check_links)


class SyncDocsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.public = self.root / "docs" / "public"
        self.public.mkdir(parents=True)
        (self.public / "index.md").write_text(
            "---\ntitle: Example\ncategory: Blocks\nnav_order: 10\n---\n\n# Example\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

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

    def test_private_source_navigation_omits_repository_link(self) -> None:
        rendered = sync_docs.inject_navigation(
            (self.public / "index.md").read_text(encoding="utf-8"),
            repository="moodle-block_example",
            title="Example",
            category="Blocks",
            nav_order=10,
            relative=Path("index.md"),
            source_commit="a" * 40,
            source_public=False,
            availability="commercial-active",
            has_children=True,
        )
        self.assertIn('parent: "Blocks"', rendered)
        self.assertIn("permalink: /products/moodle-block_example/", rendered)
        self.assertIn("Source revision: `aaaaaaaaaaaa`", rendered)
        self.assertNotIn("moodle-block_example/commit", rendered)

    def test_legacy_source_gets_public_status_notice(self) -> None:
        rendered = sync_docs.inject_navigation(
            (self.public / "index.md").read_text(encoding="utf-8"),
            repository="moodle-block_example",
            title="Example",
            category="Blocks",
            nav_order=10,
            relative=Path("index.md"),
            source_commit="a" * 40,
            source_public=True,
            availability="commercial-legacy",
            has_children=False,
        )
        self.assertIn("**Legacy product:**", rendered)
        self.assertIn("moodle-block_example/commit/", rendered)

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
        source_public = sources / "moodle-block_example" / "docs" / "public"
        source_public.mkdir(parents=True)
        source_public.joinpath("index.md").write_text(
            (self.public / "index.md").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
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
