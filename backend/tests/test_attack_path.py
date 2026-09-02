from agentshield.core.attack_path.graph import ResourceGraph
from agentshield.core.attack_path.path_analyzer import (
    AttackPathAnalyzer,
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

    graph.add_relationship(
        "database",
        "ec2",
    )

    graph.add_relationship(
        "ec2",
        "security_group",
    )

    graph.add_relationship(
        "security_group",
        "internet_gateway",
    )

    return graph


def test_find_attack_path():
    graph = build_graph()
    analyzer = AttackPathAnalyzer(graph)

    paths = analyzer.find_attack_paths(
        "database"
    )

    assert [
        "internet_gateway",
        "security_group",
        "ec2",
        "database",
    ] in paths


def test_find_shortest_attack_path():
    graph = build_graph()
    analyzer = AttackPathAnalyzer(graph)

    path = analyzer.find_shortest_attack_path(
        "database"
    )

    assert path == [
        "internet_gateway",
        "security_group",
        "ec2",
        "database",
    ]


def test_path_length():
    path = [
        "internet_gateway",
        "security_group",
        "ec2",
        "database",
    ]

    assert (
        AttackPathAnalyzer.calculate_path_length(path)
        == 3
    )


def test_unreachable_resource():
    graph = build_graph()

    graph.add_resource(
        "isolated_bucket",
        resource_type="aws_s3_bucket",
    )

    analyzer = AttackPathAnalyzer(graph)

    assert analyzer.find_attack_paths(
        "isolated_bucket"
    ) == []