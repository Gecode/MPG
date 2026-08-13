from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validate import validate  # noqa: E402


class ContentModelValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sample = json.loads((ROOT / "sample-publication.json").read_text(encoding="utf-8"))

    def messages(self, document: dict) -> str:
        return "\n".join(validate(document))

    def test_representative_manifest_is_valid(self) -> None:
        self.assertEqual(validate(self.sample), [])

    def test_stable_ids_are_globally_unique(self) -> None:
        broken = copy.deepcopy(self.sample)
        broken["validation_profiles"][0]["id"] = broken["code_artifacts"][0]["id"]
        self.assertIn("duplicate stable ID", self.messages(broken))

    def test_projection_must_reference_a_declared_artifact(self) -> None:
        broken = copy.deepcopy(self.sample)
        broken["pages"][0]["blocks"][2]["artifact_id"] = "artifact.missing"
        self.assertIn("unknown artifact", self.messages(broken))

    def test_projection_and_fold_overrides_must_reference_declared_regions(self) -> None:
        broken = copy.deepcopy(self.sample)
        projection = broken["pages"][0]["blocks"][2]
        projection["fold_overrides"]["region.missing"] = "linked"
        self.assertIn("fold override names unknown region", self.messages(broken))

    def test_region_parent_graph_must_be_acyclic(self) -> None:
        broken = copy.deepcopy(self.sample)
        regions = broken["code_artifacts"][0]["regions"]
        regions[0]["parent_id"] = "posting"
        regions[1]["parent_id"] = "whole"
        self.assertIn("parent cycle", self.messages(broken))

    def test_test_harness_cannot_claim_help_as_a_test_run(self) -> None:
        broken = copy.deepcopy(self.sample)
        broken["validation_profiles"][0]["execute"]["arguments"] = ["-help"]
        self.assertIn("must run tests, not a help argument", self.messages(broken))

    def test_test_harness_must_assert_registered_test_count(self) -> None:
        broken = copy.deepcopy(self.sample)
        del broken["validation_profiles"][0]["expect"]["registered_tests_min"]
        self.assertIn("must assert registered_tests_min", self.messages(broken))

    def test_compile_only_profile_cannot_contain_runtime_claims(self) -> None:
        broken = copy.deepcopy(self.sample)
        broken["validation_profiles"][0]["mode"] = "compile-only"
        messages = self.messages(broken)
        self.assertIn("compile-only must not declare execute", messages)
        self.assertIn("compile-only must not declare runtime expectations", messages)


if __name__ == "__main__":
    unittest.main()
