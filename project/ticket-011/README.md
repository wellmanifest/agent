# Ticket 011: Keep agent delivery reports inside their owning repository

- **ID**: ticket-011
- **Owner**: codex:repo-local-report-delivery
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-09-19

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: user requested investigation and repair of
home-local report placement and Wellman adoption on 2026-09-19. This disjoint
slice corrects agent guidance and delivers the agent-specific incident report
inside this repository. Runtime Wellman changes remain owned by issue #2;
no takeover, bulk adoption, credential migration or publication is inferred.

Canonical result: `docs/ANALYSIS/REPORT_PLACEMENT_WELLMAN.md`.
Queue: semcod/taskand-glm53 PLF-009; dependency: wellmanifest/wellman#2.

## Acceptance criteria

- [x] AC-01: Explain the final-report/recovery-store confusion with exact evidence.
- [x] AC-02: Guidance distinguishes repository/worktree roots and private versus
      protected external state; report and index pass pinned Docs completion.
- [x] AC-03: Managed governance and existing conformance tests pass; publication
      and Wellman rollout states remain explicit.

Validation: both pinned Docs completion checks and managed governance PASS;
7 Docs regressions PASS; agent conformance 4 positive/15 adversarial PASS;
publisher conformance 1 positive/14 adversarial PASS. Initial invocation mistakes
(missing --all, then missing DOCS_SOURCE) were corrected; no code bypass.
User approved Wellman owner handoff through its controller; this grants no
authority to invent the missing local ticket-002 identity or waive its gate.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.

## Publication continuation 2026-10-03

SESSION_EXECUTION_AUTHORIZATION: the user explicitly requested pushing and merging the remaining unpublished projects. This extends the earlier local-only delivery to protected publication of this existing bounded ticket. The earlier lease is cancelled; a new plan-bound fenced lease owns this continuation. Runtime changes and rollout claims remain excluded.
