from agentshield.core.attack_path.blast_radius import (
    BlastRadiusCalculator,
)
from agentshield.core.attack_path.graph import ResourceGraph


def build_graph():
    graph = ResourceGraph()

    graph.add_resource("vpc")
    graph.add_resource("subnet")
    graph.add_resource("ec2")
    graph.add_resource("database")
    graph.add_resource("lambda")

    graph.add_relationship(
        "subnet",
        "vpc",
    )

    graph.add_relationship(
        "ec2",
        "subnet",
    )

    graph.add_relationship(
        "database",
        "ec2",
    )

    graph.add_relationship(
        "lambda",
        "ec2",
    )

    return graph


def test_reachable_resources():
    graph = build_graph()
    calculator = BlastRadiusCalculator(graph)

    affected = calculator.get_reachable_resources(
        "vpc"
    )

    assert affected == {
        "subnet",
        "ec2",
        "database",
        "lambda",
    }


def test_blast_radius_count():
    graph = build_graph()
    calculator = BlastRadiusCalculator(graph)

    assert (
        calculator.calculate_blast_radius("ec2")
        == 2
    )


def test_isolated_resource_has_zero_blast_radius():
    graph = build_graph()

    graph.add_resource("isolated")

    calculator = BlastRadiusCalculator(graph)

    assert (
        calculator.calculate_blast_radius("isolated")
        == 0
    )


def test_impact_score_is_normalized():
    graph = build_graph()
    calculator = BlastRadiusCalculator(graph)

    score = calculator.calculate_impact_score(
        "vpc"
    )

    assert 0.0 <= score <= 1.0