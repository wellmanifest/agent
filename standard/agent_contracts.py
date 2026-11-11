"""Shared contract constants, schema loader, primitives, and examples for agent v1."""

from __future__ import annotations

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
    re.IGNORECASE,
)
SENSITIVE_VALUE = re.compile(
    r"(?:bearer\s+[A-Za-z0-9._-]+|-----BEGIN\s+[A-Z ]*PRIVATE\s+KEY-----)", re.IGNORECASE
)
SAFE_ASSERTIONS = {
    "secretsRedacted",
    "credentialsStored",
    "storesCredentials",
    "executesUntrustedCode",
}
SEMVER_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?$")
HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
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
RECEIPT_OUTCOMES = {
    "denied",
    "claimed",
    "diagnosed",
    "repaired",
    "validated",
    "observed",
    "leased",
    "released",
    "failed",
}


class ContractError(ValueError):
    """A bounded error that never repeats untrusted secrets or commands."""


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def strict_json_loads(text: str) -> Any:
    def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, val in pairs:
            if key in result:
                raise ContractError("duplicate JSON key")
            result[key] = val
        return result

    try:
        return json.loads(text, object_pairs_hook=_reject_duplicates)
    except json.JSONDecodeError as error:
        raise ContractError("invalid JSON syntax") from error


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
        result = datetime.fromisoformat(value)
    except ValueError as error:
        raise ContractError("invalid date-time") from error
    if result.tzinfo is None:
        raise ContractError("timezone required")
    return result


def reject_sensitive(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if SENSITIVE.search(str(key)) and key not in SAFE_ASSERTIONS:
                raise ContractError("sensitive data channel")
            reject_sensitive(child)
    elif isinstance(value, list):
        for child in value:
            reject_sensitive(child)
    elif isinstance(value, str) and SENSITIVE_VALUE.search(value):
        raise ContractError("sensitive credential material")


class Contracts:
    def __init__(self) -> None:
        self.schema = strict_json_loads(SCHEMA_PATH.read_text("utf-8"))
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
        self.max_lengths = {
            name: defs[name]["maxLength"] for name in names if "maxLength" in defs[name]
        }

    def ref(self, name: str, value: Any) -> str:
        max_len = self.max_lengths.get(name)
        if (
            not isinstance(value, str)
            or (max_len is not None and len(value) > max_len)
            or self.patterns[name].fullmatch(value) is None
        ):
            raise ContractError(f"invalid {name}")
        return value

    def integrity(self) -> None:
        if (
            self.schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
            or self.schema.get("$id") != SCHEMA_URI
        ):
            raise ContractError("schema identity mismatch")
        if (
            digest(canonical(self.schema)) != SCHEMA_DIGEST
            or digest(self.grammar) != GRAMMAR_DIGEST
        ):
            raise ContractError("contract digest mismatch")
        if {x.get("$ref") for x in self.schema.get("oneOf", [])} != {
            "#/$defs/profile",
            "#/$defs/request",
            "#/$defs/run",
            "#/$defs/receipt",
        }:
            raise ContractError("document variants incomplete")
        required_fragments = (
            "root ::= request",
            "merge commands",
            "agent-ref ::=",
            "correlation-ref ::=",
            "sha256 ::=",
        )
        for fragment in required_fragments:
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
