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
        )
