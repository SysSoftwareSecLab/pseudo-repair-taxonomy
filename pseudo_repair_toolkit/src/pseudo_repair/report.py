"""Markdown and JSON report generation."""
from __future__ import annotations

from collections import Counter
from typing import Iterable, List

from .classifier import ClassificationResult, explain_taxonomy
from .taxonomy import REPOSITORY_STATUS


def results_to_json(results: Iterable[ClassificationResult]) -> List[dict]:
    return [item.to_dict() for item in results]


def result_to_markdown(result: ClassificationResult) -> str:
    lines = [
        f"# Pseudo-Repair Classification Report: {result.trajectory_id}",
        "",
        f"**Outcome:** {result.outcome.value}",
        f"**Subtype:** {result.subtype.value if result.subtype else 'N/A'}",
        f"**Confidence:** {result.confidence:.2f}",
        f"**Apparent remediation detected:** {result.apparent_remediation}",
        "",
        "## Taxonomy Explanation",
        "",
        explain_taxonomy(result),
        "",
        "## Reasons",
        "",
    ]
    lines.extend([f"- {reason}" for reason in result.reasons] or ["- No reason recorded."])
    lines.extend(["", "## Validation Gaps", ""])
    lines.extend([f"- {gap}" for gap in result.validation_gaps] or ["- None recorded."])
    lines.extend(["", "## Evidence Summary", "", "```json"])
    import json

    lines.append(json.dumps(result.evidence, indent=2, ensure_ascii=False))
    lines.extend(["```", "", "## Repository Status", "", REPOSITORY_STATUS, ""])
    return "\n".join(lines)


def batch_markdown(results: Iterable[ClassificationResult]) -> str:
    results = list(results)
    outcome_counts = Counter(item.outcome.value for item in results)
    subtype_counts = Counter(item.subtype.value if item.subtype else "N/A" for item in results)
    lines = [
        "# Pseudo-Repair Batch Report",
        "",
        "## Summary",
        "",
        f"Total trajectories: {len(results)}",
        "",
        "### Outcome counts",
        "",
    ]
    for key, value in sorted(outcome_counts.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "### Subtype counts", ""])
    for key, value in sorted(subtype_counts.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Per-trajectory Results", ""])
    for item in results:
        lines.extend([
            f"### {item.trajectory_id}",
            f"- Outcome: {item.outcome.value}",
            f"- Subtype: {item.subtype.value if item.subtype else 'N/A'}",
            f"- Confidence: {item.confidence:.2f}",
            f"- Main reason: {item.reasons[0] if item.reasons else 'N/A'}",
            "",
        ])
    lines.extend(["## Repository Status", "", REPOSITORY_STATUS, ""])
    return "\n".join(lines)
