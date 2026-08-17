from datetime import UTC, datetime

import pytest

from gps.domain.contracts import RequestRun
from gps.domain.enums import RunStatus
from gps.providers.fakes import FakeCaseRepository


def _run(compatibility) -> RequestRun:
    return RequestRun(
        tenant_id="tenant-a",
        application_id="mohid-support",
        case_id="case-1",
        run_id="run-1",
        run_number=1,
        trigger="intake",
        environment="local",
        compatibility=compatibility,
        status=RunStatus.RECEIVED,
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_request_run_progresses_without_rewriting_attempt(compatibility) -> None:
    repository = FakeCaseRepository()
    received = _run(compatibility)
    repository.put_run(received)
    normalized = received.model_copy(update={"status": RunStatus.NORMALIZED})
    repository.put_run(normalized)
    assert repository.get_run("tenant-a", "mohid-support", "run-1") == normalized


@pytest.mark.parametrize("field,value", [("run_id", "run-2"), ("run_number", 2), ("case_id", "case-2")])
def test_request_run_identity_cannot_change(compatibility, field: str, value: object) -> None:
    repository = FakeCaseRepository()
    run = _run(compatibility)
    repository.put_run(run)
    with pytest.raises(ValueError, match="identity and configuration"):
        repository.put_run(run.model_copy(update={field: value}))


def test_request_run_compatibility_cannot_change(compatibility) -> None:
    repository = FakeCaseRepository()
    run = _run(compatibility)
    repository.put_run(run)
    changed = compatibility.model_copy(update={"policy_version": "policy-2"})
    with pytest.raises(ValueError, match="identity and configuration"):
        repository.put_run(run.model_copy(update={"compatibility": changed}))


def test_terminal_request_run_fails_closed(compatibility) -> None:
    repository = FakeCaseRepository()
    run = _run(compatibility).model_copy(update={"status": RunStatus.PROCESSING_FAILED})
    repository.put_run(run)
    with pytest.raises(ValueError, match="terminal"):
        repository.put_run(run.model_copy(update={"status": RunStatus.NORMALIZED}))


def test_repository_replaces_mutable_status_without_owning_workflow_policy(compatibility) -> None:
    repository = FakeCaseRepository()
    run = _run(compatibility)
    repository.put_run(run)
    dispatched = run.model_copy(update={"status": RunStatus.DISPATCHED})
    repository.put_run(dispatched)
    assert repository.get_run("tenant-a", "mohid-support", "run-1") == dispatched
