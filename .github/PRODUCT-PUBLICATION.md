# Product documentation publication

The documentation workflow discovers repositories through the read-only GitHub App installation. The App must remain configured for **Only select repositories**. Selecting a repository grants discovery and read access; it does not make the repository or its documentation public.

## Repository properties

Every repository selected in the App installation must have these organization custom properties:

- `product_availability`: a required single-select value. Valid values are `commercial-active`, `commercial-legacy`, `public-free`, `pre-release`, `internal-only`, `retired`, and `not-a-product`.
- `docs_branch`: an optional string. When empty, the repository default branch is used.

Only `commercial-active`, `commercial-legacy`, and `public-free` are published. All other values are nonpublic states.

A product-facing repository must use the single-page documentation contract. It provides exactly one documentation page at `docs/public/index.md` and may store approved screenshots under `docs/public/images/**`. No other files are allowed beneath `docs/**`; additional guides, PDFs, maintainer notes, and `docs/internal/**` are prohibited.

The source index owns its public `title`, `category`, and positive `nav_order` in front matter. Its H2 headings must be, in order: **Key features**, **Screenshots**, **Requirements**, **Installation**, **Configuration and use**, **Privacy and permissions**, **Troubleshooting**, and **Support and licence**. Product-specific detail belongs under H3 headings on the same page.

Public documentation must describe Marketplace ZIP installation for Moodle plugins and official Chrome Web Store installation for browser extensions. It must not contain source repository, commit, branch, filesystem deployment, Composer, npm, or shell instructions. Public issue links may point to the central `moodle-docs` tracker, but must identify products by their public names rather than repository names.

## Promotional screenshots

Every product with a user interface must maintain a reviewed promotional screenshot set. New or refreshed screenshots may be prepared while the repository's current `product_availability` is `commercial-active`, `commercial-legacy`, `public-free`, or `pre-release`. Pre-release assets remain nonpublic until the product moves to a publishable state. A later transition to another nonpublic state does not require deleting historical source assets; synchronization stops publishing the complete product route through the normal retirement process.

The screenshot set must:

- cover each materially distinct product-owned workflow for end users, teachers or managers, and administrators, while adding responsive, theme, empty, completed, permission, or error states only when they are meaningfully different;
- come from the current publication branch and latest supported product or Moodle version, using the newest supported legacy line for `commercial-legacy` products;
- show authentic current UI from the running product or a repeatable preview backed by the current build; composed advertising frames must not alter, invent, or overstate product behaviour;
- use neutral branding, fictional demonstration data, and clean framing, with no personal or customer data, credentials, private or local URLs, debug output, diagnostic footers, distracting browser chrome, unrelated navigation, or implied third-party endorsement;
- target a final canvas of at least 1280 x 800 where the interface supports it, use high-density capture for narrow panels and blocks, and never upscale a low-resolution source;
- prefer PNG for text-heavy interfaces and use JPEG or WebP only when it remains sharp and free of visible compression; and
- live as real, descriptively named kebab-case files under `docs/public/images/`, with no symlinks, and be linked from the index with meaningful alt text, an italic caption, and a fictional-data disclosure.

Existing store-listing assets outside `docs/public/**` may be copied or reproducibly regenerated into `docs/public/images/`. Reviewers must inspect file signatures, dimensions, legibility, clipping, compression, factual accuracy, and full-resolution appearance.

Screenshot coverage and advertising quality remain manual source-review requirements. Synchronization enforces the presence, location, reference, alt text, caption, and disclosure contract without attempting to judge subjective visual completeness.

## Synchronization behavior

The nightly or manually dispatched workflow:

1. creates a read-only token covering all repositories selected in the App installation;
2. enumerates that exact installation scope and reads each repository's custom-property values;
3. fails without changing generated files if any previously published repository is no longer accessible;
4. clones and validates only repositories in a public availability state;
5. generates `products/**`, `_data/repositories.yml`, and `_data/provenance.yml` as one complete snapshot; and
6. opens or updates the protected synchronization pull request.

Ordinary additions and updates remain visible for normal pull-request review. A change is classified as retirement-only only when one or more previously published repositories are removed and no public repository is added or updated. Retirement-only pull requests are configured for auto-merge after the required status check passes.

## Removing public documentation

Keep App access while changing the repository to a nonpublic `product_availability` value. The next successful synchronization will generate a pull request that removes the repository's catalog record, provenance, and complete `products/<repository>/**` route.

After that pull request merges and the Pages deployment for its merge commit succeeds, verify that the former product URL returns 404. Only then remove the repository from the App installation if the documentation workflow no longer needs access to it.

Removing App access first is intentionally not interpreted as retirement. The workflow fails closed and preserves the last published snapshot until access is restored and an explicit state transition is synchronized.

The initial migration from the fixed inventory can contain both additions and removals, so it is not retirement-only and must be reviewed as a normal synchronization pull request.
