import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "trajectories"


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "pseudo_repair.cli", *args],
            cwd=ROOT,
            env={"PYTHONPATH": str(ROOT / "src")},
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    def test_taxonomy(self):
        proc = self.run_cli("taxonomy")
        self.assertIn("Pseudo-Repair", proc.stdout)
        self.assertIn("PR-SS", proc.stdout)

    def test_classify_json(self):
        proc = self.run_cli("classify", str(EXAMPLES / "pr_scope_narrowing.json"), "--format", "json")
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["outcome"], "Pseudo-Repair")
        self.assertEqual(payload["subtype"], "PR-SN: Scope Narrowing")

    def test_batch_markdown(self):
        proc = self.run_cli("batch", str(EXAMPLES), "--format", "md")
        self.assertIn("Pseudo-Repair Batch Report", proc.stdout)
        self.assertIn("Total trajectories", proc.stdout)


if __name__ == "__main__":
    unittest.main()
