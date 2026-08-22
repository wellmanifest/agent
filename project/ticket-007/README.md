# Ticket 007: Define one-time repository publisher agent

- **ID**: ticket-007
- **Owner**: agent:codex under SESSION_EXECUTION_AUTHORIZATION
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-22

## Goal and scope

Define a companion profile for a runtime-owned agent that may publish exactly
one first remote ref under the immutable git-lifecycle contract. Preserve the
closed `agent/v1` rule that Repair mutates only through pull requests; the new
role is a domain controller with a separate grant and independent Validator.

## Acceptance criteria

- [x] AC-01: A closed profile pins both the Skills operation profile and the
  git-lifecycle initial-ref contract by immutable artifact coordinates.
- [x] AC-02: The role accepts only `empty-no-refs`, a single-use non-inherited
  digest-bound grant, non-force publication and independent validation.
- [x] AC-03: Publication is non-terminal; accepted and quarantined are the only
  terminal states, and quarantine cannot delete the ref automatically.
- [x] AC-04: The standard rejects secret storage, untrusted-code execution,
  self-validation, commands, URLs and authority widening.
- [x] AC-05: `agent/v1` remains byte-for-byte unchanged.

## Participants

- Human participant: initiating conversation; no user-* file was created.
- Agent participant: [ai-codex.md](ai-codex.md)
