import json
from pathlib import Path
import tempfile
import unittest

from scripts.release_manifest import build_manifest


class ReleaseManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "_data").mkdir()
        self.site = self.root / "_site"
        page = self.site / "products/moodle-block_example/index.html"
        page.parent.mkdir(parents=True)
        page.write_text("rendered snapshot")
        self.provenance = {"moodle-block_example": {
            "content_sha256": "a" * 64, "availability": "public-free"}}
        self.write_data()

    def write_data(self):
        (self.root / "_data/provenance.yml").write_text(json.dumps(self.provenance))
        (self.root / "_data/repositories.yml").write_text(json.dumps([
            {"repository": "moodle-block_example"}]))

    def test_uses_published_provenance_not_newer_canonical_source(self):
        source = self.root / "content/products/moodle-block_example"
        source.mkdir(parents=True)
        (source / "index.md").write_text("new documentation not yet synchronized")
        result = build_manifest(self.root, self.site, "b" * 40)
        self.assertEqual(result["products"]["moodle-block_example"]["source_sha256"], "a" * 64)
        self.assertEqual(result["commit"], "b" * 40)

    def test_missing_route_fails(self):
        (self.site / "products/moodle-block_example/index.html").unlink()
        with self.assertRaises(ValueError):
            build_manifest(self.root, self.site, "b" * 40)

    def test_invalid_digest_fails(self):
        self.provenance["moodle-block_example"]["content_sha256"] = "bad"
        self.write_data()
        with self.assertRaises(ValueError):
            build_manifest(self.root, self.site, "b" * 40)

    def test_invalid_commit_fails(self):
        with self.assertRaises(ValueError):
            build_manifest(self.root, self.site, "main")

    def test_catalog_mismatch_fails(self):
        self.provenance.clear()
        self.write_data()
        with self.assertRaises(ValueError):
            build_manifest(self.root, self.site, "b" * 40)
