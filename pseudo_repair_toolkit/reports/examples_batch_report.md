# Pseudo-Repair Batch Report

## Summary

Total trajectories: 7

### Outcome counts

- Pseudo-Repair: 4
- Regression: 1
- True Repair: 1
- Vulnerability Mutation: 1

### Subtype counts

- N/A: 3
- PR-SN: Scope Narrowing: 1
- PR-SR: Semantic Regression: 1
- PR-SS: Surface Suppression: 1
- PR-VM: Vulnerability Migration: 1

## Per-trajectory Results

### pr_scope_narrowing_demo
- Outcome: Pseudo-Repair
- Subtype: PR-SN: Scope Narrowing
- Confidence: 0.86
- Main reason: apparent remediation cue present: defensive_syntax_added

### pr_semantic_regression_demo
- Outcome: Pseudo-Repair
- Subtype: PR-SR: Semantic Regression
- Confidence: 0.88
- Main reason: apparent remediation cue present: warning_disappeared

### pr_surface_suppression_demo
- Outcome: Pseudo-Repair
- Subtype: PR-SS: Surface Suppression
- Confidence: 0.86
- Main reason: apparent remediation cue present: warning_disappeared

### pr_vulnerability_migration_demo
- Outcome: Pseudo-Repair
- Subtype: PR-VM: Vulnerability Migration
- Confidence: 0.84
- Main reason: apparent remediation cue present: warning_disappeared

### regression_demo
- Outcome: Regression
- Subtype: N/A
- Confidence: 0.90
- Main reason: functional semantics are not preserved and no credible apparent remediation cue is present

### true_repair_demo
- Outcome: True Repair
- Subtype: N/A
- Confidence: 0.95
- Main reason: apparent remediation cue present: warning_disappeared

### vulnerability_mutation_demo
- Outcome: Vulnerability Mutation
- Subtype: N/A
- Confidence: 0.68
- Main reason: validation indicates a new vulnerability was introduced during repair

## Repository Status

Empirical data, annotation guidelines, and conversation trajectories will be released upon paper acceptance. This prototype package includes a runnable taxonomy implementation, synthetic examples, and a draft schema only.
