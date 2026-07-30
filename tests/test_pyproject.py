"""Tests for pyproject.toml configuration and package versioning."""

import tomllib
from pathlib import Path

import agentshield


def test_package_version():
    assert agentshield.__version__ == "0.1.0"


def test_pyproject_toml_structure():
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    assert pyproject_path.exists()

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    assert data["project"]["name"] == "agentshield-ai"
    assert data["project"]["version"] == "0.1.0"
    assert "pydantic>=2.7.0" in data["project"]["dependencies"]
    assert "python-hcl2>=0.3.0" in data["project"]["dependencies"]
    assert "pyyaml>=6.0" in data["project"]["dependencies"]
    assert "pytest>=8.0.0" in data["project"]["optional-dependencies"]["dev"]
