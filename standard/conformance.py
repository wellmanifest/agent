#!/usr/bin/env python3
"""Dependency-free conformance checks for agent v1."""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any


def _load_contracts_module() -> Any:
    std_dir = str(Path(__file__).resolve().parent)
    if std_dir not in sys.path:
        sys.path.insert(0, std_dir)
    return importlib.import_module("agent_contracts")


_AC = _load_contracts_module()

ROOT: Path = _AC.ROOT
SCHEMA_PATH: Path = _AC.SCHEMA_PATH
GRAMMAR_PATH: Path = _AC.GRAMMAR_PATH
SCHEMA_DIGEST: str = _AC.SCHEMA_DIGEST
GRAMMAR_DIGEST: str = _AC.GRAMMAR_DIGEST
SCHEMA_URI: str = _AC.SCHEMA_URI
SENSITIVE = _AC.SENSITIVE
SAFE_ASSERTIONS: set[str] = _AC.SAFE_ASSERTIONS
LANE_FOR_KIND: dict[str, str] = _AC.LANE_FOR_KIND
MUTATION_FOR_KIND: dict[str, str] = _AC.MUTATION_FOR_KIND
PRODUCT_ONLY_OPERATIONS: set[str] = _AC.PRODUCT_ONLY_OPERATIONS
RECEIPT_OUTCOMES: set[str] = _AC.RECEIPT_OUTCOMES
ContractError = _AC.ContractError
Contracts = _AC.Contracts
canonical = _AC.canonical
digest = _AC.digest
exact = _AC.exact
is_int = _AC.is_int
profile_example = _AC.profile_example
receipt_example = _AC.receipt_example
reject_sensitive = _AC.reject_sensitive
request_example = _AC.request_example
run_example = _AC.run_example
strict_json_loads = _AC.strict_json_loads
time_value = _AC.time_value


def validate_profile(c: Any, value: Any) -> None:
    reject_sensitive(value)
    value = exact(
        value,
        {
            "$schema",
            "schema",
            "profileId",
            "version",
            "agentRef",
            "kind",
            "lane",
            "mutation",
            "isolation",
            "identityRef",
            "llmAuthority",
            "executesUntrustedCode",
            "storesCredentials",
            "maxClaimSeconds",
        },
        {"skillRef"},
    )
    if value["$schema"] != SCHEMA_URI or value["schema"] != "wellmanifest.agent-profile/v1":
        raise ContractError("unsupported profile")
    c.ref("identifier", value["profileId"])
    if not isinstance(value["version"], str) or _AC.SEMVER_RE.fullmatch(value["version"]) is None:
        raise ContractError("invalid profile version")
    c.ref("agentRef", value["agentRef"])
    c.ref("identityRef", value["identityRef"])
    if value["kind"] not in LANE_FOR_KIND:
        raise ContractError("invalid kind")
    if value["lane"] != LANE_FOR_KIND[value["kind"]]:
        raise ContractError("kind and lane disagree")
    if value["mutation"] != MUTATION_FOR_KIND[value["kind"]]:
        raise ContractError("kind and mutation disagree")
    if value["isolation"] not in {"isolated-workspace", "networkless-executor", "host-scheduler"}:
        raise ContractError("invalid isolation")
    if value["llmAuthority"] != "advisory":
        raise ContractError("llm is not advisory")
    if not isinstance(value["executesUntrustedCode"], bool):
        raise ContractError("executesUntrustedCode must be boolean")
    if value["storesCredentials"] is not False:
        raise ContractError("profile stores credentials")
    if not is_int(value["maxClaimSeconds"]) or not 60 <= value["maxClaimSeconds"] <= 7200:
        raise ContractError("invalid claim budget")
    if value["executesUntrustedCode"] is True and value["isolation"] != "networkless-executor":
        raise ContractError("untrusted execution outside networkless executor")
    if value["isolation"] == "host-scheduler" and value["executesUntrustedCode"] is not False:
        raise ContractError("token-bearing scheduler executes untrusted code")
    if value["kind"] == "skills" and "skillRef" not in value:
        raise ContractError("skills profile lacks skill")
    if "skillRef" in value:
        c.ref("skillRef", value["skillRef"])


def validate_identity_separation(profiles: list[dict[str, Any]]) -> None:
    identities: dict[str, str] = {}
    for profile in profiles:
        if not isinstance(profile, dict):
            raise ContractError("expected profile object")
        kind = profile.get("kind")
        identity = profile.get("identityRef")
        if not isinstance(kind, str) or not isinstance(identity, str):
            raise ContractError("invalid profile identity")
        if identity in identities and identities[identity] != kind:
            if {identities[identity], kind} & {"repair", "validator"}:
                raise ContractError("repair and validator share identity")
            raise ContractError("distinct lanes share identity")
        identities[identity] = kind


def validate_request(c: Any, value: Any) -> None:
    reject_sensitive(value)
    value = exact(
        value,
        {
            "$schema",
            "schema",
            "requestId",
            "operation",
            "agentRef",
            "correlationRef",
            "targetRef",
            "targetKind",
            "intentRef",
            "grantRef",
            "planHash",
        },
        {"headSha", "skillRef", "leaseRef"},
    )
    if value["$schema"] != SCHEMA_URI or value["schema"] != "wellmanifest.agent-request/v1":
        raise ContractError("unsupported request")
    c.ref("identifier", value["requestId"])
    if value["operation"] not in {
        "inspect",
        "claim",
        "diagnose",
        "repair",
        "validate",
        "observe",
        "orchestrate",
        "lease",
        "release",
    }:
        raise ContractError("unsupported operation")
    for name in ("agentRef", "correlationRef", "targetRef", "intentRef", "grantRef"):
        c.ref(name, value[name])
    c.ref("sha256", value["planHash"])
    if value["targetKind"] not in {"product", "control-plane"}:
        raise ContractError("invalid target kind")
    if value["operation"] in PRODUCT_ONLY_OPERATIONS and value["targetKind"] != "product":
        raise ContractError("repair cannot target control plane")
    if "headSha" in value and (
        not isinstance(value["headSha"], str) or _AC.HEX40_RE.fullmatch(value["headSha"]) is None
    ):
        raise ContractError("exact head SHA required")
    if value["operation"] in {"repair", "validate"} and "headSha" not in value:
        raise ContractError("exact head SHA required")
    if value["operation"] == "lease" and "leaseRef" not in value:
        raise ContractError("lease request lacks lease")
    if "leaseRef" in value:
        c.ref("leaseRef", value["leaseRef"])
    if "skillRef" in value:
        c.ref("skillRef", value["skillRef"])


def validate_run(c: Any, value: Any) -> None:
    reject_sensitive(value)
    value = exact(
        value,
        {
            "$schema",
            "schema",
            "runRef",
            "agentRef",
            "correlationRef",
            "targetRef",
            "state",
            "version",
            "updatedAt",
            "identityRef",
            "claimedUntil",
        },
        {"headSha"},
    )
    if value["$schema"] != SCHEMA_URI or value["schema"] != "wellmanifest.agent-run-state/v1":
        raise ContractError("unsupported run")
    for name in ("runRef", "agentRef", "correlationRef", "targetRef", "identityRef"):
        c.ref(name, value[name])
    if value["state"] not in {
        "unclaimed",
        "claimed",
        "diagnosing",
        "repairing",
        "validating",
        "observing",
        "blocked",
        "released",
        "failed",
    }:
        raise ContractError("invalid run state")
    if not is_int(value["version"]) or value["version"] < 1:
        raise ContractError("invalid version")
    updated_at = time_value(value["updatedAt"])
    claimed_until = value["claimedUntil"]
    if claimed_until is not None:
        parsed_until = time_value(claimed_until)
        if value["state"] in {"claimed", "diagnosing", "repairing", "validating"} and (
            parsed_until <= updated_at
        ):
            raise ContractError("claim is not forward-bounded")
    elif value["state"] in {"claimed", "diagnosing", "repairing", "validating"}:
        raise ContractError("active claim lacks deadline")
    if "headSha" in value and (
        not isinstance(value["headSha"], str) or _AC.HEX40_RE.fullmatch(value["headSha"]) is None
    ):
        raise ContractError("invalid head SHA")
    if value["state"] in {"repairing", "validating"} and "headSha" not in value:
        raise ContractError("active mutation lacks exact SHA")


def validate_receipt(c: Any, value: Any) -> None:
    reject_sensitive(value)
    value = exact(
        value,
        {
            "$schema",
            "schema",
            "requestId",
            "runRef",
            "agentRef",
            "correlationRef",
            "targetRef",
            "inputHash",
            "planHash",
            "outcome",
            "startedAt",
            "completedAt",
            "evidenceRefs",
            "secretsRedacted",
            "credentialsStored",
        },
    )
    if value["$schema"] != SCHEMA_URI or value["schema"] != "wellmanifest.agent-receipt/v1":
        raise ContractError("unsupported receipt")
    c.ref("identifier", value["requestId"])
    for name in ("runRef", "agentRef", "correlationRef", "targetRef"):
        c.ref(name, value[name])
    c.ref("sha256", value["inputHash"])
    c.ref("sha256", value["planHash"])
    if value["outcome"] not in RECEIPT_OUTCOMES:
        raise ContractError("invalid receipt outcome")
    if time_value(value["completedAt"]) < time_value(value["startedAt"]):
        raise ContractError("receipt chronology")
    evidence = value["evidenceRefs"]
    if not isinstance(evidence, list) or not 1 <= len(evidence) <= 64:
        raise ContractError("receipt lacks bounded evidence list")
    seen_refs: set[str] = set()
    for ref in evidence:
        c.ref("evidenceRef", ref)
        if ref in seen_refs:
            raise ContractError("duplicate evidence ref")
        seen_refs.add(ref)
    if value["secretsRedacted"] is not True or value["credentialsStored"] is not False:
        raise ContractError("unsafe receipt")


def validate_any(c: Any, value: Any) -> None:
    if not isinstance(value, dict):
        raise ContractError("expected object")
    kind = value.get("schema")
    dispatch = {
        "wellmanifest.agent-profile/v1": validate_profile,
        "wellmanifest.agent-request/v1": validate_request,
        "wellmanifest.agent-run-state/v1": validate_run,
        "wellmanifest.agent-receipt/v1": validate_receipt,
    }
    validator = dispatch.get(str(kind))
    if validator is None:
        raise ContractError("unsupported agent schema")
    validator(c, value)


def _adversarial_cases(
    c: Any,
    request: dict[str, Any],
    run: dict[str, Any],
    receipt: dict[str, Any],
) -> list[tuple[str, Callable[[], None]]]:
    cases: list[tuple[str, Callable[[], None]]] = []

    def add(name: str, fn: Callable[[Any, Any], None], payload: Any) -> None:
        cases.append((name, lambda fn=fn, payload=payload: fn(c, payload)))

    add(
        "doctor-with-pr-mutation",
        validate_profile,
        {**profile_example("doctor"), "mutation": "pull-request"},
    )
    shared_pair = [
        profile_example("repair"),
        {**profile_example("validator"), "identityRef": "identity://example.test/repair"},
    ]
    cases.append(
        (
            "validator-shares-repair-identity",
            lambda pair=shared_pair: validate_identity_separation(pair),
        )
    )
    add(
        "scheduler-executes-untrusted",
        validate_profile,
        {
            **profile_example("control"),
            "isolation": "host-scheduler",
            "executesUntrustedCode": True,
        },
    )
    add(
        "vault-stores-credentials",
        validate_profile,
        {**profile_example("vault"), "storesCredentials": True},
    )
    add(
        "llm-as-trust-root",
        validate_profile,
        {**profile_example("repair"), "llmAuthority": "authoritative"},
    )
    add(
        "repair-without-head-sha",
        validate_request,
        {**copy.deepcopy(request), "operation": "repair"},
    )
    add(
        "repair-control-plane",
        validate_request,
        {
            **copy.deepcopy(request),
            "operation": "repair",
            "targetRef": "target://example.test/control/diagit",
            "targetKind": "control-plane",
            "headSha": "b" * 40,
        },
    )
    add("inline-token", validate_request, {**copy.deepcopy(request), "token": "redacted-canary"})
    add(
        "bearer-grant-in-document",
        validate_request,
        {**copy.deepcopy(request), "grant_id": "runtime-grant-canary"},
    )
    add(
        "merge-command", validate_request, {**copy.deepcopy(request), "mergeCommand": "gh pr merge"}
    )
    add("lease-without-ref", validate_request, {**copy.deepcopy(request), "operation": "lease"})
    add("claim-without-deadline", validate_run, {**copy.deepcopy(run), "claimedUntil": None})
    add("repairing-without-sha", validate_run, {**copy.deepcopy(run), "state": "repairing"})
    add(
        "credentials-in-receipt",
        validate_receipt,
        {**copy.deepcopy(receipt), "credentialsStored": True},
    )
    add("secret-field-receipt", validate_receipt, {**copy.deepcopy(receipt), "api_key": "redacted"})
    add("version-bool-true", validate_run, {**copy.deepcopy(run), "version": True})
    add(
        "optional-invalid-lease-ref",
        validate_request,
        {**copy.deepcopy(request), "leaseRef": "not-a-lease-uri"},
    )
    add(
        "inactive-run-invalid-claimed-until",
        validate_run,
        {**copy.deepcopy(run), "state": "released", "claimedUntil": 12345},
    )
    add(
        "receipt-non-list-evidence",
        validate_receipt,
        {**copy.deepcopy(receipt), "evidenceRefs": 123},
    )
    add(
        "receipt-duplicate-evidence",
        validate_receipt,
        {
            **copy.deepcopy(receipt),
            "evidenceRefs": [
                "evidence://example.test/agent/diagnose-001/r1",
                "evidence://example.test/agent/diagnose-001/r1",
            ],
        },
    )
    add(
        "receipt-invalid-outcome",
        validate_receipt,
        {**copy.deepcopy(receipt), "outcome": "unknown"},
    )
    return cases


def run_all() -> dict[str, Any]:
    for py_path in sorted(ROOT.glob("*.py")):
        lines = len(py_path.read_text(encoding="utf-8").splitlines())
        if lines >= 500:
            raise ContractError(f"module exceeds 500 lines: {py_path.name}")
    c = Contracts()
    c.integrity()
    profiles = [profile_example(kind) for kind in LANE_FOR_KIND]
    profiles[4]["skillRef"] = "skill://example.test/org-audit/v1"
    for profile in profiles:
        validate_profile(c, profile)
    validate_identity_separation(profiles)
    request, run, receipt = request_example(), run_example(), receipt_example()
    validate_request(c, request)
    control_diagnosis = copy.deepcopy(request)
    control_diagnosis["targetRef"] = "target://example.test/control/diagit"
    control_diagnosis["targetKind"] = "control-plane"
    validate_request(c, control_diagnosis)
    control_validation = copy.deepcopy(control_diagnosis)
    control_validation["operation"] = "validate"
    control_validation["headSha"] = "b" * 40
    validate_request(c, control_validation)
    validate_run(c, run)
    validate_receipt(c, receipt)
    rejected = []
    for name, case in _adversarial_cases(c, request, run, receipt):
        try:
            case()
        except ContractError:
            rejected.append(name)
        else:
            raise AssertionError(f"adversarial case accepted: {name}")
    return {
        "schema": "wellmanifest.agent-conformance/v1",
        "ok": True,
        "schemaDigest": "sha256:" + SCHEMA_DIGEST,
        "grammarDigest": "sha256:" + GRAMMAR_DIGEST,
        "positiveVariants": 4,
        "adversarialRejected": rejected,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--file", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.all:
            print(json.dumps(run_all(), indent=2, sort_keys=True))
        elif args.file:
            if args.file.is_symlink():
                raise ContractError("symlinked input forbidden")
            c = Contracts()
            c.integrity()
            validate_any(c, strict_json_loads(args.file.read_text(encoding="utf-8")))
            print(f"PASS: {args.file}")
        else:
            parser.error("choose --all or --file")
    except (ContractError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
