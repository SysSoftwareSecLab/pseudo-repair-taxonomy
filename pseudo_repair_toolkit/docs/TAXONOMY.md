# Taxonomy Summary

## What is Pseudo-Repair?

Pseudo-Repair describes apparent fixes produced during iterative LLM code refinement that create the impression of successful remediation without substantively closing the underlying security vulnerability or correctness problem.

## Top-Level Outcome Classes

| Outcome | Meaning | Core evidence |
|---|---|---|
| True Repair | Vulnerability substantively closed and functionality preserved | security oracle passes; functional oracle passes |
| Pseudo-Repair | Apparent fix, vulnerability remains or repair is only superficial | apparent remediation cue + substantive non-closure |
| Vulnerability Mutation | A meaningfully different vulnerability is introduced | new vulnerability evidence |
| Regression | Functionality broken during repair | functional oracle fails |

## Pseudo-Repair Subtypes

| Subtype | Name | Mechanism |
|---|---|---|
| PR-SS | Surface Suppression | Visible warning disappears but exploit path remains |
| PR-SN | Scope Narrowing | Trigger condition narrowed without causal fix |
| PR-VM | Vulnerability Migration | Original issue appears suppressed but a connected vulnerability appears elsewhere |
| PR-SR | Semantic Regression | Artifact appears safer but breaks intended functionality |

## Boundary Rules

- Pseudo-Repair is not every failed repair.
- It requires a credible appearance of remediation.
- Static-warning disappearance alone is not sufficient to prove True Repair.
- A dynamic or oracle-based check is preferred when making substantive closure claims.
- Regression without an apparent safety cue should be labeled top-level Regression, not PR-SR.
