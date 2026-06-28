"""Schema helpers for repair-trajectory JSON files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional


class SchemaError(ValueError):
    """Raised when a trajectory file is missing required structure."""


@dataclass
class StaticFindings:
    before_count: Optional[int] = None
    after_count: Optional[int] = None
    before_types: List[str] = field(default_factory=list)
    after_types: List[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "StaticFindings":
        return cls(
            before_count=_optional_int(data.get("before_count")),
            after_count=_optional_int(data.get("after_count")),
            before_types=list(data.get("before_types", []) or []),
            after_types=list(data.get("after_types", []) or []),
        )


@dataclass
class ValidationEvidence:
    original_vulnerability_closed: Optional[bool] = None
    exploit_path_reachable_after: Optional[bool] = None
    functionality_preserved: Optional[bool] = None
    new_vulnerability_introduced: Optional[bool] = None
    related_new_vulnerability: Optional[bool] = None
    input_scope_narrowed: Optional[bool] = None
    notes: str = ""

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ValidationEvidence":
        return cls(
            original_vulnerability_closed=_optional_bool(data.get("original_vulnerability_closed")),
            exploit_path_reachable_after=_optional_bool(data.get("exploit_path_reachable_after")),
            functionality_preserved=_optional_bool(data.get("functionality_preserved")),
            new_vulnerability_introduced=_optional_bool(data.get("new_vulnerability_introduced")),
            related_new_vulnerability=_optional_bool(data.get("related_new_vulnerability")),
            input_scope_narrowed=_optional_bool(data.get("input_scope_narrowed")),
            notes=str(data.get("notes", "") or ""),
        )


@dataclass
class ApparentCues:
    warning_disappeared: Optional[bool] = None
    defensive_syntax_added: Optional[bool] = None
    explicit_security_claim: Optional[bool] = None
    narrower_input_handling: Optional[bool] = None
    user_facing_assurance: Optional[bool] = None
    other: List[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ApparentCues":
        return cls(
            warning_disappeared=_optional_bool(data.get("warning_disappeared")),
            defensive_syntax_added=_optional_bool(data.get("defensive_syntax_added")),
            explicit_security_claim=_optional_bool(data.get("explicit_security_claim")),
            narrower_input_handling=_optional_bool(data.get("narrower_input_handling")),
            user_facing_assurance=_optional_bool(data.get("user_facing_assurance")),
            other=list(data.get("other", []) or []),
        )


@dataclass
class RepairTrajectory:
    id: str
    prompt: str
    original_code: str
    repaired_code: str
    static_findings: StaticFindings = field(default_factory=StaticFindings)
    validation: ValidationEvidence = field(default_factory=ValidationEvidence)
    apparent_cues: ApparentCues = field(default_factory=ApparentCues)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "RepairTrajectory":
        for key in ("id", "original_code", "repaired_code"):
            if key not in data:
                raise SchemaError(f"missing required field: {key}")
        return cls(
            id=str(data["id"]),
            prompt=str(data.get("prompt", "") or ""),
            original_code=str(data["original_code"]),
            repaired_code=str(data["repaired_code"]),
            static_findings=StaticFindings.from_mapping(data.get("static_findings", {}) or {}),
            validation=ValidationEvidence.from_mapping(data.get("validation", {}) or {}),
            apparent_cues=ApparentCues.from_mapping(data.get("apparent_cues", {}) or {}),
            metadata=dict(data.get("metadata", {}) or {}),
        )


def _optional_bool(value: Any) -> Optional[bool]:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0"}:
            return False
    raise SchemaError(f"expected boolean or null, got {value!r}")


def _optional_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        raise SchemaError(f"expected integer or null, got {value!r}")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise SchemaError(f"expected integer or null, got {value!r}") from exc
