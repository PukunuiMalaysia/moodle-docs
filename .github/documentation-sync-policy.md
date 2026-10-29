# Documentation synchronization policy

Discovery uses the complete source App inventory and the existing product
availability properties. No repository-specific filter or property override is
used. Existing published products remain fail-closed: inaccessible repositories,
missing sources, partial/invalid content and unsafe paths stop the snapshot.

An eligible product with an entirely absent central source directory may be
blocked from first publication without blocking updates to other products only
when its name is absent from **all** existing provenance, catalog and generated
routes. Broken symlinks count as existing paths and must fail validation. No
fallback or synthesized product page is published.

The result reports `blocked_new_products` with reasons. Workflow warnings and
step summaries show those blockers even when no generated diff exists; generated
PR bodies also identify them. Any blocker disables retirement-only automatic
merge. Inventory availability remains unchanged and is not presented as proof
that documentation exists. A blocked product becomes eligible for inclusion only
when its canonical source is supplied and passes the normal contract.

This narrow exception was authorized on 29 October 2026 to allow Boleh's reviewed
source update while unrelated, never-published Bento lacked its central source.
It replaces all-eligible atomic failure only for this absent-new-source case.
All existing snapshot atomic replacement, navigation, source safety, PR/status,
build/link validation and release-manifest consistency guards remain in force.
