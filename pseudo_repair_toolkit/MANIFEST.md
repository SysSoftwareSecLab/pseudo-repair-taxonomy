# Package Manifest

This archive contains a runnable prototype implementation for the Pseudo-Repair taxonomy.

## Included

- `src/pseudo_repair/`: Python package source code
- `examples/trajectories/`: synthetic example repair trajectories for True Repair, Pseudo-Repair subtypes, Vulnerability Mutation, and Regression
- `docs/`: taxonomy, annotation, validation, and input-schema notes
- `tests/`: unit tests for classifier and CLI
- `scripts/run_examples.sh`: script that validates examples and generates a batch Markdown report
- `reports/examples_batch_report.md`: generated sample report
- `README.md`: setup and usage instructions

## Verification Performed

- `python -m unittest discover -s tests`: passed
- `python -m compileall src tests`: passed
- editable installation and CLI smoke test: passed
