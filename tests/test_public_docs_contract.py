from __future__ import annotations

from pathlib import Path
import struct
import tempfile
import unittest

from scripts import check_external_links
from scripts import public_docs_contract as contract


class PublicDocsContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.write_valid_index()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def valid_text(self, marketplace: str = "https://marketplace.moodle.com/plugins/block_example") -> str:
        return f"""---
title: Example
category: Blocks
nav_order: 10
---

# Example

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

Download the ZIP from the [Moodle Marketplace]({marketplace}), then install it through **Site administration > Plugins > Install plugins**.

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
"""

    def write_valid_index(self) -> None:
        public = self.root / "docs" / "public"
        images = public / "images"
        images.mkdir(parents=True)
        images.joinpath("example-overview.png").write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + struct.pack(">I", 13)
            + b"IHDR"
            + struct.pack(">II", 1280, 800)
            + b"\x08\x02\x00\x00\x00"
        )
        public.joinpath("index.md").write_text(self.valid_text(), encoding="utf-8")

    def validate(self, availability: str = "commercial-active") -> contract.ContractResult:
        return contract.validate_docs_tree(
            self.root, "moodle-block_example", availability
        )

    def test_valid_single_page_contract_passes(self) -> None:
        result = self.validate()
        self.assertEqual([], result.errors)
        self.assertEqual([], result.warnings)

    def test_reordered_headings_are_rejected(self) -> None:
        index = self.root / "docs" / "public" / "index.md"
        text = index.read_text(encoding="utf-8")
        text = text.replace("## Requirements", "## Temporary").replace(
            "## Installation", "## Requirements"
        ).replace("## Temporary", "## Installation")
        index.write_text(text, encoding="utf-8")
        self.assertTrue(any("required order" in error for error in self.validate().errors))

    def test_additional_guide_is_rejected(self) -> None:
        self.root.joinpath("docs/public/guide.md").write_text("# Guide\n", encoding="utf-8")
        self.assertTrue(any("prohibited documentation file" in error for error in self.validate().errors))

    def test_docs_internal_is_rejected(self) -> None:
        internal = self.root / "docs" / "internal"
        internal.mkdir()
        internal.joinpath("notes.md").write_text("private\n", encoding="utf-8")
        errors = self.validate().errors
        self.assertTrue(any("docs/internal is prohibited" in error for error in errors))

    def test_screenshot_alt_caption_and_disclosure_are_required(self) -> None:
        index = self.root / "docs" / "public" / "index.md"
        text = index.read_text(encoding="utf-8")
        text = text.replace("![Example product overview]", "![]")
        text = text.replace("*The example workflow shown in Moodle.*\n\n", "")
        text = text.replace("All people and content shown are fictional demonstration data.\n\n", "")
        index.write_text(text, encoding="utf-8")
        errors = self.validate().errors
        self.assertTrue(any("empty alt text" in error for error in errors))
        self.assertTrue(any("italic caption" in error for error in errors))
        self.assertTrue(any("fictional demonstration data" in error for error in errors))

    def test_image_signature_must_match_filename(self) -> None:
        image = self.root / "docs" / "public" / "images" / "example-overview.png"
        image.write_bytes(b"\xff\xd8\xff\xd9")
        errors = self.validate().errors
        self.assertTrue(any("signature" in error or "start-of-frame" in error for error in errors))

    def test_deprecated_and_source_repository_links_are_rejected(self) -> None:
        index = self.root / "docs" / "public" / "index.md"
        text = index.read_text(encoding="utf-8")
        text += "\n[Old support](https://pukunui.com/home/location/malaysia/)\n"
        text += "[Source](https://github.com/PukunuiMalaysia/moodle-block_example/commit/abc)\n"
        index.write_text(text, encoding="utf-8")
        errors = self.validate().errors
        self.assertTrue(any("deprecated Malaysia" in error for error in errors))
        self.assertTrue(any("source commit" in error for error in errors))

    def test_public_marketplace_link_is_required(self) -> None:
        index = self.root / "docs" / "public" / "index.md"
        index.write_text(self.valid_text("https://example.com/product"), encoding="utf-8")
        result = self.validate("commercial-active")
        self.assertTrue(any("verified Marketplace" in error for error in result.errors))
        result = self.validate("pre-release")
        self.assertFalse(any("verified Marketplace" in error for error in result.errors))
        self.assertTrue(any("verified Marketplace" in warning for warning in result.warnings))

    def test_alphabetical_navigation_uses_tens(self) -> None:
        alpha = contract.ContractResult(
            repository="moodle-block_alpha", title="Alpha", category="Blocks", nav_order=20
        )
        beta = contract.ContractResult(
            repository="moodle-block_beta", title="Beta", category="Blocks", nav_order=10
        )
        errors = contract.validate_navigation_order([beta, alpha])
        self.assertEqual(2, len(errors))

    def test_external_link_status_classification(self) -> None:
        self.assertEqual("ok", check_external_links.classify_status(200))
        self.assertEqual("ok", check_external_links.classify_status(302))
        self.assertEqual("error", check_external_links.classify_status(404))
        self.assertEqual("warning", check_external_links.classify_status(429))


if __name__ == "__main__":
    unittest.main()
