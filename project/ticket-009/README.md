# Ticket 009: MCP client authority boundaries for Taskand agents

- **ID**: ticket-009
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-19

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: user request 2026-09-19 authorizes guidance
in the owning Wellmanifest standards for Taskand MCP reuse. Intake: Taskand
Planfile PLF-005. Scope: indexed informational client authority boundaries,
preserving agent/v1, runtime ownership and independent publication approval.
No runtime code, normative schema changes or secret access.

Publication continuation: user explicitly authorized the proposed protected
PR/review/merge path on 2026-09-19. Intake PLF-007 follows completed local
PLF-005. Dependency ticket-010 was independently reviewed and merged in PR #14.
The new accepted base is that observed merge, not an unreviewed local adoption.

Exact-range publication validation found inconsistent XS/30-minute metadata
(XS permits at most 10 minutes). Corrected the declaration to S, retaining
the original 30-minute estimate and all tighter budgets: two files, one
component, no public interface changes or dependencies. No scope was added.

2026-09-19: User explicitly authorized adoption/metadata repairs. Dependency
ticket-010 supplies the pinned local checker. Continue in canonical linked
checkout on that committed dependency; preserve dirty primary AGENTS.md.

## Acceptance criteria

- [x] AC-01: Document least-privilege tool selection, effects, isolation and denial tests.
- [x] AC-02: Pass documentation and managed governance checks.

## Tracking boundary

Current boundary: local material delivery validated on dependency ticket-010.
Docs completion, managed governance and all 7 Docs adoption tests passed.
Agent conformance passed 4 positive variants and 15 adversarial cases;
publisher conformance passed its profile and 14 adversarial cases.
The blocker below is historical and resolved by authorized adoption.
At the initial local boundary there was no push, PR or merge. Publication now
proceeds through the protected Validator; no protected CI rollout or runtime
implementation is included.

2026-09-19: No implementation started. Docs prepare at trusted source revision
19efafbeb18923cfd51cc69bd519330488500137 fails: no .governance/docs.json,
no tracked docs/README.md, unresolved managed SNAPSHOT_MIGRATION.md inventory.
Next: bounded Docs adoption in its owning governance scope, then successful
prepare before document generation. No lease, commit or remote effect.
The allocator-created carrier remains in primary; do not write implementation
there. Resolve the canonical ticket-009 worktree only after admission succeeds.

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
