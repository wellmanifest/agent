---
participant-id: agent:grok
participant: grok
role: agent
ticket: ticket-001
---
# Participant: grok (AI agent)

## Understanding

Subactor already runs several agent planes: doctor diagnoses, repair mutates
only through a PR, validator independently checks an exact SHA, skills
orchestrates the lane, test observes fleet health, onedev schedules isolated
workspaces, and credential-vault issues short leases. The missing module is a
closed DSL that declares those roles without embedding a GitHub org, a model
vendor or a secret.

## Execution plan

1. Adopt published `wellmanifest/new-project` and create one local seed
   baseline before any standard file exists.
2. Define closed profile, request, run-state and receipt variants.
3. Constrain requests with matching GBNF and reject secrets, shell, merge
   commands and wildcard targets.
4. Document composition with POA, ticket-lifecycle, git-lifecycle and
   saas-lifecycle.
5. Validate locally, through the governance gate and in networkless Docker.

## Actual changes

- Initialized the bounded ticket and recorded SESSION_EXECUTION_AUTHORIZATION
  from the request to create and publish this repository.
- Adopted published `wellmanifest/new-project` v0.16.0 at
  `6800f0138bc9063eb2dacb0a8b797dedcafb7952`.
- Created seed baseline `b8650be38afef7ac8d1f14d7076fae2157272772`.
- Added profile/request/run/receipt contracts, GBNF, conformance and
  composition docs.

## Blockers

- The initial-baseline blocker is resolved by the authorized local seed
  commit once HEAD exists.
- New authority remains required for destructive action, secret access,
  material objective expansion and trusted merge.

## Risks and controls

- A doctor profile can smuggle repair mutation; doctor mutation is `none`.
- A validator can share the repair identity; identities must differ.
- A scheduler can execute untrusted PR code with a token; token-bearing
  identities cannot execute untrusted code.
- Receipts can leak leases; `credentialsStored` is forced false.
