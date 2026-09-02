"""Security finding prioritization using severity, exposure and blast radius."""

from __future__ import annotations

from agentshield.core.attack_path.blast_radius import (
    BlastRadiusCalculator,
)
from agentshield.core.attack_path.graph import ResourceGraph
from agentshield.core.attack_path.path_analyzer import (
    AttackPathAnalyzer,
)
from agentshield.core.schemas.vulnerability import (
    Severity,
    VulnerabilityFinding,
)


class FindingPrioritizer:
    """Rank vulnerabilities using multiple infrastructure-risk signals."""

    SEVERITY_WEIGHTS: dict[Severity, float] = {
        Severity.CRITICAL: 1.00,
        Severity.HIGH: 0.75,
        Severity.MEDIUM: 0.50,
        Severity.LOW: 0.25,
        Severity.INFORMATIONAL: 0.10,
    }

    def __init__(self, graph: ResourceGraph) -> None:
        self.graph = graph
        self.path_analyzer = AttackPathAnalyzer(graph)
        self.blast_radius = BlastRadiusCalculator(graph)

    def calculate_priority_score(
        self,
        finding: VulnerabilityFinding,
    ) -> float:
        """Calculate a 0-100 priority score.

        Score composition:

            50% severity
            30% topological exposure
            20% blast radius
        """

        severity_score = self.SEVERITY_WEIGHTS.get(
            finding.severity,
            0.10,
        )

        exposure_score = (
            self.path_analyzer.calculate_topological_exposure(
                finding.affected_resource
            )
        )

        blast_score = (
            self.blast_radius.calculate_impact_score(
                finding.affected_resource
            )
        )

        confidence = finding.confidence_score

        raw_score = (
            (severity_score * 0.50)
            + (exposure_score * 0.30)
            + (blast_score * 0.20)
        )

        confidence_adjusted = (
            raw_score * (0.5 + (0.5 * confidence))
        )

        return round(
            confidence_adjusted * 100,
            2,
        )

    def assign_priority(
        self,
        score: float,
    ) -> str:
        """Convert numeric priority score to a priority level."""

        if score >= 85:
            return "CRITICAL"

        if score >= 70:
            return "HIGH"

        if score >= 40:
            return "MEDIUM"

        if score >= 20:
            return "LOW"

        return "INFORMATIONAL"

    def prioritize_finding(
        self,
        finding: VulnerabilityFinding,
    ) -> VulnerabilityFinding:
        """Calculate and attach Task 3.3 results to a finding."""

        paths = self.path_analyzer.find_attack_paths(
            finding.affected_resource
        )

        shortest_path = (
            self.path_analyzer.find_shortest_attack_path(
                finding.affected_resource
            )
        )

        blast_resources = sorted(
            self.blast_radius.get_reachable_resources(
                finding.affected_resource
            )
        )

        topological_exposure = (
            self.path_analyzer.calculate_topological_exposure(
                finding.affected_resource
            )
        )

        score = self.calculate_priority_score(finding)
        priority = self.assign_priority(score)

        finding.attack_path = shortest_path

        finding.raw_details.update(
            {
                "attack_paths": paths,
                "topological_exposure": topological_exposure,
                "blast_radius": len(blast_resources),
                "blast_radius_resources": blast_resources,
                "priority_score": score,
                "priority": priority,
            }
        )

        return finding

    def rank_findings(
        self,
        findings: list[VulnerabilityFinding],
    ) -> list[VulnerabilityFinding]:
        """Prioritize and sort findings from highest to lowest risk."""

        prioritized = [
            self.prioritize_finding(finding)
            for finding in findings
        ]

        return sorted(
            prioritized,
            key=lambda finding: (
                finding.raw_details.get(
                    "priority_score",
                    0.0,
                ),
                self.SEVERITY_WEIGHTS.get(
                    finding.severity,
                    0.10,
                ),
            ),
            reverse=True,
        )