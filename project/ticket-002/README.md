# Ticket 002: Distill diagnostic agent evidence rules

- **ID**: ticket-002
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-14

## Goal and scope

Distil current, verified behavior from Diagit and Doctor into compatible
`wellmanifest.agent/v1` guidance. The change clarifies that read-only
diagnosis and validation may inspect a product or its control plane, while
repair remains a product-only pull-request mutation.

The standard will also define how diagnostic findings, fleet read models,
plans, receipts and operational logs preserve stable identity, target
attribution, bounded redacted evidence and tamper detection. It does not add a
document variant, change the JSON Schema or GBNF, or make Diagit or Doctor a
runtime dependency.

## Acceptance criteria

- [x] AC-01: The evidence basis records the exact verified Diagit and Doctor
  revisions without making either repository a runtime dependency.
- [x] AC-02: Conformance accepts read-only diagnosis of a control-plane target
  and rejects product repair directed at a control-plane target.
- [x] AC-03: Normative guidance requires stable diagnostic identity, explicit
  target attribution, bounded redacted evidence, deterministic bounded read
  models and ownership-boundary deduplication.
- [x] AC-04: Normative guidance keeps findings and plans non-authoritative and
  composes receipts with immutable evidence, tamper-evident operational logs,
  independent validation and exact-state read-back.
- [x] AC-05: Local, networkless Docker, governance, diff-hygiene and Subactor
  artifact-registry checks pass for the bounded change.
- [x] AC-06: Credential discovery remains metadata-only, while exact-route
  runtime grant issuance, injection and revocation remain controller-owned and
  fail closed without proof.

## Authorization

The request to continue work across Diagit and Doctor and update the extracted
conclusions in this repository creates `SESSION_EXECUTION_AUTHORIZATION` for
this bounded ticket. It authorizes the ticket branch, the three implementation
files declared in intent, validation, a commit, pushing the ticket branch and
opening a pull request. It does not authorize a direct push to `main`, trusted
review, merge, tag, release, destructive action or secret access.

## Evidence basis

- Diagit `origin/main` at `b6958c40598adcc44dd02e184bc7dc92325a90b9`
  (including remote finding and shared-stash behavior from
  `ec01d24e20882f60938b2641f787c69863303bdc`) passed 109 tests, Ruff and mypy
  in a detached read-only worktree.
- Doctor `origin/main` at `1aed648d7c45588cf1e04d95ce315b64251c80bd`
  passed its hosted CI and contribution-policy checks before this ticket.
- Subactor's clean credential-harvest connector
  `74df0673612f31712c13791b57030441f921b2bb`, locally validated Inventory
  credential-reference handoff and tenant-scoped exact lookup
  `ead9a678bd556da7ffb338bb168df0a0d90b4661`, and locally validated Control ticket
  `d518444aae1634afc7f4b83e3e761509f7dbb069` establish the runtime grant
  boundary. The dirty, stale Hub checkout is excluded from normative evidence.
- The Subactor artifact registry has no managed entry for these external
  source paths or this standalone standard; Platform artifact build and check
  remain required after the managed text edits.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
