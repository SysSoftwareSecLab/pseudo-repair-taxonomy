#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src"
python -m pseudo_repair.cli taxonomy
python -m pseudo_repair.cli validate examples/trajectories
python -m pseudo_repair.cli batch examples/trajectories --format md --out reports/examples_batch_report.md
echo "Wrote reports/examples_batch_report.md"
