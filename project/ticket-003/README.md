# Ticket 003: Codify autonomous credential-reference and evidence-window rules

- **ID**: ticket-003
- **Owner**: founder-session
- **Status**: DONE
- **Workflow state**: DONE
- **Created**: 2026-08-14

## Goal and scope

Refresh the standalone agent standard from the exact merged Subactor
credential-reference work and the reproduced intent-evidence window failure.
The standard must distinguish a metadata inventory, a grant-gated secret
resolver, a public runtime route, a connector and a controller-owned grant
lifecycle instead of treating any one implementation as end-to-end readiness.

The change also defines a non-circular bootstrap boundary for service
credentials and requires history-dependent gates to bind their tool revision,
base/head revisions, bounded evidence window and truncation state. It updates
guidance only; it does not change the agent JSON Schema, GBNF or document
variants and does not publish the missing Hub HTTP endpoint.

## Acceptance criteria

- [x] AC-01: The evidence basis records exact reviewed and merged revisions for
  Inventory, Hub, connector, Control grant lifecycle and the Core evidence
  window fix without making them runtime dependencies.
- [x] AC-02: The standard treats the exact-reference capability as incomplete
  until the metadata query, resolver, public route, connector selection proof,
  controller grant/revocation and Vault read-back are all present and exercised.
- [x] AC-03: Inventory remains metadata-only; secret-bearing configuration is
  resolved by Hub/password-manager/Vault under a live grant, while bootstrap
  credentials come from a separate protected root of trust and never the LLM.
- [x] AC-04: A history-dependent gate binds the extractor/tool revision,
  base/head, bounded window and truncation state and cannot report a semantic
  regression from evidence evicted only by an asymmetric default window.
- [x] AC-05: Conformance, governance, diff hygiene and Subactor artifact build
  and check pass for the two-file standard clarification.

## Authorization

The Founder's requests to continue autonomously, analyse the dirty checkouts,
push the work and update the extracted conclusions here create
`SESSION_EXECUTION_AUTHORIZATION` for this bounded ticket. It authorizes the
ticket branch, the two implementation files declared in intent, validation,
commits, branch push, a pull request and submission of its exact head to the
independent Validator. It does not authorize direct push to `main`, secret
access, a self-issued grant, destructive cleanup or bypassing trusted review.

## Evidence basis

- Inventory head `082e8fc954a0554458c4f08456e8e18009579d5d`, merged as
  `1c6cdf5a1acee02ae1e754c3d6f12ea72a65c1e2`, exposes a tenant-scoped exact
  `credential-ref://...` metadata query and passed PostgreSQL plus the complete
  Linux/macOS/Windows Python 3.11/3.13 matrix.
- Hub head `1183d80b1460f8f1ad339ce7e224e8db3c02f3f8`, merged as
  `485997c345ea1da19320eb5a384bbd8941a91d4f`, resolves one exact Inventory
  reference to one supported isolated Firefox login after the live grant
  check. Its accepted intent explicitly excludes a new HTTP or MCP endpoint.
- Connector head `ae7f8e80419afebf28f2b77c3627e3984c5a9cac`, merged as
  `f941dd9fdd8949d77b4808000caf05da09832dd6`, sends an exact selector only to
  `/v1/commands/harvest-reference` and requires the identical selector in the
  response. Because Hub does not yet publish that route, this proves the
  fail-closed boundary but not an operational end-to-end path.
- Control head `8dbbb1570bdb3abe6a2e458c3ec24b115327f398`, merged as
  `cb611df46bbb99b1dba8b1f608eb231ba0e28321`, issues a just-in-time grant and
  requests revocation on success and dispatch failure.
- Core head `bf041fc6a9d72cde6e7757d14dac8d5685639676`, merged as
  `16b259d4ca42c1b10888296e56c16fc3619fa943`, reproduces a false coverage
  regression with todo2code's ten-commit default and removes it by binding the
  maximum supported bounded window of 100 commits without weakening policy.
- Internal knowledge
  `knowledge://subactor/architecture.plesk-secret-intake-binding-gap/v3`
  confirms the earlier grant-gated password-manager/Vault cycle. The separate
  `architecture.plesk-profile-operator-ownership/v3` open-adapter note is older
  than the merged implementation above, while
  `architecture.autonomy-structural-gaps/v2` passed its review deadline on
  2026-08-13; neither is silently reused as current completion evidence.
- The Subactor artifact registry has no managed entry for this external
  standalone standard. Platform artifact build and check remain required after
  the text edits, without committing the user's dirty Platform checkout.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
