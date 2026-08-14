#!/usr/bin/env python3
"""Dependency-free conformance checks for agent v1."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "agent.schema.json"
GRAMMAR_PATH = ROOT / "agent.v1.gbnf"
SCHEMA_DIGEST = "97406321f9b7b2388b78ebdbbf307ea6cf2628cf1e8684252f9c3f5b142800b6"
GRAMMAR_DIGEST = "72ca71087b5da77c006e3ad41588409af8bbe156711d6c6350e75549bd537286"
SCHEMA_URI = "https://wellmanifest.dev/schemas/agent/v1"
SENSITIVE = re.compile(
    r"(?:password|passwd|token|secret|cookie|api[-_]?key|card|cvv|private[-_]?key|"
    r"argv|shell|remote[-_]?url|force[-_]?push|auto[-_]?merge|merge[-_]?command)",
    re.I,
)
SAFE_ASSERTIONS = {"secretsRedacted", "credentialsStored", "storesCredentials", "executesUntrustedCode"}
LANE_FOR_KIND = {
    "doctor": "diagnose",
    "repair": "repair",
    "validator": "validate",
    "test": "observe",
    "skills": "orchestrate",
    "control": "orchestrate",
    "runtime": "execute",
    "vault": "lease",
}
MUTATION_FOR_KIND = {
    "doctor": "none",
    "repair": "pull-request",
    "validator": "none",
    "test": "none",
    "skills": "none",
    "control": "none",
    "runtime": "none",
    "vault": "none",
}
PRODUCT_ONLY_OPERATIONS = {"repair"}


class ContractError(ValueError):
    """A bounded error that never repeats untrusted secrets or commands."""


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def exact(value: Any, required: set[str], optional: set[str] | None = None) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError("expected object")
    optional = optional or set()
    if set(value) - required - optional:
        raise ContractError("undeclared field")
    if required - set(value):
        raise ContractError("missing field")
    return value


def time_value(value: Any) -> datetime:
    if not isinstance(value, str) or len(value) > 40:
        raise ContractError("invalid date-time")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ContractError("invalid date-time") from error
    if result.tzinfo is None:
        raise ContractError("timezone required")
    return result


def reject_sensitive(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if SENSITIVE.search(key) and key not in SAFE_ASSERTIONS:
                raise ContractError("sensitive data channel")
            reject_sensitive(child)
    elif isinstance(value, list):
        for child in value:
            reject_sensitive(child)


class Contracts:
    def __init__(self) -> None:
        self.schema = json.loads(SCHEMA_PATH.read_text("utf-8"))
        self.grammar = GRAMMAR_PATH.read_text("utf-8")
        defs = self.schema.get("$defs", {})
        names = (
            "identifier",
            "sha256",
            "agentRef",
            "runRef",
            "correlationRef",
            "targetRef",
            "skillRef",
            "identityRef",
            "leaseRef",
            "intentRef",
            "grantRef",
            "evidenceRef",
        )
        self.patterns = {name: re.compile(defs[name]["pattern"]) for name in names}

    def ref(self, name: str, value: Any) -> str:
        if not isinstance(value, str) or self.patterns[name].fullmatch(value) is None:
            raise ContractError(f"invalid {name}")
        return value

    def integrity(self) -> None:
        if self.schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema" or self.schema.get("$id") != SCHEMA_URI:
            raise ContractError("schema identity mismatch")
        if digest(canonical(self.schema)) != SCHEMA_DIGEST or digest(self.grammar) != GRAMMAR_DIGEST:
            raise ContractError("contract digest mismatch")
        if {x.get("$ref") for x in self.schema.get("oneOf", [])} != {
            "#/$defs/profile",
            "#/$defs/request",
            "#/$defs/run",
            "#/$defs/receipt",
        }:
            raise ContractError("document variants incomplete")
        for fragment in ("root ::= request", "merge commands", "agent-ref ::=", "correlation-ref ::=", "sha256 ::="):
            if fragment not in self.grammar:
                raise ContractError("grammar incomplete")
        self._closed(self.schema)

    def _closed(self, value: Any) -> None:
        if isinstance(value, dict):
            if value.get("type") == "object" and value.get("additionalProperties") is not False:
                raise ContractError("open object schema")
            for child in value.values():
                self._closed(child)
        elif isinstance(value, list):
            for child in value:
                self._closed(child)


def profile_example(kind: str = "doctor") -> dict[str, Any]:
    lane = LANE_FOR_KIND[kind]
    return {
        "$schema": SCHEMA_URI,
        "schema": "wellmanifest.agent-profile/v1",
        "profileId": f"profile-{kind}",
        "version": "1.0.0",
        "agentRef": f"agent://example.test/{kind}/v1",
        "kind": kind,
        "lane": lane,
        "mutation": MUTATION_FOR_KIND[kind],
        "isolation": "isolated-workspace" if kind != "control" else "host-scheduler",
        "identityRef": f"identity://example.test/{kind}",
        "llmAuthority": "advisory",
        "executesUntrustedCode": False,
        "storesCredentials": False,
        "maxClaimSeconds": 1800,
    }


def request_example() -> dict[str, Any]:
    return {
        "$schema": SCHEMA_URI,
        "schema": "wellmanifest.agent-request/v1",
        "requestId": "request-001",
        "operation": "diagnose",
        "agentRef": "agent://example.test/doctor/v1",
        "correlationRef": "correlation://example.test/corr-001",
        "targetRef": "target://example.test/product/subactor",
        "targetKind": "product",
        "intentRef": "intent://example.test/agent/request-001",
        "grantRef": "grant://example.test/agent/request-001/g1",
        "planHash": "a" * 64,
    }


def run_example() -> dict[str, Any]:
    return {
        "$schema": SCHEMA_URI,
        "schema": "wellmanifest.agent-run-state/v1",
        "runRef": "run://example.test/run-001",
        "agentRef": "agent://example.test/doctor/v1",
        "correlationRef": "correlation://example.test/corr-001",
        "targetRef": "target://example.test/product/subactor",
        "state": "diagnosing",
        "version": 2,
        "updatedAt": "2026-08-13T12:00:00Z",
        "identityRef": "identity://example.test/doctor",
        "claimedUntil": "2026-08-13T12:30:00Z",
    }


def receipt_example() -> dict[str, Any]:
    return {
        "$schema": SCHEMA_URI,
        "schema": "wellmanifest.agent-receipt/v1",
        "requestId": "request-001",
        "runRef": "run://example.test/run-001",
        "agentRef": "agent://example.test/doctor/v1",
        "correlationRef": "correlation://example.test/corr-001",
        "targetRef": "target://example.test/product/subactor",
        "inputHash": "c" * 64,
        "planHash": "a" * 64,
        "outcome": "diagnosed",
        "startedAt": "2026-08-13T11:50:00Z",
        "completedAt": "2026-08-13T12:00:00Z",
        "evidenceRefs": ["evidence://example.test/agent/diagnose-001/r1"],
        "secretsRedacted": True,
        "credentialsStored": False,
    }


def validate_profile(c: Contracts, value: Any) -> None:
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
    if value["storesCredentials"] is not False:
        raise ContractError("profile stores credentials")
    if not isinstance(value["maxClaimSeconds"], int) or not 60 <= value["maxClaimSeconds"] <= 7200:
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
        kind = profile["kind"]
        identity = profile["identityRef"]
        if identity in identities and identities[identity] != kind:
            if {identities[identity], kind} & {"repair", "validator"}:
                raise ContractError("repair and validator share identity")
            raise ContractError("distinct lanes share identity")
        identities[identity] = kind


def validate_request(c: Contracts, value: Any) -> None:
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
    if value["operation"] in {"repair", "validate"}:
        if "headSha" not in value or not re.fullmatch(r"[0-9a-f]{40}", str(value["headSha"])):
            raise ContractError("exact head SHA required")
    if value["operation"] == "lease":
        if "leaseRef" not in value:
            raise ContractError("lease request lacks lease")
        c.ref("leaseRef", value["leaseRef"])
    if "skillRef" in value:
        c.ref("skillRef", value["skillRef"])


def validate_run(c: Contracts, value: Any) -> None:
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
    if not isinstance(value["version"], int) or value["version"] < 1:
        raise ContractError("invalid version")
    time_value(value["updatedAt"])
    if value["state"] in {"claimed", "diagnosing", "repairing", "validating"}:
        if not isinstance(value["claimedUntil"], str):
            raise ContractError("active claim lacks deadline")
        if time_value(value["claimedUntil"]) <= time_value(value["updatedAt"]):
            raise ContractError("claim is not forward-bounded")
    if value["state"] in {"repairing", "validating"}:
        if "headSha" not in value or not re.fullmatch(r"[0-9a-f]{40}", str(value["headSha"])):
            raise ContractError("active mutation lacks exact SHA")
    if "headSha" in value and not re.fullmatch(r"[0-9a-f]{40}", str(value["headSha"])):
        raise ContractError("invalid head SHA")


def validate_receipt(c: Contracts, value: Any) -> None:
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
    if time_value(value["completedAt"]) < time_value(value["startedAt"]):
        raise ContractError("receipt chronology")
    if not value["evidenceRefs"]:
        raise ContractError("receipt lacks evidence")
    for ref in value["evidenceRefs"]:
        c.ref("evidenceRef", ref)
    if value["secretsRedacted"] is not True or value["credentialsStored"] is not False:
        raise ContractError("unsafe receipt")


def run_all() -> dict[str, Any]:
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
    cases = []
    bad = profile_example("doctor")
    bad["mutation"] = "pull-request"
    cases.append(("doctor-with-pr-mutation", lambda: validate_profile(c, bad)))
    bad = profile_example("validator")
    bad["identityRef"] = "identity://example.test/repair"
    pair = [profile_example("repair"), bad]
    cases.append(("validator-shares-repair-identity", lambda: validate_identity_separation(pair)))
    bad = profile_example("control")
    bad["isolation"] = "host-scheduler"
    bad["executesUntrustedCode"] = True
    cases.append(("scheduler-executes-untrusted", lambda: validate_profile(c, bad)))
    bad = profile_example("vault")
    bad["storesCredentials"] = True
    cases.append(("vault-stores-credentials", lambda: validate_profile(c, bad)))
    bad = profile_example("repair")
    bad["llmAuthority"] = "authoritative"
    cases.append(("llm-as-trust-root", lambda: validate_profile(c, bad)))
    bad = copy.deepcopy(request)
    bad["operation"] = "repair"
    cases.append(("repair-without-head-sha", lambda: validate_request(c, bad)))
    bad = copy.deepcopy(request)
    bad["operation"] = "repair"
    bad["targetRef"] = "target://example.test/control/diagit"
    bad["targetKind"] = "control-plane"
    bad["headSha"] = "b" * 40
    cases.append(("repair-control-plane", lambda: validate_request(c, bad)))
    bad = copy.deepcopy(request)
    bad["token"] = "redacted-canary"
    cases.append(("inline-token", lambda: validate_request(c, bad)))
    bad = copy.deepcopy(request)
    bad["mergeCommand"] = "gh pr merge"
    cases.append(("merge-command", lambda: validate_request(c, bad)))
    bad = copy.deepcopy(request)
    bad["operation"] = "lease"
    cases.append(("lease-without-ref", lambda: validate_request(c, bad)))
    bad = copy.deepcopy(run)
    bad["claimedUntil"] = None
    cases.append(("claim-without-deadline", lambda: validate_run(c, bad)))
    bad = copy.deepcopy(run)
    bad["state"] = "repairing"
    cases.append(("repairing-without-sha", lambda: validate_run(c, bad)))
    bad = copy.deepcopy(receipt)
    bad["credentialsStored"] = True
    cases.append(("credentials-in-receipt", lambda: validate_receipt(c, bad)))
    bad = copy.deepcopy(receipt)
    bad["api_key"] = "redacted"
    cases.append(("secret-field-receipt", lambda: validate_receipt(c, bad)))
    rejected = []
    for name, case in cases:
        try:
            case()
        except (ContractError, KeyError, TypeError):
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    if not args.all:
        parser.error("--all is required")
    print(json.dumps(run_all(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
