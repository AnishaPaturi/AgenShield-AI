from agentshield.core.attack_path.graph import ResourceGraph


def test_add_resource():
    graph = ResourceGraph()

    graph.add_resource(
        resource_id="aws.vpc.main",
        resource_type="aws_vpc",
        name="main",
    )

    assert "aws.vpc.main" in graph
    assert graph.get_resource(
        "aws.vpc.main"
    )["resource_type"] == "aws_vpc"


def test_add_relationship():
    graph = ResourceGraph()

    graph.add_resource("vpc")
    graph.add_resource("subnet")

    graph.add_relationship(
        source_id="subnet",
        target_id="vpc",
    )

    assert graph.get_dependencies("subnet") == ["vpc"]
    assert graph.get_dependents("vpc") == ["subnet"]


def test_public_cidr_is_detected():
    graph = ResourceGraph()

    graph.add_resource(
        resource_id="security_group",
        resource_type="aws_security_group",
        attributes={
            "ingress": [
                {
                    "cidr_blocks": [
                        "0.0.0.0/0"
                    ],
                }
            ]
        },
    )

    assert graph.is_internet_exposed(
        "security_group"
    ) is True


def test_internet_gateway_is_detected():
    graph = ResourceGraph()

    graph.add_resource(
        "igw",
        resource_type="aws_internet_gateway",
    )

    assert graph.is_internet_exposed(
        "igw"
    ) is True