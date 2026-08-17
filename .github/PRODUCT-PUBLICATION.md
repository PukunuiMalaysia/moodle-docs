# Product documentation publication

The documentation workflow discovers repositories through the read-only GitHub App installation. The App must remain configured for **Only select repositories**. Selecting a repository grants discovery and read access; it does not make the repository or its documentation public.

## Repository properties

Every repository selected in the App installation must have these organization custom properties:

- `product_availability`: a required single-select value. Valid values are `commercial-active`, `commercial-legacy`, `public-free`, `pre-release`, `internal-only`, `retired`, and `not-a-product`.
- `docs_branch`: an optional string. When empty, the repository default branch is used.

Only `commercial-active`, `commercial-legacy`, and `public-free` are published. All other values are nonpublic states.

A publishable repository must provide `docs/public/index.md`. Its front matter owns the public `title`, `category`, and positive integer `nav_order`. Only validated files under `docs/public/**` are copied. `docs/internal/**`, repository files outside the public tree, hidden paths, symlinks, and unapproved file types are never published.

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
