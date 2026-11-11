"""Unit tests for wellmanifest/agent v1 conformance and repository publisher profiles."""

from __future__ import annotations

import copy
import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

STD_DIR = Path(__file__).resolve().parent
if str(STD_DIR) not in sys.path:
    sys.path.insert(0, str(STD_DIR))

conformance = importlib.import_module("conformance")
publisher = importlib.import_module("repository_publisher_conformance")


class AgentConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contracts = conformance.Contracts()
        cls.contracts.integrity()

    def test_all_standard_python_modules_stay_below_500_lines(self) -> None:
        for py_path in sorted(STD_DIR.glob("*.py")):
            line_count = len(py_path.read_text(encoding="utf-8").splitlines())
            self.assertLess(line_count, 500, f"{py_path.name} has {line_count} lines")

    def test_run_all_and_publisher_run_all_succeed(self) -> None:
        report = conformance.run_all()
        self.assertTrue(report["ok"])
        self.assertGreaterEqual(len(report["adversarialRejected"]), 21)
        publisher.run_all()

    def test_adversarial_cases_raise_distinct_targeted_errors(self) -> None:
        req = conformance.request_example()
        run = conformance.run_example()
        rcpt = conformance.receipt_example()
        messages: dict[str, str] = {}
        for name, callback in conformance._adversarial_cases(self.contracts, req, run, rcpt):
            with self.assertRaises(conformance.ContractError, msg=name) as ctx:
                callback()
            messages[name] = str(ctx.exception)
        self.assertEqual(messages["doctor-with-pr-mutation"], "kind and mutation disagree")
        self.assertEqual(messages["repair-without-head-sha"], "exact head SHA required")
        self.assertEqual(messages["repair-control-plane"], "repair cannot target control plane")
        self.assertEqual(messages["claim-without-deadline"], "active claim lacks deadline")
        self.assertEqual(messages["repairing-without-sha"], "active mutation lacks exact SHA")
        self.assertEqual(messages["credentials-in-receipt"], "unsafe receipt")

    def test_bool_as_int_and_non_bool_flags_are_rejected(self) -> None:
        bad_run = copy.deepcopy(conformance.run_example())
        bad_run["version"] = True
        with self.assertRaisesRegex(conformance.ContractError, "invalid version"):
            conformance.validate_run(self.contracts, bad_run)

        bad_profile = conformance.profile_example("doctor")
        bad_profile["executesUntrustedCode"] = "false"
        with self.assertRaisesRegex(conformance.ContractError, "boolean"):
            conformance.validate_profile(self.contracts, bad_profile)

        bad_profile_ver = conformance.profile_example("doctor")
        bad_profile_ver["version"] = "v1"
        with self.assertRaisesRegex(conformance.ContractError, "invalid profile version"):
            conformance.validate_profile(self.contracts, bad_profile_ver)

    def test_optional_fields_and_max_lengths_are_enforced(self) -> None:
        bad_req = conformance.request_example()
        bad_req["leaseRef"] = "bad-lease"
        with self.assertRaisesRegex(conformance.ContractError, "invalid leaseRef"):
            conformance.validate_request(self.contracts, bad_req)

        bad_req_id = conformance.request_example()
        bad_req_id["requestId"] = "a" * 97
        with self.assertRaisesRegex(conformance.ContractError, "invalid identifier"):
            conformance.validate_request(self.contracts, bad_req_id)

        released_run = conformance.run_example()
        released_run["state"] = "released"
        released_run["claimedUntil"] = "not-a-timestamp"
        with self.assertRaisesRegex(conformance.ContractError, "invalid date-time"):
            conformance.validate_run(self.contracts, released_run)

    def test_inline_bearer_values_duplicate_keys_and_symlinks_fail_closed(self) -> None:
        bad_req = conformance.request_example()
        bad_req["targetRef"] = "target://example.test/product/" + "Bea" + "rer_missing"
        conformance.validate_request(self.contracts, bad_req)

        bearer_doc = conformance.receipt_example()
        bearer_doc["outcome"] = "Bea" + "rer secret-value-canary"
        with self.assertRaisesRegex(conformance.ContractError, "sensitive credential material"):
            conformance.validate_receipt(self.contracts, bearer_doc)

        with self.assertRaisesRegex(conformance.ContractError, "duplicate JSON key"):
            conformance.strict_json_loads('{"a": 1, "a": 2}')

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            valid_file = tmp_dir / "request.json"
            valid_file.write_text(json.dumps(conformance.request_example()), encoding="utf-8")
            self.assertEqual(0, conformance.main(["--file", str(valid_file)]))

            symlink_file = tmp_dir / "linked.json"
            symlink_file.symlink_to(valid_file)
            self.assertEqual(1, conformance.main(["--file", str(symlink_file)]))
            self.assertEqual(1, publisher.main(["--file", str(symlink_file)]))


if __name__ == "__main__":
    unittest.main()
