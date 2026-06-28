# Validation Guidance

The taxonomy distinguishes apparent remediation from substantive remediation. For this reason, static analysis is useful but insufficient on its own.

## Recommended Evidence Layers

1. **Static evidence**: analyzer warnings, dangerous patterns, changed sinks, dependency changes.
2. **Functional evidence**: unit tests, integration tests, API contract checks, expected output checks.
3. **Security evidence**: exploit oracle, dynamic test, semantic check, taint-flow evidence, manual adjudication for hard cases.
4. **Mutation evidence**: whether the repair introduces a different vulnerability.

## Interpreting Common Situations

- Warning disappears, exploit still works: PR-SS.
- Blacklist blocks one payload but variants still reach the sink: PR-SN.
- SQL injection disappears but command injection appears: PR-VM.
- Code rejects all input or removes required behavior while claiming safety: PR-SR.
- Functionality breaks and no safety appearance exists: Regression.
- Original exploit path is closed, functionality preserved, no new risk: True Repair.

## Warning

This toolkit does not execute untrusted code. Run dynamic tests only in a sandboxed environment designed for security evaluation.
