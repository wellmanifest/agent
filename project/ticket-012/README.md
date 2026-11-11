# Ticket 012: Modularize and harden agent conformance checks

- **ID**: ticket-012
- **Owner**: human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-11-11

## Goal and scope

Modularize `standard/conformance.py` strictly below 500 lines (`standard/agent_contracts.py`, `standard/conformance.py`, `standard/test_conformance.py`) and fix critical conformance validation defects:

1. Fix the late-binding `lambda` closure bug in `conformance.run_all()` where 14 adversarial test cases bound to the outer `bad` variable and only tested the final `receipt` mutation instead of their own mutations, and narrow exception catching from `(ContractError, KeyError, TypeError)` to `ContractError`.
2. Reject `bool` values for integer fields (`maxClaimSeconds`, `version`) and enforce boolean type on `executesUntrustedCode` and semver format on `profile.version`.
3. Validate optional `leaseRef` and `headSha` even when `operation` is not `lease`/`repair`/`validate`, validate `claimedUntil` on inactive run states when non-null, and enforce `receipt.outcome` enum plus `evidenceRefs` list type, cardinality (`1..64`), and uniqueness.
4. Enforce `maxLength` bounds from `agent.schema.json` `$defs`, reject duplicate JSON keys via `strict_json_loads`, scan string values for inline bearer/private-key material, and reject symlinked `--file` inputs.

## Acceptance criteria

- [x] AC-01: All `standard/*.py` files are strictly below 500 lines and pass `python3 standard/conformance.py --all` and `python3 standard/repository_publisher_conformance.py --all`.
- [x] AC-02: Unit tests in `standard/test_conformance.py` verify distinct `ContractError` messages per adversarial mutation, bool-as-int rejection, optional field validation, duplicate JSON keys, and symlink rejection.
- [x] AC-03: Passes `./project/governance-check.sh` and `wellman check`.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
