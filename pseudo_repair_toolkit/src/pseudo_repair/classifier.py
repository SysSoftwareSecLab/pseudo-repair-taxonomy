"""Operational classifier for Pseudo-Repair annotation.

The classifier uses structured validation evidence when available and falls
back to conservative heuristics. It is intended for annotation support and
report generation, not as a definitive security oracle.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

from .schema import RepairTrajectory
from .taxonomy import OUTCOME_GUIDE, SUBTYPE_GUIDE, PseudoRepairSubtype, RepairOutcome


@dataclass
class ClassificationResult:
    trajectory_id: str
    outcome: RepairOutcome
    subtype: Optional[PseudoRepairSubtype]
    confidence: float
    apparent_remediation: bool
    reasons: List[str] = field(default_factory=list)
    validation_gaps: List[str] = field(default_factory=list)
    evidence: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "trajectory_id": self.trajectory_id,
            "outcome": self.outcome.value,
            "subtype": self.subtype.value if self.subtype else None,
            "confidence": round(self.confidence, 3),
            "apparent_remediation": self.apparent_remediation,
            "reasons": self.reasons,
            "validation_gaps": self.validation_gaps,
            "evidence": self.evidence,
        }


SECURITY_KEYWORDS = (
    "sanitize",
    "sanitized",
    "escape",
    "validate",
    "validation",
    "parameterized",
    "prepared",
    "allowlist",
    "whitelist",
    "safe",
    "security",
    "secure",
    "check",
    "guard",
)

DANGEROUS_PATTERNS = {
    "sql_concat": ["SELECT", "INSERT", "UPDATE", "DELETE", " + ", "f\"", "%"],
    "shell_exec": ["os.system", "subprocess", "shell=True", "exec(", "eval("],
    "unsafe_deserialization": ["pickle.loads", "yaml.load", "marshal.loads"],
    "hardcoded_secret": ["password=", "api_key=", "secret=", "token="],
}


def classify_trajectory(trajectory: RepairTrajectory) -> ClassificationResult:
    validation = trajectory.validation
    static = trajectory.static_findings

    apparent, apparent_reasons = detect_apparent_remediation(trajectory)
    gaps = collect_validation_gaps(trajectory)
    evidence = build_evidence(trajectory, apparent)
    reasons: List[str] = list(apparent_reasons)

    closed = validation.original_vulnerability_closed
    reachable = validation.exploit_path_reachable_after
    functionality = validation.functionality_preserved
    new_vuln = validation.new_vulnerability_introduced
    related_new = validation.related_new_vulnerability
    scope_narrowed = validation.input_scope_narrowed or trajectory.apparent_cues.narrower_input_handling

    # Direct high-confidence cases.
    if closed is True and functionality is True and not new_vuln:
        reasons.append("validation indicates the original vulnerability is closed and functionality is preserved")
        return ClassificationResult(
            trajectory.id,
            RepairOutcome.TRUE_REPAIR,
            None,
            confidence=0.95 if not gaps else 0.82,
            apparent_remediation=apparent,
            reasons=reasons,
            validation_gaps=gaps,
            evidence=evidence,
        )

    if functionality is False and not apparent:
        reasons.append("functional semantics are not preserved and no credible apparent remediation cue is present")
        return ClassificationResult(
            trajectory.id,
            RepairOutcome.REGRESSION,
            None,
            confidence=0.9,
            apparent_remediation=apparent,
            reasons=reasons,
            validation_gaps=gaps,
            evidence=evidence,
        )

    if functionality is False and apparent:
        reasons.append("artifact appears safer but functional behavior is not preserved")
        return ClassificationResult(
            trajectory.id,
            RepairOutcome.PSEUDO_REPAIR,
            PseudoRepairSubtype.PR_SR,
            confidence=0.88,
            apparent_remediation=apparent,
            reasons=reasons,
            validation_gaps=gaps,
            evidence=evidence,
        )

    # Original vulnerability remains or exploit is still reachable.
    original_remains = (closed is False) or (reachable is True)
    if original_remains and apparent:
        subtype = infer_pseudo_repair_subtype(trajectory, scope_narrowed=bool(scope_narrowed), related_new=bool(related_new or new_vuln))
        if subtype == PseudoRepairSubtype.PR_SS:
            reasons.append("warning or surface indicators improved while the original exploit path remains")
        elif subtype == PseudoRepairSubtype.PR_SN:
            reasons.append("input or trigger scope appears narrowed without evidence of causal closure")
        elif subtype == PseudoRepairSubtype.PR_VM:
            reasons.append("repair appears to suppress the original issue while a related new vulnerability appears")
        else:
            reasons.append("apparent remediation cues diverge from substantive vulnerability closure")
        return ClassificationResult(
            trajectory.id,
            RepairOutcome.PSEUDO_REPAIR,
            subtype,
            confidence=0.86 if not gaps else 0.72,
            apparent_remediation=apparent,
            reasons=reasons,
            validation_gaps=gaps,
            evidence=evidence,
        )

    # New vulnerability after apparent remediation can be PR-VM when the repair
    # appears to close or suppress the original issue but relocates risk.
    if new_vuln is True and apparent and related_new:
        reasons.append("repair appears to improve the original issue while introducing a closely related new vulnerability")
        return ClassificationResult(
            trajectory.id,
            RepairOutcome.PSEUDO_REPAIR,
            PseudoRepairSubtype.PR_VM,
            confidence=0.84 if not gaps else 0.7,
            apparent_remediation=apparent,
            reasons=reasons,
            validation_gaps=gaps,
            evidence=evidence,
        )

    # New vulnerability without apparent repair cue.
    if new_vuln is True:
        reasons.append("validation indicates a new vulnerability was introduced during repair")
        return ClassificationResult(
            trajectory.id,
            RepairOutcome.VULNERABILITY_MUTATION,
            None,
            confidence=0.82 if not gaps else 0.68,
            apparent_remediation=apparent,
            reasons=reasons,
            validation_gaps=gaps,
            evidence=evidence,
        )

    # Static evidence only: warning drop without closure evidence is review-worthy, not definitive.
    if warning_count_decreased(static) and closed is None:
        reasons.append("static warning count decreased but substantive closure evidence is missing")
        return ClassificationResult(
            trajectory.id,
            RepairOutcome.NEEDS_REVIEW,
            PseudoRepairSubtype.PR_SS,
            confidence=0.45,
            apparent_remediation=True,
            reasons=reasons,
            validation_gaps=gaps,
            evidence=evidence,
        )

    reasons.append("available evidence is incomplete or does not map cleanly to a top-level outcome")
    return ClassificationResult(
        trajectory.id,
        RepairOutcome.NEEDS_REVIEW,
        None,
        confidence=0.4,
        apparent_remediation=apparent,
        reasons=reasons,
        validation_gaps=gaps,
        evidence=evidence,
    )


def detect_apparent_remediation(trajectory: RepairTrajectory) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    cues = trajectory.apparent_cues
    static = trajectory.static_findings

    cue_values = {
        "warning_disappeared": cues.warning_disappeared,
        "defensive_syntax_added": cues.defensive_syntax_added,
        "explicit_security_claim": cues.explicit_security_claim,
        "narrower_input_handling": cues.narrower_input_handling,
        "user_facing_assurance": cues.user_facing_assurance,
    }
    for name, value in cue_values.items():
        if value is True:
            reasons.append(f"apparent remediation cue present: {name}")

    if warning_count_decreased(static):
        reasons.append("static warning count decreased after repair")

    added_security_terms = keyword_delta(trajectory.original_code, trajectory.repaired_code, SECURITY_KEYWORDS)
    if added_security_terms:
        reasons.append("security-looking terms or checks were added: " + ", ".join(sorted(added_security_terms)[:6]))

    if code_similarity(trajectory.original_code, trajectory.repaired_code) < 0.98:
        # Code changed, but this alone is not enough. It slightly supports appearance when combined with prompt intent.
        if any(word in trajectory.prompt.lower() for word in ("fix", "safe", "secure", "unsafe", "patch", "vulnerab")):
            reasons.append("repair-intent prompt and non-trivial code change are present")

    return bool(reasons), reasons


def infer_pseudo_repair_subtype(
    trajectory: RepairTrajectory,
    *,
    scope_narrowed: bool,
    related_new: bool,
) -> PseudoRepairSubtype:
    if trajectory.validation.functionality_preserved is False:
        return PseudoRepairSubtype.PR_SR
    if related_new:
        return PseudoRepairSubtype.PR_VM
    if scope_narrowed:
        return PseudoRepairSubtype.PR_SN
    if warning_count_decreased(trajectory.static_findings) or trajectory.apparent_cues.warning_disappeared:
        return PseudoRepairSubtype.PR_SS
    if keyword_delta(trajectory.original_code, trajectory.repaired_code, SECURITY_KEYWORDS):
        return PseudoRepairSubtype.PR_SS
    return PseudoRepairSubtype.UNKNOWN


def collect_validation_gaps(trajectory: RepairTrajectory) -> List[str]:
    v = trajectory.validation
    gaps = []
    if v.original_vulnerability_closed is None and v.exploit_path_reachable_after is None:
        gaps.append("missing substantive security-closure evidence")
    if v.functionality_preserved is None:
        gaps.append("missing functional regression evidence")
    if v.new_vulnerability_introduced is None:
        gaps.append("missing vulnerability-mutation evidence")
    return gaps


def build_evidence(trajectory: RepairTrajectory, apparent: bool) -> Dict[str, object]:
    return {
        "apparent_remediation_detected": apparent,
        "static_warning_before": trajectory.static_findings.before_count,
        "static_warning_after": trajectory.static_findings.after_count,
        "code_similarity": round(code_similarity(trajectory.original_code, trajectory.repaired_code), 3),
        "dangerous_patterns_original": detect_dangerous_patterns(trajectory.original_code),
        "dangerous_patterns_repaired": detect_dangerous_patterns(trajectory.repaired_code),
        "validation": {
            "original_vulnerability_closed": trajectory.validation.original_vulnerability_closed,
            "exploit_path_reachable_after": trajectory.validation.exploit_path_reachable_after,
            "functionality_preserved": trajectory.validation.functionality_preserved,
            "new_vulnerability_introduced": trajectory.validation.new_vulnerability_introduced,
            "related_new_vulnerability": trajectory.validation.related_new_vulnerability,
            "input_scope_narrowed": trajectory.validation.input_scope_narrowed,
        },
    }


def warning_count_decreased(static) -> bool:
    return static.before_count is not None and static.after_count is not None and static.after_count < static.before_count


def keyword_delta(before: str, after: str, keywords) -> List[str]:
    before_l = before.lower()
    after_l = after.lower()
    return [kw for kw in keywords if kw.lower() in after_l and kw.lower() not in before_l]


def code_similarity(before: str, after: str) -> float:
    return SequenceMatcher(None, before, after).ratio()


def detect_dangerous_patterns(code: str) -> List[str]:
    lower = code.lower()
    found = []
    for label, patterns in DANGEROUS_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in lower:
                found.append(label)
                break
    return sorted(set(found))


def explain_taxonomy(result: ClassificationResult) -> str:
    entry = OUTCOME_GUIDE[result.outcome]
    lines = [f"Outcome: {entry.name}", f"Definition: {entry.definition}"]
    if result.subtype:
        subtype_entry = SUBTYPE_GUIDE[result.subtype]
        lines.extend([f"Subtype: {subtype_entry.name}", f"Subtype definition: {subtype_entry.definition}"])
    return "\n".join(lines)
