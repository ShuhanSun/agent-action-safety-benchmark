from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Decision(str, Enum):
    ALLOW = "ALLOW"
    ASK = "ASK"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class BenchmarkCase:
    id: str
    scenario: str
    user_request: str
    source_trust: str
    action: dict[str, Any]
    permissions: list[str]
    data_classification: str
    reversibility: str
    expected_decision: Decision
    severity: int
    risk_tags: list[str]
    rationale: str
    # v0.2 metadata. These fields are useful for dataset analysis and split
    # validation but must never be exposed to a benchmarked model.
    family_id: str = ""
    category: str = ""
    split: str = ""
    variant_index: int = 0

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "BenchmarkCase":
        return cls(
            id=row["id"],
            scenario=row["scenario"],
            user_request=row["user_request"],
            source_trust=row["source_trust"],
            action=row["action"],
            permissions=list(row.get("permissions", [])),
            data_classification=row.get("data_classification", "public"),
            reversibility=row.get("reversibility", "reversible"),
            expected_decision=Decision(row["expected_decision"]),
            severity=int(row.get("severity", 0)),
            risk_tags=list(row.get("risk_tags", [])),
            rationale=row.get("rationale", ""),
            family_id=row.get("family_id", ""),
            category=row.get("category", ""),
            split=row.get("split", ""),
            variant_index=int(row.get("variant_index", 0)),
        )

    def model_input(self, condition: str = "full") -> dict[str, Any]:
        """Return only fields that are legitimate model inputs.

        Supported ablation conditions:
        - ``action``: proposed tool action only
        - ``intent``: action + user request
        - ``provenance``: action + request + source trust
        - ``full``: request + provenance + permissions + sensitivity + reversibility

        Annotation fields such as the expected label, family/split identifiers,
        severity, risk tags, and rationale are intentionally excluded.
        """
        if condition not in {"action", "intent", "provenance", "full"}:
            raise ValueError(f"unknown input condition: {condition}")

        payload: dict[str, Any] = {"action": self.action}
        if condition in {"intent", "provenance", "full"}:
            payload["user_request"] = self.user_request
        if condition in {"provenance", "full"}:
            payload["source_trust"] = self.source_trust
        if condition == "full":
            payload.update(
                permissions=self.permissions,
                data_classification=self.data_classification,
                reversibility=self.reversibility,
            )
        return payload
