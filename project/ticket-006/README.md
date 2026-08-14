# Ticket 006: Bind autonomous publication to real work identity

- **ID**: ticket-006
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Created**: 2026-08-14

## Goal and scope

Distil the publication failure reproduced on `subactor/doctor-agent`: hosted
checks and an exact PR head were valid, but the independent Validator required
a `ticket-NNN` or `PLF-N` string although that repository has no compatible
ticket issuer. The standard must require a durable, real work identity without
allowing a controller to invent a syntactically valid token, borrow another
workstream's ticket or bypass independent validation.

Keep the closed agent v1 schema and grammar unchanged. Add guidance only for
controller/validator integration: configured identity schemes must be resolved
to an existing target-bound record, and repositories without a compatible
issuer/resolver remain fail-closed until policy supplies one.

## Acceptance criteria

- [x] AC-01: The user's request to continue autonomously and update extracted
  conclusions records `SESSION_EXECUTION_AUTHORIZATION` for this bounded slice.
- [x] AC-02: Publication binds repository, change, exact head and a durable real
  work identity issued before mutation or supplied by an authorized intake.
- [x] AC-03: Syntax-only identifiers, PR-number aliases, foreign tickets and
  post-hoc fabricated references are explicitly insufficient.
- [x] AC-04: Validators resolve configured identity schemes and verify target
  ownership plus an admissible lifecycle state; an unsupported repository is
  blocked rather than bypassed.
- [x] AC-05: Agent v1 schema/grammar remain unchanged and conformance,
  governance and diff hygiene pass.

## Validation evidence

- `python3 standard/conformance.py --all`: 4 positive variants; 15 adversarial
  cases rejected; schema and grammar digests unchanged.
- `./project/governance-check.sh`: `GOV-PASS`, 0 errors and 0 warnings.
- `git diff --check`: pass.
- Platform artifact build wrote nothing and confirmed that this external
  standard is not its managed artifact. Its independent check currently fails
  on pre-existing `platform/AGENTS.md` declared-version drift (614/615 valid);
  no Platform file was changed by this ticket.

## Evidence basis

- Doctor Agent PR #105 exact head
  `4f1156dad200a94447c28ceeda4b7fc46084c88b` passed hosted `test`, `validate`
  and `sync`; merge commit `a64d5330ee3f9f0135e39797a1685a6e18cb117d`
  has the identical Git tree.
- Validator run `31814901052` stopped before code validation solely because an
  empty ticket did not match its universal `ticket-NNN`/`PLF-N` regex.
- Doctor Agent has no new-project ticket allocator, active ticket directories,
  branch protection or ruleset that could supply that identifier. Inventing
  one would make the approval binding non-recomputable.

## Participants

- Human participant: unresolved; no user-* file was created by this script.
- Agent participant: [ai-codex.md](ai-codex.md)
