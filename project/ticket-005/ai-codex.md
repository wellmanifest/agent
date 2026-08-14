---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-005
---
# Participant: codex (AI agent)

## Understanding

The dirty Intent/Contract DSL checkout exposed a reusable ambiguity: HOME is
the organization that owns and operates an artifact, while ADOPT names the
standards it follows. The rule already exists in the current
`wellmanifest/new-project` schema and instructions, but is absent from this
agent guidance. It belongs in architecture and lifecycle guidance, not in the
closed agent v1 document family.

## Execution plan

1. Bind the conclusion to the existing new-project closed vocabulary.
2. Add one normative placement invariant and one fail-closed routing rule.
3. Keep the JSON Schema, grammar and digest-pinned conformance runtime intact.
4. Run conformance, governance and diff checks before exact-head publication.

## Actual changes

- Initialized the bounded ticket and recorded SESSION_EXECUTION_AUTHORIZATION
  from the request to execute this work.
- Confirmed the closed HOME/SHAPE/runtimeOwner/ADOPT vocabulary in the current
  `wellmanifest/new-project` schema and instructions.
- Added the placement distinction to agent architecture, normative invariants,
  trust boundaries, lifecycle flow and fail-closed failure routing.
- Kept `standard/agent.schema.json`, `standard/agent.v1.gbnf` and their pinned
  conformance digests unchanged.
- Passed all conformance cases, deterministic governance and diff hygiene.

## Blockers

- None inside the recorded intent; proceed without a second confirmation.
- New authority remains required for destructive action, secret access, new
  external coordination, material objective expansion and trusted merge.

## Completion

- Confirmed trusted Validator approval and explicit merge of PR #8.
- Verified that the reviewed head and integrated merge have identical Git
  trees, then closed ticket-005 from integrated `main`.
