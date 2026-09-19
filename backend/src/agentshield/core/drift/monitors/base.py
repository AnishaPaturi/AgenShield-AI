"""Base Cloud Provider Monitor for Live Drift Detection (Task 5.2)."""

from abc import ABC, abstractmethod
from typing import Any

from agentshield.core.schemas import CloudProvider


class BaseCloudMonitor(ABC):
    """Abstract interface for querying live cloud provider infrastructure states."""

    def __init__(self, provider: CloudProvider) -> None:
        self.provider = provider
        self._mock_states: dict[str, dict[str, Any]] = {}

    def set_mock_resource_state(self, resource_id: str, state: dict[str, Any]) -> None:
        """Inject simulated live state for unit testing and offline environments."""
        self._mock_states[resource_id] = state

    @abstractmethod
    def get_live_resource_state(
        self, resource_type: str, resource_name: str
    ) -> dict[str, Any] | None:
        """Fetch actual live cloud configuration for a resource.

        Returns:
            dict containing live properties, or None if resource does not exist.
        """
        pass
