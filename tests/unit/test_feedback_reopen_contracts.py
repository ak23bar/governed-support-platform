from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from gps.domain.contracts import FeedbackEvent, ReopenEvent


def test_feedback_event_round_trips_and_is_immutable() -> None:
    feedback = FeedbackEvent(
        tenant_id="tenant-a",
        application_id="mohid-support",
        case_id="case-1",
        feedback_id="feedback-1",
        source="requester",
        rating=5,
        feedback_type="SATISFACTION",
        comment="The documented steps resolved the issue.",
        received_at=datetime(2026, 1, 2, tzinfo=UTC),
    )

    assert FeedbackEvent.model_validate_json(feedback.model_dump_json()) == feedback
    with pytest.raises(ValidationError):
        feedback.rating = 1  # type: ignore[misc]


def test_feedback_event_requires_a_rating_or_type() -> None:
    with pytest.raises(ValidationError, match="rating or feedback type"):
        FeedbackEvent(
            tenant_id="tenant-a",
            application_id="mohid-support",
            case_id="case-1",
            feedback_id="feedback-1",
            source="requester",
            comment="Follow-up feedback.",
            received_at=datetime(2026, 1, 2, tzinfo=UTC),
        )


def test_reopen_event_round_trips_and_is_immutable() -> None:
    reopened = ReopenEvent(
        tenant_id="tenant-a",
        application_id="mohid-support",
        case_id="case-1",
        reopen_id="reopen-1",
        prior_outcome_id="outcome-1",
        reason="Requester supplied new information after closure.",
        new_message_or_event_ref="message-2",
        reopened_at=datetime(2026, 1, 3, tzinfo=UTC),
        new_run_id="run-2",
    )

    assert ReopenEvent.model_validate_json(reopened.model_dump_json()) == reopened
    with pytest.raises(ValidationError):
        reopened.new_run_id = "run-3"  # type: ignore[misc]
