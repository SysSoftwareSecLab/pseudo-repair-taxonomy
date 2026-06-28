"""Core taxonomy definitions for Pseudo-Repair analysis.

The implementation intentionally separates top-level repair outcomes from
mechanism-level Pseudo-Repair subtypes. It is a lightweight operationalization
of a taxonomy, not a benchmark or a replacement for expert validation.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class RepairOutcome(str, Enum):
    """Four top-level outcomes for iterative repair attempts."""

    TRUE_REPAIR = "True Repair"
    PSEUDO_REPAIR = "Pseudo-Repair"
    VULNERABILITY_MUTATION = "Vulnerability Mutation"
    REGRESSION = "Regression"
    NEEDS_REVIEW = "Needs Review"


class PseudoRepairSubtype(str, Enum):
    """Mechanism-level Pseudo-Repair subtypes."""

    PR_SS = "PR-SS: Surface Suppression"
    PR_SN = "PR-SN: Scope Narrowing"
    PR_VM = "PR-VM: Vulnerability Migration"
    PR_SR = "PR-SR: Semantic Regression"
    UNKNOWN = "Pseudo-Repair: subtype requires review"


@dataclass(frozen=True)
class TaxonomyEntry:
    code: str
    name: str
    definition: str
    positive_indicators: List[str]
    boundary_notes: List[str]


OUTCOME_GUIDE: Dict[RepairOutcome, TaxonomyEntry] = {
    RepairOutcome.TRUE_REPAIR: TaxonomyEntry(
        code="TR",
        name="True Repair",
        definition="The original vulnerability is substantively closed under the chosen validation stack and relevant functionality is preserved.",
        positive_indicators=[
            "original exploit path no longer works",
            "functional regression checks pass",
            "no closely related replacement vulnerability is introduced",
        ],
        boundary_notes=[
            "Static-warning disappearance alone is insufficient.",
            "A repair that breaks required behavior is not a true repair.",
        ],
    ),
    RepairOutcome.PSEUDO_REPAIR: TaxonomyEntry(
        code="PR",
        name="Pseudo-Repair",
        definition="The output presents credible signs of remediation while the original security or correctness problem is not substantively closed, is displaced, or is functionally regressed.",
        positive_indicators=[
            "warnings disappear but exploit path remains",
            "code looks more defensive but cause is not addressed",
            "a repair explanation claims safety without sufficient validation evidence",
        ],
        boundary_notes=[
            "Not every failed fix is Pseudo-Repair; there must be a plausible appearance of remediation.",
            "Pure non-action or unchanged vulnerable code without repair cues is outside scope.",
        ],
    ),
    RepairOutcome.VULNERABILITY_MUTATION: TaxonomyEntry(
        code="VM",
        name="Vulnerability Mutation",
        definition="The repair operation introduces a new vulnerability meaningfully different from the original one.",
        positive_indicators=[
            "new vulnerable sink or unsafe API appears",
            "original issue is replaced by a different security failure",
            "security status changes but not toward substantive safety",
        ],
        boundary_notes=[
            "This can coexist with apparent closure; if the appearance of repair is central, use PR-VM as a subtype.",
        ],
    ),
    RepairOutcome.REGRESSION: TaxonomyEntry(
        code="RG",
        name="Regression",
        definition="Functional semantics are broken during the repair process.",
        positive_indicators=[
            "unit tests fail after repair",
            "public API contract is changed unexpectedly",
            "required behavior is removed or distorted",
        ],
        boundary_notes=[
            "If the output also presents a plausible safety improvement, PR-SR may be the more informative subtype.",
        ],
    ),
    RepairOutcome.NEEDS_REVIEW: TaxonomyEntry(
        code="NR",
        name="Needs Review",
        definition="Available evidence is insufficient or conflicting.",
        positive_indicators=[
            "missing functional oracle",
            "missing security validation",
            "ambiguous or conflicting analyzer evidence",
        ],
        boundary_notes=[
            "Use this to avoid over-claiming when validation evidence is incomplete.",
        ],
    ),
}


SUBTYPE_GUIDE: Dict[PseudoRepairSubtype, TaxonomyEntry] = {
    PseudoRepairSubtype.PR_SS: TaxonomyEntry(
        code="PR-SS",
        name="Surface Suppression",
        definition="Visible warning signals disappear or defensive-looking syntax is added, but the exploit path remains open.",
        positive_indicators=[
            "static findings decrease while dynamic exploit still succeeds",
            "dangerous call is wrapped cosmetically",
            "warning text disappears without causal fix",
        ],
        boundary_notes=["Requires apparent warning/surface improvement plus evidence that the original issue remains."],
    ),
    PseudoRepairSubtype.PR_SN: TaxonomyEntry(
        code="PR-SN",
        name="Scope Narrowing",
        definition="The model narrows a triggering condition, input shape, or edge case without addressing the underlying cause.",
        positive_indicators=[
            "blocks only one payload pattern",
            "adds blacklist or length check while unsafe sink remains",
            "limits a special case but leaves general exploitability",
        ],
        boundary_notes=["Do not use for a complete input-domain validation redesign that actually closes the issue."],
    ),
    PseudoRepairSubtype.PR_VM: TaxonomyEntry(
        code="PR-VM",
        name="Pseudo-Repair via Vulnerability Migration",
        definition="The original issue appears suppressed while a closely connected vulnerability emerges elsewhere in the repair.",
        positive_indicators=[
            "moves user input from SQL injection into command injection",
            "replaces one unsafe deserialization path with another unsafe loader",
            "relocates the vulnerable sink to a helper function",
        ],
        boundary_notes=["If no apparent closure cue exists, classify as top-level Vulnerability Mutation instead."],
    ),
    PseudoRepairSubtype.PR_SR: TaxonomyEntry(
        code="PR-SR",
        name="Semantic Regression",
        definition="The artifact appears safer but breaks or distorts intended functionality in doing so.",
        positive_indicators=[
            "removes required feature to avoid vulnerability",
            "changes return contract while claiming security improvement",
            "passes a shallow safety check but fails functional oracle",
        ],
        boundary_notes=["Top-level Regression is for function-breaking repair without a credible apparent safety signal."],
    ),
    PseudoRepairSubtype.UNKNOWN: TaxonomyEntry(
        code="PR-UNK",
        name="Subtype requires review",
        definition="Pseudo-Repair is likely, but available structured evidence does not identify one mechanism subtype.",
        positive_indicators=["apparent remediation and substantive non-closure diverge"],
        boundary_notes=["Use a human adjudicator or add validation evidence."],
    ),
}


REPOSITORY_STATUS = (
    "Empirical data, annotation guidelines, and conversation trajectories will be released upon paper acceptance. "
    "This prototype package includes a runnable taxonomy implementation, synthetic examples, and a draft schema only."
)
