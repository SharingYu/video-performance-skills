"""Negative fixtures for release portability and accidental leaks."""

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_package.py"
SPEC = importlib.util.spec_from_file_location("package_checks", SCRIPT)
CHECKS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKS)


class PackageChecks(unittest.TestCase):
    def test_relative_link_survives_a_clean_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "reference.md").write_text("material", encoding="utf-8")
            self.assertEqual(CHECKS.link_errors(root / "SKILL.md", root, "[read](reference.md)"), [])

    def test_missing_and_outside_links_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            findings = CHECKS.link_errors(root / "SKILL.md", root, "[a](missing.md) [b](../outside.md)")
            self.assertTrue(any("missing local target" in item for item in findings))
            self.assertTrue(any("escapes package" in item for item in findings))

    def test_remote_and_anchor_links_are_not_fetched(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(CHECKS.link_errors(root / "README.md", root, "[a](https://example.org/a) [b](#local)"), [])

    def test_personal_path_and_token_are_flagged(self):
        personal_path = "C:" + "/Users/" + "Example/private.txt"
        token = "ghp_" + "x" * 30
        self.assertTrue(CHECKS.sensitive_findings(personal_path))
        self.assertTrue(CHECKS.sensitive_findings(token))
        self.assertEqual(CHECKS.sensitive_findings("skills/performance-direction/SKILL.md"), [])

    def test_oracle_cannot_silently_omit_a_case(self):
        cases = {"schema_version": 1, "cases": [{"id": "T1", "request": "review", "evidence": ["visible"], "candidate": "candidate", "synthetic_text": True}]}
        oracle = {"schema_version": 1, "expected": []}
        self.assertIn("case and oracle ids do not match", CHECKS.evaluation_errors(cases, oracle))

    def test_text_evidence_is_explicitly_labeled(self):
        cases = {"schema_version": 1, "cases": [{"id": "T1", "request": "review", "evidence": ["visible"], "candidate": "candidate"}]}
        oracle = {"schema_version": 1, "expected": [{"id": "T1", "decision": "supported"}]}
        self.assertTrue(any("synthetic_text" in item for item in CHECKS.evaluation_errors(cases, oracle)))


if __name__ == "__main__":
    unittest.main()
