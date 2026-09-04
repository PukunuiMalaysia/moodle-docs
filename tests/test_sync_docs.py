from __future__ import annotations

import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock

from scripts import check_links, sync_docs


class SyncDocsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.public = self.root / "product"
        self.public.mkdir(parents=True)
        self.write_valid_index(self.public)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_valid_index(self, product_root: Path, title: str = "Example") -> None:
        images = product_root / "images"
        images.mkdir(parents=True, exist_ok=True)
        images.joinpath("example-overview.png").write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + struct.pack(">I", 13)
            + b"IHDR"
            + struct.pack(">II", 1280, 800)
            + b"\x08\x02\x00\x00\x00"
        )
        product_root.joinpath("index.md").write_text(
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
            "content_commit": "b" * 40,
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

    def test_index_requires_centrally_owned_navigation_metadata(self) -> None:
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

    def test_legacy_product_gets_public_status_notice(self) -> None:
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

    def test_pre_release_product_gets_public_status_notice(self) -> None:
        rendered = sync_docs.inject_navigation(
            (self.public / "index.md").read_text(encoding="utf-8"),
            repository="moodle-block_example",
            title="Example",
            category="Blocks",
            nav_order=10,
            relative=Path("index.md"),
            availability="pre-release",
            has_children=False,
        )
        self.assertIn("**Pre-release product:**", rendered)
        self.assertIn("Marketplace listing may not yet be available", rendered)

    def test_inventory_ignores_missing_product_availability(self) -> None:
        inventory = sync_docs.normalize_inventory(
            [
                {
                    "repository": "moodle-block_example",
                    "default_branch": "main",
                    "visibility": "private",
                }
            ]
        )
        self.assertIsNone(inventory[0]["availability"])

    def test_inventory_rejects_invalid_product_availability(self) -> None:
        with self.assertRaisesRegex(sync_docs.SyncError, "invalid product_availability"):
            sync_docs.normalize_inventory(
                [
                    self.inventory_entry("moodle-block_example", "commercial-actve")
                ]
            )

    def test_inventory_rejects_invalid_docs_branch(self) -> None:
        entry = self.inventory_entry("moodle-block_example", "commercial-active")
        entry["properties"]["docs_branch"] = "../unsafe"  # type: ignore[index]
        with self.assertRaisesRegex(sync_docs.SyncError, "Invalid docs_branch"):
            sync_docs.normalize_inventory([entry])

    def test_transient_github_failure_is_retried(self) -> None:
        failure = mock.Mock(returncode=1, stderr="HTTP 503: unavailable", stdout="")
        success = mock.Mock(returncode=0, stderr="", stdout='{"ok": true}\n')
        with (
            mock.patch.object(sync_docs.subprocess, "run", side_effect=[failure, success]) as runner,
            mock.patch.object(sync_docs.time, "sleep") as sleep,
        ):
            output = sync_docs.run(["gh", "api", "example"])

        self.assertEqual('{"ok": true}', output)
        self.assertEqual(2, runner.call_count)
        sleep.assert_called_once_with(1)

    def test_permanent_github_failure_is_not_retried(self) -> None:
        failure = mock.Mock(returncode=1, stderr="HTTP 404: not found", stdout="")
        with mock.patch.object(sync_docs.subprocess, "run", return_value=failure) as runner:
            with self.assertRaisesRegex(sync_docs.SyncError, "HTTP 404"):
                sync_docs.run(["gh", "api", "example"])

        runner.assert_called_once()

    def test_remote_discovery_requires_all_repository_app_scope(self) -> None:
        with mock.patch.object(
            sync_docs,
            "command_json",
            return_value={"repository_selection": "selected"},
        ) as command:
            with self.assertRaisesRegex(
                sync_docs.SyncError, "must grant access to all repositories"
            ):
                sync_docs.discover_all_repositories({"GH_TOKEN": "test-token"})

        command.assert_called_once_with(
            ["gh", "api", "installation"], env={"GH_TOKEN": "test-token"}
        )

    def test_user_token_discovery_uses_organization_repository_list(self) -> None:
        with mock.patch.object(
            sync_docs,
            "command_json",
            side_effect=[
                [[
                    {
                        "name": "moodle-block_example",
                        "owner": {"login": "PukunuiMalaysia"},
                        "default_branch": "main",
                        "visibility": "private",
                        "private": True,
                    }
                ]],
                [{"property_name": "product_availability", "value": None}],
            ],
        ) as command:
            inventory = sync_docs.discover_org_repositories({"GH_TOKEN": "test-token"})

        self.assertEqual("moodle-block_example", inventory[0]["repository"])
        self.assertIsNone(inventory[0]["availability"])
        self.assertEqual(2, command.call_count)

    def test_pre_release_is_published_and_in_development_is_not(self) -> None:
        central = self.root / "central"
        data = central / "_data"
        products = central / "products"
        content = central / "content" / "products"
        data.mkdir(parents=True)
        products.mkdir()
        pre_release = content / "moodle-block_prerelease"
        self.write_valid_index(pre_release, "Pre-release")
        index = pre_release / "index.md"
        text = index.read_text(encoding="utf-8").replace(
            "Download the ZIP from the [Moodle Marketplace]"
            "(https://marketplace.moodle.com/plugins/block_example), then install it",
            "Marketplace publication is pending. If you have been provided with the "
            "pre-release ZIP, install it",
        )
        index.write_text(text, encoding="utf-8")
        data.joinpath("provenance.yml").write_text("{}", encoding="utf-8")
        data.joinpath("repositories.yml").write_text("[]", encoding="utf-8")
        inventory = self.root / "inventory.json"
        inventory.write_text(
            json.dumps(
                [
                    self.inventory_entry("moodle-block_prerelease", "pre-release"),
                    self.inventory_entry("moodle-block_development", "in-development"),
                ]
            ),
            encoding="utf-8",
        )

        with mock.patch.object(sync_docs, "content_commit", return_value="d" * 40):
            result = sync_docs.synchronize(central, inventory_path=inventory)

        self.assertEqual(["moodle-block_prerelease"], result["added"])
        self.assertEqual(1, result["published_repository_count"])
        self.assertTrue((products / "moodle-block_prerelease" / "index.md").is_file())
        self.assertFalse((products / "moodle-block_development").exists())
        provenance = json.loads(data.joinpath("provenance.yml").read_text(encoding="utf-8"))
        self.assertEqual("pre-release", provenance["moodle-block_prerelease"]["availability"])

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
        with mock.patch.object(sync_docs, "content_commit", return_value="b" * 40):
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
                self.public,
                destination,
                old,
                self.root,
            )
        self.assertEqual("b" * 40, result["content_commit"])
        self.assertEqual("2026-08-13T00:00:00+00:00", result["synced_at"])

    def test_explicit_nonpublic_state_deletes_docs_and_is_retirement_only(self) -> None:
        central = self.root / "central"
        data = central / "_data"
        products = central / "products"
        content = central / "content" / "products"
        data.mkdir(parents=True)
        products.mkdir()
        source_public = content / "moodle-block_example"
        self.write_valid_index(source_public)
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
                "content_commit": "c" * 40,
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

        with mock.patch.object(sync_docs, "content_commit", return_value="b" * 40):
            result = sync_docs.synchronize(central, inventory_path=inventory)

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
        data.mkdir(parents=True)
        products.mkdir(parents=True)
        data.joinpath("provenance.yml").write_text(
            json.dumps(
                {
                    "moodle-block_retired": {
                        "availability": "commercial-active",
                        "branch": "main",
                        "content_sha256": "c" * 64,
                        "content_commit": "c" * 40,
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
            sync_docs.synchronize(central, inventory_path=inventory)

        self.assertTrue(products.is_dir())

    def test_missing_central_source_fails_without_replacing_generated_docs(self) -> None:
        central = self.root / "central"
        data = central / "_data"
        product = central / "products" / "moodle-block_example"
        data.mkdir(parents=True)
        product.mkdir(parents=True)
        product.joinpath("index.md").write_text("published\n", encoding="utf-8")
        data.joinpath("provenance.yml").write_text("{}", encoding="utf-8")
        data.joinpath("repositories.yml").write_text("[]", encoding="utf-8")
        inventory = self.root / "inventory.json"
        inventory.write_text(
            json.dumps([self.inventory_entry("moodle-block_example", "commercial-active")]),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(sync_docs.SyncError, "Missing required directory"):
            sync_docs.synchronize(central, inventory_path=inventory)

        self.assertEqual("published\n", product.joinpath("index.md").read_text(encoding="utf-8"))

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
