# Product documentation publication

The documentation workflow discovers repositories through the read-only GitHub App installation. The App must remain configured for **All repositories**. App access grants discovery and read access; it does not make a repository or its documentation public. The `product_availability` property remains the publication gate.

## Repository properties

Every repository in the organization must have these organization custom properties:

- `product_availability`: a required single-select value. Valid values are `commercial-active`, `commercial-legacy`, `public-free`, `pre-release`, `in-development`, `internal-only`, `retired`, and `not-a-product`.
- `docs_branch`: a legacy optional string retained as product-source provenance. When empty, the repository default branch is recorded. Documentation is never read from that branch.

Because the App can see every repository, assign `product_availability: not-a-product` to repositories that are not documentation products when practical. Repositories with no property value are ignored as non-products. An explicitly invalid value remains an error, so a typo cannot silently suppress or alter publication.

The publication lifecycle is:

- `in-development`: active product work that is not ready for release; documentation remains nonpublic.
- `pre-release`: release-ready work being prepared for or awaiting Marketplace publication; documentation is published without requiring a Marketplace URL.
- `commercial-active`, `commercial-legacy`, and `public-free`: published products whose documentation must link to their verified Marketplace or store listing where applicable.
- `internal-only`, `retired`, and `not-a-product`: nonpublic states.

A product's only editable public documentation lives in this repository at `content/products/<repository>/index.md`, with approved screenshots under `content/products/<repository>/images/**`. The product directory must contain exactly that single page and its referenced image files. Additional guides, PDFs, maintainer notes, and private material are prohibited. `products/**` is generated publication output and must not be edited by hand.

The central index owns its public `title`, `category`, and positive `nav_order` in front matter. Its H2 headings must be, in order: **Key features**, **Screenshots**, **Requirements**, **Installation**, **Configuration and use**, **Privacy and permissions**, **Troubleshooting**, and **Support and licence**. Product-specific detail belongs under H3 headings on the same page.

Public documentation must describe ZIP installation through Moodle's plugin installer for Moodle plugins and official Chrome Web Store installation for browser extensions. A pre-release Moodle plugin must state that Marketplace publication is pending and explain how to install a provided pre-release ZIP; it does not require a Marketplace URL. Other published Moodle plugins must link to their verified Marketplace page. Public documentation must not contain source repository, commit, branch, filesystem deployment, Composer, npm, or shell instructions. Public issue links may point to the central `moodle-docs` tracker, but must identify products by their public names rather than repository names.

## Promotional screenshots

Every product with a user interface must maintain a reviewed promotional screenshot set. New or refreshed screenshots may be prepared while the repository's current `product_availability` is `commercial-active`, `commercial-legacy`, `public-free`, or `pre-release`. Pre-release assets are published with the rest of the release-ready documentation. A later transition to a nonpublic state does not require deleting historical source assets; synchronization stops publishing the complete product route through the normal retirement process.

The screenshot set must:

- cover each materially distinct product-owned workflow for end users, teachers or managers, and administrators, while adding responsive, theme, empty, completed, permission, or error states only when they are meaningfully different;
- come from the current publication branch and latest supported product or Moodle version, using the newest supported legacy line for `commercial-legacy` products;
- show authentic current UI from the running product or a repeatable preview backed by the current build; composed advertising frames must not alter, invent, or overstate product behaviour;
- use neutral branding, fictional demonstration data, and clean framing, with no personal or customer data, credentials, private or local URLs, debug output, diagnostic footers, distracting browser chrome, unrelated navigation, or implied third-party endorsement;
- target a final canvas of at least 1280 x 800 where the interface supports it, use high-density capture for narrow panels and blocks, and never upscale a low-resolution source;
- prefer PNG for text-heavy interfaces and use JPEG or WebP only when it remains sharp and free of visible compression; and
- live as real, descriptively named kebab-case files under `content/products/<repository>/images/`, with no symlinks, and be linked from the index with meaningful alt text, an italic caption, and a fictional-data disclosure.

Existing store-listing assets may be copied or reproducibly regenerated into the central product image directory. Reviewers must inspect file signatures, dimensions, legibility, clipping, compression, factual accuracy, and full-resolution appearance.

Screenshot coverage and advertising quality remain manual source-review requirements. Synchronization enforces the presence, location, reference, alt text, caption, and disclosure contract without attempting to judge subjective visual completeness.

## Synchronization behavior

The nightly or manually dispatched workflow:

1. creates a read-only token covering all repositories in the App installation;
2. verifies that the installation is configured for **All repositories**, then enumerates that scope and reads each repository's custom-property values;
3. fails without changing generated files if any previously published repository is no longer accessible;
4. validates the matching central source for every repository in a publishable availability state, including `pre-release`;
5. fails closed when an eligible product has no complete central source;
6. generates `products/**`, `_data/repositories.yml`, and `_data/provenance.yml` as one complete snapshot; and
7. opens or updates the protected synchronization pull request.

Transient GitHub API connection errors and HTTP 502–504 responses are retried before the run fails. Contract, lifecycle, App-scope, and missing-content errors are not retried or weakened.

Ordinary additions and updates remain visible for normal pull-request review. A change is classified as retirement-only only when one or more previously published repositories are removed and no public repository is added or updated. Retirement-only pull requests are configured for auto-merge after the required status check passes.

## Removing public documentation

Keep App access while changing the repository to a nonpublic `product_availability` value. The next successful synchronization will generate a pull request that removes the repository's catalog record, provenance, and complete `products/<repository>/**` route.

After that pull request merges and the Pages deployment for its merge commit succeeds, verify that the former product URL returns 404. Only then remove the repository from the App installation if the documentation workflow no longer needs access to it.

Removing App access first is intentionally not interpreted as retirement. The workflow fails closed and preserves the last published snapshot until access is restored and an explicit state transition is synchronized.

The initial migration to central content can update provenance for every published product, so its generated snapshot must be reviewed as a normal synchronization pull request.

## Adding or updating a product

Create a focused change under `content/products/<repository>/**` using source-faithful information from the product's final publication branch and authentic local-runtime screenshots. Merge that central content change and set the repository's `product_availability` to the intended lifecycle state. A manual synchronization run will then discover the repository, validate the central source, and expose the generated diff through the protected synchronization pull request.

Product repositories may retain a concise README that directs readers to this public documentation hub. Do not maintain a second canonical `docs/public/**` tree or copy private and maintainer-only material into this repository.
