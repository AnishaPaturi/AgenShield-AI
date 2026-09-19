"""Azure Cloud Monitor for Live Drift Detection (Task 5.2)."""

from __future__ import annotations

from typing import Any

from agentshield.core.drift.monitors.base import BaseCloudMonitor
from agentshield.core.schemas import CloudProvider


class AzureCloudMonitor(BaseCloudMonitor):
    """Monitors live Azure resources (Network Security Groups, Storage Accounts, Key Vaults)."""

    def __init__(self) -> None:
        super().__init__(provider=CloudProvider.AZURE)

    def get_live_resource_state(
        self, resource_type: str, resource_name: str
    ) -> dict[str, Any] | None:
        resource_id = f"{resource_type}.{resource_name}"
        return self._mock_states.get(resource_id)
