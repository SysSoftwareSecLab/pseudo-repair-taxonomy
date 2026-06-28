# Draft Annotation Guide

This guide is intentionally conservative. The current repository does not claim to release final empirical data, a locked annotation manual, or a benchmark-scale validation suite.

## Annotation Unit

The basic unit is a repair trajectory:

1. user prompt or repair instruction;
2. original generated code;
3. repaired code;
4. static findings before/after;
5. functional evidence;
6. security evidence;
7. apparent remediation cues;
8. final outcome and optional subtype.

## Recommended Annotation Steps

1. Record the repair intent.
2. Identify visible remediation cues, such as warning disappearance, more defensive syntax, or explicit claims of safety.
3. Check whether the original vulnerability is substantively closed.
4. Check whether relevant functionality is preserved.
5. Check whether a new vulnerability was introduced.
6. Assign one top-level class.
7. If the top-level class is Pseudo-Repair, assign one mechanism-level subtype.
8. Record missing evidence instead of forcing a label.

## Minimal Evidence Policy

- True Repair requires both security and functionality evidence.
- Pseudo-Repair requires both apparent remediation evidence and non-closure or regression evidence.
- Vulnerability Mutation requires evidence of a new vulnerability.
- Regression requires functional evidence.
- Needs Review should be used when evidence is insufficient.

## Suggested Fields

Use the JSON structure in `examples/trajectories/` as a starting point. The schema is intentionally simple so that future empirical releases can extend it without breaking compatibility.
