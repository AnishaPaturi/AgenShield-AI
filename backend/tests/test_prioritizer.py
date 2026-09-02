from agentshield.core.attack_path.graph import ResourceGraph
from agentshield.core.attack_path.prioritizer import (
    FindingPrioritizer,
)
from agentshield.core.schemas.vulnerability import (
    Severity,
    VulnerabilityFinding,
)


def build_graph():
    graph = ResourceGraph()

    graph.add_resource(
        "internet_gateway",
        resource_type="aws_internet_gateway",
    )

    graph.add_resource(
        "security_group",
        resource_type="aws_security_group",
    )

    graph.add_resource(
        "ec2",
        resource_type="aws_instance",
    )

    graph.add_resource(
        "database",
        resource_type="aws_db_instance",
    )

    graph.add_resource(
        "isolated_bucket",
        resource_type="aws_s3_bucket",
    )

    graph.add_relationship(
        "security_group",
        "internet_gateway",
    )

    graph.add_relationship(
        "ec2",
        "security_group",
    )

    graph.add_relationship(
        "database",
        "ec2",
    )

    return graph


def make_finding(
    finding_id: str,
    resource: str,
    severity: Severity,
) -> VulnerabilityFinding:
    return VulnerabilityFinding(
        finding_id=finding_id,
        rule_id="TEST-001",
        title="Test vulnerability",
        description="Test finding",
        severity=severity,
        confidence_score=1.0,
        affected_resource=resource,
        resource_type="test",
    )


def test_priority_score_is_in_range():
    graph = build_graph()
    prioritizer = FindingPrioritizer(graph)

    finding = make_finding(
        "finding-1",
        "database",
        Severity.CRITICAL,
    )

    score = prioritizer.calculate_priority_score(
        finding
    )

    assert 0.0 <= score <= 100.0


def test_critical_exposed_finding_gets_priority():
    graph = build_graph()
    prioritizer = FindingPrioritizer(graph)

    finding = make_finding(
        "finding-1",
        "database",
        Severity.CRITICAL,
    )

    result = prioritizer.prioritize_finding(
        finding
    )

    assert result.attack_path == [
        "internet_gateway",
        "security_group",
        "ec2",
        "database",
    ]

    assert (
        result.raw_details["topological_exposure"]
        > 0
    )

    assert (
        result.raw_details["blast_radius"]
        == 0
    )

    assert (
        0.0
        <= result.raw_details["priority_score"]
        <= 100.0
    )

    assert result.raw_details["priority"] in {
        "CRITICAL",
        "HIGH",
        "MEDIUM",
    }


def test_rank_findings():
    graph = build_graph()
    prioritizer = FindingPrioritizer(graph)

    critical = make_finding(
        "critical",
        "database",
        Severity.CRITICAL,
    )

    low = make_finding(
        "low",
        "isolated_bucket",
        Severity.LOW,
    )

    ranked = prioritizer.rank_findings(
        [low, critical]
    )

    assert ranked[0].finding_id == "critical"
    assert ranked[1].finding_id == "low"