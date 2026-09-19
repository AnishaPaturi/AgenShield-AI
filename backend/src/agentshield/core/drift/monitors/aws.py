"""AWS Cloud Monitor querying live AWS Config, EC2, S3, and RDS state (Task 5.2)."""

from __future__ import annotations

import logging
import os
from typing import Any

from agentshield.core.drift.monitors.base import BaseCloudMonitor
from agentshield.core.schemas import CloudProvider

logger = logging.getLogger("agentshield.drift.monitors.aws")


class AWSCloudMonitor(BaseCloudMonitor):
    """Monitors live AWS infrastructure configurations via AWS SDK / LocalStack."""

    def __init__(
        self,
        endpoint_url: str | None = None,
        region_name: str = "us-east-1",
    ) -> None:
        super().__init__(provider=CloudProvider.AWS)
        self.endpoint_url = endpoint_url or os.getenv("LOCALSTACK_ENDPOINT_URL")
        self.region_name = region_name

    def get_live_resource_state(
        self, resource_type: str, resource_name: str
    ) -> dict[str, Any] | None:
        resource_id = f"{resource_type}.{resource_name}"

        # 1. Check injected mock states first (for tests/offline simulation)
        if resource_id in self._mock_states:
            return self._mock_states[resource_id]

        # 2. Query Live AWS / LocalStack if boto3 available and configured
        try:
            import boto3

            session = boto3.Session(region_name=self.region_name)

            if resource_type in {"aws_s3_bucket", "AWS::S3::Bucket"}:
                s3_client = session.client("s3", endpoint_url=self.endpoint_url)
                try:
                    pab = s3_client.get_public_access_block(Bucket=resource_name)
                    config = pab.get("PublicAccessBlockConfiguration", {})
                    block_public_acls = config.get("BlockPublicAcls", False)
                except Exception:
                    block_public_acls = False

                return {
                    "bucket": resource_name,
                    "block_public_acls": block_public_acls,
                    "acl": "public-read" if not block_public_acls else "private",
                }

            elif resource_type in {"aws_security_group", "AWS::EC2::SecurityGroup"}:
                ec2_client = session.client("ec2", endpoint_url=self.endpoint_url)
                resp = ec2_client.describe_security_groups(
                    Filters=[{"Name": "group-name", "Values": [resource_name]}]
                )
                groups = resp.get("SecurityGroups", [])
                if not groups:
                    return None
                sg = groups[0]
                ingress_rules = []
                for perm in sg.get("IpPermissions", []):
                    from_port = perm.get("FromPort")
                    to_port = perm.get("ToPort")
                    protocol = perm.get("IpProtocol")
                    for ip_range in perm.get("IpRanges", []):
                        ingress_rules.append(
                            {
                                "from_port": from_port,
                                "to_port": to_port,
                                "protocol": protocol,
                                "cidr_blocks": [ip_range.get("CidrIp")],
                            }
                        )
                return {"name": resource_name, "ingress": ingress_rules}

            elif resource_type in {"aws_db_instance", "AWS::RDS::DBInstance"}:
                rds_client = session.client("rds", endpoint_url=self.endpoint_url)
                resp = rds_client.describe_db_instances(DBInstanceIdentifier=resource_name)
                dbs = resp.get("DBInstances", [])
                if not dbs:
                    return None
                db = dbs[0]
                return {
                    "identifier": resource_name,
                    "storage_encrypted": db.get("StorageEncrypted", False),
                    "publicly_accessible": db.get("PubliclyAccessible", False),
                }

        except Exception as exc:
            logger.debug("Live AWS monitor query exception for %s: %s", resource_id, exc)

        return None
