# Wellmanifest Agent

Experimental standard for declared software agents: roles, isolation,
mutation policy, credential leases and secret-free run receipts.

The normative artifacts live in `standard/`; architecture and lifecycle
guidance live in `docs/`. This repository never stores credentials, executes
untrusted pull-request code or grants merge authority.

It generalizes verified Subactor lanes (`doctor`, `repair`, `validator`,
`skills`, `test`, `onedev` control and `credential-vault`) so later
`saas-lifecycle` and product systems can bind an `agentRef` without absorbing
a specific fleet.
