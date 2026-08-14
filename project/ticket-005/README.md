# Ticket 005: Separate agent standard HOME from adopted packs

- **ID**: ticket-005
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-14

## Goal and scope

Distil the verified HOME-versus-ADOPT placement rule into the standalone agent
guidance. A `wellmanifest` domain pack defines a standard to adopt; it does not
make a product CLI, daemon or runtime service HOME in the `wellmanifest`
organization. Keep the closed agent v1 schema and grammar unchanged.

## Acceptance criteria

- [x] AC-01: The user's request to continue autonomously and update extracted
  conclusions records `SESSION_EXECUTION_AUTHORIZATION` for this bounded slice.
- [x] AC-02: Guidance separates the owner/operator of an agent runtime from the
  Wellmanifest packs that the runtime adopts.
- [x] AC-03: "within Wellmanifest standardization" is treated as ADOPT, not as
  an inferred HOME placement.
- [x] AC-04: Runtime agent services remain HOME in a runtime organization such
  as `subactor` or `semcod`; `wellmanifest` remains valid HOME for a domain
  pack rather than a product daemon.
- [x] AC-05: The agent v1 JSON Schema, request grammar and their digests remain
  unchanged; conformance, governance and diff hygiene pass.

## Validation evidence

- `python3 standard/conformance.py --all`: 4 positive variants and 15
  adversarial cases; pinned schema and grammar digests unchanged.
- `./project/governance-check.sh`: `GOV-PASS`, 0 errors and 0 warnings.
- `git diff --check`: pass; `standard/**` has no diff from the accepted base.
- The Subactor artifact registry has no managed entry for this external
  standalone standard, so no registry projection is changed by this ticket.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
