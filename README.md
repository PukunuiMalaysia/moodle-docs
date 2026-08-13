# Pukunui Moodle documentation

This public repository aggregates approved user and administrator documentation from the `docs/public` directory of PukunuiMalaysia Moodle repositories and publishes it with Jekyll and Just the Docs.

Product pages under `products/` and `_data/provenance.yml` are generated. Edit product documentation in its source repository, then wait for or manually run the nightly synchronization workflow. A maintainer reviews the resulting pull request before publication.

## Local checks

```sh
python3 -m unittest discover -s tests
python3 scripts/sync_docs.py --local-root /path/to/PukunuiMalaysia/repos
bundle exec jekyll build --baseurl /moodle-docs --strict_front_matter
```

## Publication boundary

Only `docs/public/**` is eligible for publication. Internal material belongs under `docs/internal/**` and is never read by the synchronization tool. Source directories must contain `docs/public/index.md`; symlinks and unapproved file types make the complete synchronization fail.

## Licensing

Original documentation is licensed under [Creative Commons Attribution 4.0 International](LICENSE). Automation code is licensed under the [MIT License](LICENSE-CODE). Content retaining another notice remains under that notice.
