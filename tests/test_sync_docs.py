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
        (self.public / "index.md").write_text("---\ntitle: Example\n---\n\n# Example\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

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

    def test_navigation_and_provenance_are_injected(self) -> None:
        rendered = sync_docs.inject_navigation(
            (self.public / "index.md").read_text(encoding="utf-8"),
            repository="moodle-block_example",
            title="Example",
            category="Blocks",
            nav_order=10,
            relative=Path("index.md"),
            source_commit="a" * 40,
            has_children=True,
        )
        self.assertIn('parent: "Blocks"', rendered)
        self.assertIn("permalink: /products/moodle-block_example/", rendered)
        self.assertIn("aaaaaaaaaaaa", rendered)

    def test_config_requires_exact_allowlist_size(self) -> None:
        with self.assertRaisesRegex(sync_docs.SyncError, "exactly 22"):
            sync_docs.validate_config([])

    def test_previous_provenance_is_reused_for_unchanged_content(self) -> None:
        destination = self.root / "output"
        digest = sync_docs.content_digest(self.public)
        old = {
            "moodle-block_example": {
                "content_sha256": digest,
                "source_commit": "b" * 40,
                "synced_at": "2026-08-13T00:00:00+00:00",
            }
        }
        result = sync_docs.sync_repository(
            {
                "repository": "moodle-block_example",
                "title": "Example",
                "category": "Blocks",
                "nav_order": 10,
            },
            self.root,
            destination,
            old,
            "main",
        )
        self.assertEqual("b" * 40, result["source_commit"])
        self.assertEqual("2026-08-13T00:00:00+00:00", result["synced_at"])

    def test_markdown_link_targets_generated_html(self) -> None:
        site = self.root / "_site"
        page = site / "products" / "example" / "index.html"
        page.parent.mkdir(parents=True)
        target = check_links.target_for(site, page, "guide.md", "/moodle-docs")
        self.assertEqual(page.parent / "guide.html", target)


if __name__ == "__main__":
    unittest.main()
