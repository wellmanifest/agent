# Ticket 004: Refresh operational autonomy readiness rules

- **ID**: ticket-004
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-14

## Goal and scope

Refresh the standalone agent guidance after the exact-reference Hub route and
its permanent HTTP regression were independently reviewed and merged. Replace
the stale "missing provider route" conclusion with a distinction between
structural capability completeness and operational readiness, which still
requires one live controller-owned grant/revoke and Vault read-back canary.

Also codify two autonomy recovery rules reproduced during publication: an
exhausted control-plane API transport may switch to an equivalent authenticated
transport only while preserving exact-state and independent-review bindings,
and a remotely merged but locally active workstream reservation must be closed
from integrated main rather than bypassed with a new ticket.

## Acceptance criteria

- [x] AC-01: The user's request to continue autonomously and update extracted
  conclusions records `SESSION_EXECUTION_AUTHORIZATION` for this bounded slice.
- [x] AC-02: The evidence basis binds the exact reviewed Hub route and durable
  regression revisions without making them runtime dependencies.
- [x] AC-03: The standard distinguishes structural exact-reference completion
  from operational readiness and requires a live, secret-free canary receipt.
- [x] AC-04: A degraded control-plane transport may be substituted only with
  unchanged exact-head, hosted-check, identity and read-back guarantees; retry
  storms and policy bypass remain forbidden.
- [x] AC-05: A stale local workstream reservation after remote merge is
  reconciled and closed from integrated main, never bypassed with force-new.
- [x] AC-06: Conformance, governance, diff hygiene and Subactor artifact build
  and check pass for the two-file guidance clarification.

## Validation evidence

- `python3 standard/conformance.py --all`: 4 positive variants; 15 adversarial
  cases rejected; schema and grammar digests unchanged.
- Deterministic governance: `GOV-PASS`, 0 errors and 0 warnings.
- `git diff --check`: pass.
- Platform artifact registry: 614 valid artifacts, 0 invalid and 0 drift.
- Platform unstaged, staged and untracked fingerprints are identical before
  and after artifact validation.

## Delivery evidence

- PR #6 froze exact head `6c4e3eca2f820a423f5b873e1b3778db10fe6d59`.
- Validator run `31799560345` submitted trusted approval review `4937022633`
  for that exact head and explicitly merged the pull request.
- Merge commit `6f6e6562aad5c911f34b148d7ef70ae2601d33a3` has the same tree as the
  reviewed head; the remote implementation branch was deleted.

## Evidence basis

- Hub route head `62fdd105a9263b2c6bdc8e86db95145edb70365c`, merged as
  `3bc723fe9ca7b3a774c0f67a22595c06e8f4ec7c`, added authenticated
  `POST /v1/commands/harvest-reference` with exact delegation and no secret
  response. Validator run `31797279515` approved the exact head.
- Regression head `f59cc503312c8e58a651fbd6bc944afd005e6920`, merged as
  `feb2548401a49757018baa2c6607ba0b8ce90f1e`, permanently proves bearer and
  request validation, byte-exact selection proof, secret-free receipt and
  legacy compatibility. Validator run `31798413692` approved the exact head;
  the full Hub suite passed 168 tests with 1 skipped.
- Shared GraphQL quota reached zero during that publication. REST froze the
  same head before and after both hosted checks, dispatched the independent
  Validator App with explicit merge, and read back its exact review and merge.
- Ticket 017's already merged application work remained locally active and
  blocked ticket allocation. Governance-only PR #40 closed it from integrated
  main through Validator run `31797921804`; no force-new bypass was used.
- The Subactor artifact registry contains no managed entry for this external
  standalone standard. Platform artifact build/check remains required after
  the text edits.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
