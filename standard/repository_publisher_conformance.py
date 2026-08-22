#!/usr/bin/env python3
"""Dependency-free conformance for the repository publisher companion role."""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "repository-publisher-agent.schema.json"
PROFILE_PATH = ROOT / "repository-publisher-agent.profile.json"
SCHEMA_URI = "https://wellmanifest.dev/schemas/repository-publisher-agent/v1"
ARTIFACTS = {
    "operationProfile": {
        "repository": "wellmanifest/skills",
        "revision": "54d71ad2ec04896a1591d14d22de54562bafd4a1",
        "path": "standard/repository-initial-ref.operation-profile.json",
        "sha256": "5c11ad50de8e5724dc056797573e1bee4176d9f531c3f38f79f04562c3127225",
    },
    "mutationContract": {
        "repository": "wellmanifest/git-lifecycle",
        "revision": "72ade3b6c7ad68f617a50871a1f7466e7a868ab9",
        "path": "standard/repository-initial-ref.schema.json",
        "sha256": "6fdba8c71765cb217219bd3f459258170f7f1eaf70bb60970c4d3ecc68f0d724",
    },
}
AGENT_REF = re.compile(r"^agent://[a-z0-9.-]+/repository-publisher-agent/v[1-9][0-9]*$")
IDENTITY_REF = re.compile(r"^identity://[a-z0-9.-]+/[A-Za-z0-9._:/-]+$")
SENSITIVE = re.compile(
    r"(?:https?://|bearer\s|-----BEGIN|\b(?:ba)?sh\s+-c\b|\bgit\s+(?:push|reset)\b|"
    r"\bcurl\s|\bwget\s|\$\(|`)",
    re.I,
)


class ContractError(ValueError):
    """A bounded validation error that never repeats untrusted input."""


def exact(value: Any, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ContractError("object shape mismatch")
    return value


def reject_sensitive(value: Any, *, allow_schema: bool = False) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            reject_sensitive(child, allow_schema=(key == "$schema" and child == SCHEMA_URI))
    elif isinstance(value, list):
        for child in value:
            reject_sensitive(child)
    elif isinstance(value, str) and not allow_schema and SENSITIVE.search(value):
        raise ContractError("profile contains executable, remote or sensitive text")


def validate_profile(value: Any) -> None:
    value = exact(value, {
        "$schema", "schema", "profileId", "version", "agentRef", "kind", "lane",
        "mutation", "identityRef", "operationProfile", "mutationContract",
        "remotePrecondition", "authority", "executionSafety", "completion",
        "maxClaimSeconds", "llmAuthority",
    })
    if value["$schema"] != SCHEMA_URI or value["schema"] != "wellmanifest.repository-publisher-agent/v1":
        raise ContractError("unsupported publisher profile")
    if value["profileId"] != "profile.repository.publisher.v1" or value["version"] != "1.0.0":
        raise ContractError("publisher profile identity mismatch")
    if not isinstance(value["agentRef"], str) or AGENT_REF.fullmatch(value["agentRef"]) is None:
        raise ContractError("invalid publisher agent ref")
    if not isinstance(value["identityRef"], str) or IDENTITY_REF.fullmatch(value["identityRef"]) is None:
        raise ContractError("invalid publisher identity ref")
    if (value["kind"], value["lane"], value["mutation"]) != (
        "repository-publisher", "publish-initial-ref", "initial-ref-publish"
    ):
        raise ContractError("publisher lane mismatch")
    for field, expected in ARTIFACTS.items():
        artifact = exact(value[field], {"repository", "revision", "path", "sha256"})
        if artifact != expected:
            raise ContractError("immutable contract pin mismatch")
    if value["remotePrecondition"] != "empty-no-refs":
        raise ContractError("remote is not an unborn subject")

    authority = exact(value["authority"], {
        "mode", "requiredBindings", "singleUse", "inheritedAuthority", "whenMissing"
    })
    required = {
        "planDigest", "repositoryRef", "targetBranchRef", "sourceCommitSha",
        "sourceTreeDigest", "allowlistDigest",
    }
    bindings = authority["requiredBindings"]
    if not isinstance(bindings, list) or len(bindings) != len(set(bindings)) or set(bindings) != required:
        raise ContractError("publisher authority bindings mismatch")
    if authority != {
        "mode": "digest-bound",
        "requiredBindings": bindings,
        "singleUse": True,
        "inheritedAuthority": False,
        "whenMissing": "block",
    }:
        raise ContractError("publisher authority is not fresh and fail-closed")

    safety = exact(value["executionSafety"], {
        "isolation", "executesUntrustedCode", "storesCredentials", "forceAllowed"
    })
    if safety != {
        "isolation": "isolated-workspace",
        "executesUntrustedCode": False,
        "storesCredentials": False,
        "forceAllowed": False,
    }:
        raise ContractError("publisher execution safety mismatch")

    completion = exact(value["completion"], {
        "publicationState", "publicationTerminal", "validatorRole",
        "independentValidation", "terminalStates", "automaticRefDeletion",
    })
    if completion != {
        "publicationState": "initial-ref-published",
        "publicationTerminal": False,
        "validatorRole": "validator-agent",
        "independentValidation": True,
        "terminalStates": ["accepted", "quarantined"],
        "automaticRefDeletion": False,
    }:
        raise ContractError("publisher completion boundary mismatch")
    if not isinstance(value["maxClaimSeconds"], int) or not 60 <= value["maxClaimSeconds"] <= 1800:
        raise ContractError("publisher claim bound invalid")
    if value["llmAuthority"] != "advisory":
        raise ContractError("model gained publisher authority")
    reject_sensitive(value)


def schema_integrity() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    if schema.get("$id") != SCHEMA_URI or schema.get("additionalProperties") is not False:
        raise ContractError("schema identity or closure mismatch")

    def closed(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("type") == "object" and node.get("additionalProperties") is not False:
                raise ContractError("open object schema")
            for child in node.values():
                closed(child)
        elif isinstance(node, list):
            for child in node:
                closed(child)

    closed(schema)


def expect_rejected(callback: Callable[[], Any]) -> None:
    try:
        callback()
    except ContractError:
        return
    raise ContractError("adversarial publisher profile accepted")


def run_all() -> None:
    schema_integrity()
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    validate_profile(profile)
    mutations = [
        lambda item: item["operationProfile"].update(revision="main"),
        lambda item: item["mutationContract"].update(path="standard/git-lifecycle.lifecycle"),
        lambda item: item.update(remotePrecondition="existing-ref"),
        lambda item: item["authority"].update(inheritedAuthority=True),
        lambda item: item["authority"].update(singleUse=False),
        lambda item: item["authority"]["requiredBindings"].remove("sourceTreeDigest"),
        lambda item: item["executionSafety"].update(forceAllowed=True),
        lambda item: item["executionSafety"].update(storesCredentials=True),
        lambda item: item["executionSafety"].update(executesUntrustedCode=True),
        lambda item: item["completion"].update(publicationTerminal=True),
        lambda item: item["completion"].update(independentValidation=False),
        lambda item: item["completion"].update(automaticRefDeletion=True),
        lambda item: item.update(llmAuthority="approve"),
        lambda item: item.update(agentRef="agent://subactor/repair-agent/v1"),
    ]
    for mutate in mutations:
        candidate = copy.deepcopy(profile)
        mutate(candidate)
        expect_rejected(lambda candidate=candidate: validate_profile(candidate))
    print(f"PASS: 1 repository publisher profile, {len(mutations)} adversarial cases")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--file", type=Path)
    args = parser.parse_args()
    try:
        schema_integrity()
        if args.all:
            run_all()
        elif args.file:
            validate_profile(json.loads(args.file.read_text(encoding="utf-8")))
            print(f"PASS: {args.file}")
        else:
            parser.error("choose --all or --file")
    except (ContractError, json.JSONDecodeError, OSError) as error:
        print(f"FAIL: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
