from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Evidence:
    source: str
    evidence_type: str
    description: str
    strength: float


@dataclass
class Finding:

    finding_id: str
    vulnerability_type: str
    severity: str
    file: str
    line: int

    evidence: List[Evidence] = field(default_factory=list)

    def add_evidence(
        self,
        source,
        evidence_type,
        description,
        strength
    ):

        self.evidence.append(
            Evidence(
                source=source,
                evidence_type=evidence_type,
                description=description,
                strength=strength
            )
        )

    def evidence_score(self):

        if not self.evidence:
            return 0.0

        total = sum(e.strength for e in self.evidence)

        # Cap at 1.0
        return min(total, 1.0)

    def to_dict(self) -> Dict[str, Any]:

        return {
            "finding_id": self.finding_id,
            "vulnerability_type": self.vulnerability_type,
            "severity": self.severity,
            "file": self.file,
            "line": self.line,
            "evidence": [
                {
                    "source": e.source,
                    "type": e.evidence_type,
                    "description": e.description,
                    "strength": e.strength
                }
                for e in self.evidence
            ],
            "evidence_score": self.evidence_score()
        }
