# Agent logic flow

## Diagnose, repair and validate

```mermaid
stateDiagram-v2
    [*] --> Unclaimed
    Unclaimed --> Claimed: claim under exclusive TTL
    Claimed --> Diagnosing: diagnose
    Diagnosing --> Repairing: repair at exact head SHA
    Diagnosing --> Released: no repairable finding
    Repairing --> Validating: pull request opened
    Validating --> Released: independent validation accepted
    Validating --> Blocked: changes requested
    Blocked --> Repairing: resume same correlation
    Claimed --> Failed: claim expired or denied
    Diagnosing --> Failed: reproduction failed
    Repairing --> Failed: patch or tests failed
    Validating --> Failed: deterministic checks failed
    Unclaimed --> Observing: observe fleet health
    Observing --> Released: report written
```

`inspect` and `observe` never change product state. `lease` never starts a
repair. `orchestrate` may only sequence the declared lane; it cannot apply a
patch.

## Control plane versus product target

```mermaid
sequenceDiagram
    participant S as Skills or control
    participant D as Doctor
    participant Vlt as Vault
    participant R as Repair
    participant V as Validator
    S->>D: diagnose product target and correlation
    D-->>S: diagnosed receipt
    alt repairable
        S->>Vlt: lease for repair identity
        Vlt-->>R: opaque lease ref
        S->>R: repair exact head SHA
        R-->>S: repaired receipt with PR evidence
        S->>V: validate new exact head
        V-->>S: validated or blocked receipt
    else healthy
        S-->>S: release claim
    end
```

Repair and validator identities stay distinct. The scheduler that holds a
GitHub token does not execute the untrusted PR head; a networkless executor
without secrets may run tests.

## Failure routing

| Failure | Required state/outcome | Safe next action |
| --- | --- | --- |
| Doctor profile with `pull-request` mutation | `denied` | publish a diagnose-only profile |
| Repair and validator share `identityRef` | `denied` | split identities |
| Host scheduler executes untrusted code | `denied` | move execution to networkless executor |
| `repair` without `headSha` | `denied` | bind the exact checkout |
| Diagnose or repair a `control-plane` target | `denied` | keep agents off the product lane |
| Request contains a token or merge command | `denied` | use grant and git-lifecycle |
| Active claim without `claimedUntil` | `failed` | expire and re-claim |
| Repairing without SHA | `failed` | stop before apply |
| Receipt stores credentials | `failed` | redact and re-issue |

No failure path stores a lease secret or turns a transport-level success into
a merged product change.
