import json
import unittest
from pathlib import Path

from pseudo_repair.classifier import classify_trajectory
from pseudo_repair.io import load_trajectory, load_trajectories
from pseudo_repair.taxonomy import PseudoRepairSubtype, RepairOutcome

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "trajectories"


class ClassifierTests(unittest.TestCase):
    def classify_example(self, name):
        return classify_trajectory(load_trajectory(EXAMPLES / name))

    def test_true_repair(self):
        result = self.classify_example("true_repair.json")
        self.assertEqual(result.outcome, RepairOutcome.TRUE_REPAIR)
        self.assertIsNone(result.subtype)

    def test_surface_suppression(self):
        result = self.classify_example("pr_surface_suppression.json")
        self.assertEqual(result.outcome, RepairOutcome.PSEUDO_REPAIR)
        self.assertEqual(result.subtype, PseudoRepairSubtype.PR_SS)

    def test_scope_narrowing(self):
        result = self.classify_example("pr_scope_narrowing.json")
        self.assertEqual(result.outcome, RepairOutcome.PSEUDO_REPAIR)
        self.assertEqual(result.subtype, PseudoRepairSubtype.PR_SN)

    def test_vulnerability_migration(self):
        result = self.classify_example("pr_vulnerability_migration.json")
        self.assertEqual(result.outcome, RepairOutcome.PSEUDO_REPAIR)
        self.assertEqual(result.subtype, PseudoRepairSubtype.PR_VM)

    def test_semantic_regression(self):
        result = self.classify_example("pr_semantic_regression.json")
        self.assertEqual(result.outcome, RepairOutcome.PSEUDO_REPAIR)
        self.assertEqual(result.subtype, PseudoRepairSubtype.PR_SR)

    def test_regression(self):
        result = self.classify_example("regression.json")
        self.assertEqual(result.outcome, RepairOutcome.REGRESSION)

    def test_vulnerability_mutation(self):
        result = self.classify_example("vulnerability_mutation.json")
        self.assertEqual(result.outcome, RepairOutcome.VULNERABILITY_MUTATION)

    def test_load_directory(self):
        trajectories = load_trajectories(EXAMPLES)
        self.assertGreaterEqual(len(trajectories), 6)


if __name__ == "__main__":
    unittest.main()
