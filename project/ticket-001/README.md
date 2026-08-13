# Ticket 001: Define standalone agent standard

- **ID**: ticket-001
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-13

## Goal and scope

Define a reusable agent standard from verified Subactor experience: doctor,
repair, validator, skills, test, onedev control and credential-vault. The
contract covers versioned agent profiles, isolated runs, mutation policy,
exclusive claims, credential leases and secret-free receipts. It is a
constraint language, not a fleet runtime.

A later `saas-lifecycle` or product system may bind `agentRef` values. This
module does not execute agents, store secrets or merge pull requests.

## Acceptance criteria

- [x] AC-01: The repository has an immutable published governance adoption and
  a real local seed baseline created before implementation.
- [x] AC-02: A closed Draft 2020-12 schema defines profile, request, run
  state and receipt variants.
- [x] AC-03: Request-only GBNF excludes secrets, shell, argv, remote URLs and
  merge commands.
- [x] AC-04: Documentation defines lanes, identity separation, lease
  boundaries, composition with POA/ticket/git lifecycles, and fail-closed
  behavior.
- [x] AC-05: Positive and adversarial conformance passes locally and in
  networkless, read-only Docker.
- [x] AC-06: Governance and diff hygiene pass against the exact baseline.

## Authorization

The request to create this repository as a governed DSL project creates
`SESSION_EXECUTION_AUTHORIZATION` and the narrow autonomous seed-baseline
authorization. It allows exactly one local governance-only baseline commit
while `HEAD` is unborn and implementation is absent. It does not authorize a
remote, push, PR, merge, tag or release.

The same request separately authorizes later public repository creation,
committing the bounded implementation, pushing its ticket branch and opening
a pull request. It does not authorize a direct push to `main`, merge, tag,
release creation or credential access.

## Baseline

The local seed transaction created
`b8650be38afef7ac8d1f14d7076fae2157272772`. Standard implementation begins
after this SHA and bounded delivery uses it as the exact accepted base.

## Participants

- Human participant: unresolved; no `user-*` file was created.
- Agent participant: [ai-grok.md](ai-grok.md)
