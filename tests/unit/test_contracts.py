from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from gps.domain.contracts import CompatibilityTuple, RequestRun, ResolutionDecision, SupportCase
from gps.domain.enums import CaseState, ResolutionType, RunStatus


def test_support_case_schema_round_trip() -> None:
    case = SupportCase(
        tenant_id="tenant-a",
        application_id="mohid-support",
        case_id="case-1",
        channel="manual",
        requester_ref="requester-1",
        state=CaseState.RECEIVED,
        version=1,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        updated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    assert SupportCase.model_validate_json(case.model_dump_json()) == case


def test_request_run_and_compatibility_are_immutable(compatibility: CompatibilityTuple) -> None:
    run = RequestRun(
        tenant_id="tenant-a",
        application_id="mohid-support",
        case_id="case-1",
        run_id="run-1",
        run_number=1,
        trigger="manual",
        environment="local",
        compatibility=compatibility,
        status=RunStatus.RECEIVED,
    )
    with pytest.raises(ValidationError):
        run.status = RunStatus.NORMALIZED  # type: ignore[misc]
    with pytest.raises(ValidationError):
        run.compatibility.policy_version = "policy-2"  # type: ignore[misc]


@pytest.mark.parametrize("alias", ["latest", "current", "*"])
def test_compatibility_tuple_rejects_mutable_aliases(alias: str) -> None:
    with pytest.raises(ValidationError):
        CompatibilityTuple(
            runtime_version=alias,
            application_package_version="app-1",
            workflow_version="workflow-1",
            corpus_version="corpus-1",
            policy_version="policy-1",
            model_profile_version="model-1",
            adapter_versions=("fake-1",),
        )


def test_resolution_requires_evidence() -> None:
    with pytest.raises(ValidationError):
        ResolutionDecision(
            tenant_id="tenant-a",
            application_id="mohid-support",
            case_id="case-1",
            run_id="run-1",
            decision_id="decision-1",
            state=ResolutionType.RESOLVE,
            rationale_codes=("EVIDENCE_SUFFICIENT",),
        )
