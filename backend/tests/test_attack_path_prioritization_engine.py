"""Comprehensive tests for Task 3.3: Attack-Path & Blast-Radius Prioritization Engine.

Tests:
- Resource topological graph construction (Internet Gateway -> Security Group -> Unencrypted DB)
- Exploitability route evaluation and path explanation
- Finding ranking based on combined severity, blast radius, and topological exposure
- Choke point identification and Mermaid diagram generation
"""

from agentshield.core.attack_path.blast_radius import BlastRadiusCalculator
from agentshield.core.attack_path.graph import ResourceGraph
from agentshield.core.attack_path.path_analyzer import AttackPathAnalyzer
from agentshield.core.attack_path.prioritizer import FindingPrioritizer
from agentshield.core.schemas.iac import ASTNode, IaCTemplate
from agentshield.core.schemas.vulnerability import Severity, VulnerabilityFinding


def test_topological_graph_igw_sg_unencrypted_db():
    """Verify topological graph evaluates exploitability routes:
    Internet Gateway -> Security Group -> Unencrypted DB
    """
    graph = ResourceGraph()

    graph.add_resource(
        "aws_internet_gateway.igw",
        resource_type="aws_internet_gateway",
        name="main-igw",
    )
    graph.add_resource(
        "aws_security_group.web_sg",
        resource_type="aws_security_group",
        name="web_sg",
        attributes={
            "ingress": [{"cidr_blocks": ["0.0.0.0/0"], "from_port": 80, "to_port": 80}]
        },
    )
    graph.add_resource(
        "aws_db_instance.unencrypted_db",
        resource_type="aws_db_instance",
        name="unencrypted-db",
        attributes={"storage_encrypted": False, "allocated_storage": 20},
    )

    # In IaC dependency orientation:
    # unencrypted_db depends on web_sg, web_sg depends on igw
    graph.add_relationship("aws_db_instance.unencrypted_db", "aws_security_group.web_sg")
    graph.add_relationship("aws_security_group.web_sg", "aws_internet_gateway.igw")

    analyzer = AttackPathAnalyzer(graph)
    paths = analyzer.find_attack_paths("aws_db_instance.unencrypted_db")

    assert len(paths) >= 1
    shortest = analyzer.find_shortest_attack_path("aws_db_instance.unencrypted_db")
    assert shortest == [
        "aws_internet_gateway.igw",
        "aws_security_group.web_sg",
        "aws_db_instance.unencrypted_db",
    ]

    # Verify route explanation
    eval_hops = analyzer.evaluate_route_exploitability(shortest)
    assert len(eval_hops) == 3
    assert "Internet Gateway" in eval_hops[0]["role"]
    assert "Security Group" in eval_hops[1]["role"]
    assert "Unencrypted" in eval_hops[2]["role"] or "Data Store" in eval_hops[2]["role"]


def test_auto_inference_from_template_ast():
    """Verify ResourceGraph.from_template automatically infers references and topology."""
    root = ASTNode(
        node_id="root",
        node_type="module",
        name="main",
        children=[
            ASTNode(
                node_id="aws_internet_gateway.igw",
                node_type="resource",
                resource_type="aws_internet_gateway",
                name="igw",
            ),
            ASTNode(
                node_id="aws_security_group.web_sg",
                node_type="resource",
                resource_type="aws_security_group",
                name="web_sg",
                attributes={
                    "ingress": [{"cidr_blocks": ["0.0.0.0/0"]}]
                },
            ),
            ASTNode(
                node_id="aws_db_instance.unencrypted_db",
                node_type="resource",
                resource_type="aws_db_instance",
                name="unencrypted_db",
                attributes={
                    "storage_encrypted": False,
                    "vpc_security_group_ids": ["${aws_security_group.web_sg.id}"],
                },
            ),
        ],
    )

    template = IaCTemplate(file_path="main.tf", raw_content="mock", parsed_ast=root)
    graph = ResourceGraph.from_template(template)

    assert "aws_internet_gateway.igw" in graph
    assert "aws_security_group.web_sg" in graph
    assert "aws_db_instance.unencrypted_db" in graph

    analyzer = AttackPathAnalyzer(graph)
    shortest = analyzer.find_shortest_attack_path("aws_db_instance.unencrypted_db")

    # Inferred topology: igw -> web_sg -> unencrypted_db
    assert shortest == [
        "aws_internet_gateway.igw",
        "aws_security_group.web_sg",
        "aws_db_instance.unencrypted_db",
    ]


def test_rank_findings_by_severity_blast_radius_and_exposure():
    """Verify findings ranking based on combined severity, blast radius, and topological exposure."""
    graph = ResourceGraph()

    # Internet Gateway -> Web SG -> Web App -> Internal Shared DB -> 5 Microservices
    graph.add_resource("aws_internet_gateway.igw", resource_type="aws_internet_gateway")
    graph.add_resource(
        "aws_security_group.web_sg",
        resource_type="aws_security_group",
        attributes={"ingress": [{"cidr_blocks": ["0.0.0.0/0"]}]},
    )
    graph.add_resource("aws_instance.web_app", resource_type="aws_instance")
    graph.add_resource(
        "aws_db_instance.unencrypted_db",
        resource_type="aws_db_instance",
        attributes={"storage_encrypted": False},
    )

    # 4 dependent services connected to database
    for i in range(1, 5):
        graph.add_resource(f"aws_lambda_function.service_{i}", resource_type="aws_lambda_function")
        graph.add_relationship(f"aws_lambda_function.service_{i}", "aws_db_instance.unencrypted_db")

    graph.add_relationship("aws_db_instance.unencrypted_db", "aws_instance.web_app")
    graph.add_relationship("aws_instance.web_app", "aws_security_group.web_sg")
    graph.add_relationship("aws_security_group.web_sg", "aws_internet_gateway.igw")

    # Isolated low risk resource
    graph.add_resource("aws_s3_bucket.isolated_logs", resource_type="aws_s3_bucket")

    prioritizer = FindingPrioritizer(graph)

    finding_critical_exposed = VulnerabilityFinding(
        finding_id="f-critical",
        rule_id="CKV_AWS_16",
        title="RDS Database is not encrypted at rest",
        description="Unencrypted database holding sensitive data is exposed through web tier.",
        severity=Severity.CRITICAL,
        confidence_score=0.95,
        affected_resource="aws_db_instance.unencrypted_db",
    )

    finding_medium_isolated = VulnerabilityFinding(
        finding_id="f-medium",
        rule_id="CKV_AWS_18",
        title="S3 Bucket access logging disabled",
        description="Bucket has no access logging.",
        severity=Severity.MEDIUM,
        confidence_score=0.90,
        affected_resource="aws_s3_bucket.isolated_logs",
    )

    # Rank findings
    ranked = prioritizer.rank_findings([finding_medium_isolated, finding_critical_exposed])

    assert ranked[0].finding_id == "f-critical"
    assert ranked[1].finding_id == "f-medium"

    crit_details = ranked[0].raw_details
    assert crit_details["priority_score"] > ranked[1].raw_details["priority_score"]
    assert crit_details["priority"] in {"CRITICAL", "HIGH", "MEDIUM"}
    assert crit_details["topological_exposure"] > 0.0
    assert crit_details["blast_radius"] == 4  # 4 lambda services depend on DB
    assert ranked[0].attack_path == [
        "aws_internet_gateway.igw",
        "aws_security_group.web_sg",
        "aws_instance.web_app",
        "aws_db_instance.unencrypted_db",
    ]


def test_choke_point_detection():
    """Verify that choke points are accurately identified when multiple attack paths converge."""
    graph = ResourceGraph()

    # Two distinct entry points: Public LB and Internet Gateway
    graph.add_resource("aws_lb.public_alb", resource_type="aws_lb")
    graph.add_resource("aws_internet_gateway.igw", resource_type="aws_internet_gateway")

    # Common choke point: web security group
    graph.add_resource(
        "aws_security_group.common_sg",
        resource_type="aws_security_group",
        attributes={"ingress": [{"cidr_blocks": ["0.0.0.0/0"]}]},
    )
    graph.add_resource("aws_instance.app_1", resource_type="aws_instance")
    graph.add_resource("aws_instance.app_2", resource_type="aws_instance")
    graph.add_resource("aws_db_instance.target_db", resource_type="aws_db_instance")

    # Both paths traverse through common_sg to reach target_db
    graph.add_relationship("aws_db_instance.target_db", "aws_instance.app_1")
    graph.add_relationship("aws_db_instance.target_db", "aws_instance.app_2")
    graph.add_relationship("aws_instance.app_1", "aws_security_group.common_sg")
    graph.add_relationship("aws_instance.app_2", "aws_security_group.common_sg")
    graph.add_relationship("aws_security_group.common_sg", "aws_internet_gateway.igw")
    graph.add_relationship("aws_security_group.common_sg", "aws_lb.public_alb")

    analyzer = AttackPathAnalyzer(graph)
    choke_points = analyzer.find_choke_points("aws_db_instance.target_db")

    assert len(choke_points) > 0
    top_choke = choke_points[0]
    assert top_choke["resource_id"] == "aws_security_group.common_sg"
    assert top_choke["paths_severed_if_remediated"] >= 2


def test_mermaid_graph_generation():
    """Verify Mermaid diagram generation for topology and attack paths."""
    graph = ResourceGraph()
    graph.add_resource("aws_internet_gateway.igw", resource_type="aws_internet_gateway")
    graph.add_resource("aws_security_group.sg", resource_type="aws_security_group")
    graph.add_resource("aws_db_instance.db", resource_type="aws_db_instance")

    graph.add_relationship("aws_db_instance.db", "aws_security_group.sg")
    graph.add_relationship("aws_security_group.sg", "aws_internet_gateway.igw")

    analyzer = AttackPathAnalyzer(graph)
    path = analyzer.find_shortest_attack_path("aws_db_instance.db")
    mermaid_diagram = analyzer.generate_mermaid_path(path)

    assert "graph LR" in mermaid_diagram
    assert "aws_internet_gateway_igw" in mermaid_diagram
    assert "aws_db_instance_db" in mermaid_diagram
