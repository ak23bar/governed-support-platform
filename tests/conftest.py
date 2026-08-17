from pathlib import Path

import pytest

from gps.domain.contracts import CompatibilityTuple


@pytest.fixture
def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def compatibility() -> CompatibilityTuple:
    return CompatibilityTuple(
        runtime_version="runtime-1",
        application_package_version="app-1",
        workflow_version="workflow-1",
        corpus_version="corpus-1",
        policy_version="policy-1",
        model_profile_version="model-1",
        adapter_versions=("fake-1",),
    )
