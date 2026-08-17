from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from gps.domain.contracts import (
    DispatchDecision,
    EvidenceIntent,
    EvidencePacket,
    RetrievalTrace,
    RoutingDecision,
    SourceSpan,
    ToolAction,
    ToolAuthorization,
    ToolDryRun,
    ToolReceipt,
)
from gps.domain.enums import (
    ActorType,
    DispatchMode,
    EvidenceCoverage,
    PassStatus,
    ReceiptStatus,
    RouteType,
    ToolActionStatus,
)

CTX = {"tenant_id": "mohid", "application_id": "mohid-support", "case_id": "case-1", "run_id": "run-1"}


def test_evidence_packet_preserves_evidence_per_intent_round_trip() -> None:
    span = SourceSpan(
        span_id="span-1",
        document_version_id="docv-1",
        chunk_id="chunk-1",
        heading_path=("Setup", "Prerequisites"),
        canonical_url="https://example.invalid/doc",
        quote="Synthetic approved evidence.",
    )
    packet = EvidencePacket(
        **CTX,
        packet_id="packet-1",
        corpus_version="corpus-1",
        intents=(
            EvidenceIntent(
                intent_id="intent-1",
                normalized_intent="setup mtap",
                coverage=EvidenceCoverage.SUFFICIENT,
                source_spans=(span,),
            ),
            EvidenceIntent(
                intent_id="intent-2",
                normalized_intent="unknown account operation",
                coverage=EvidenceCoverage.NONE,
                missing_requirements=("account identifier",),
            ),
        ),
        retrieval_trace=RetrievalTrace(
            queries=("setup mtap",),
            candidate_ids=("chunk-1",),
            ranking_version="ranking-1",
            embedding_version="embedding-1",
            latency_ms=1,
        ),
    )
    assert EvidencePacket.model_validate_json(packet.model_dump_json()) == packet
    assert packet.intents[1].source_spans == ()


def test_dispatch_binds_policy_verification_and_review_gate() -> None:
    decision = DispatchDecision(
        **CTX,
        decision_id="dispatch-1",
        outcome=DispatchMode.HUMAN_APPROVAL,
        reason_codes=("CATEGORY_REVIEW_ONLY",),
        policy_decision_id="policy-decision-1",
        policy_version="policy-1",
        verification_result_id="verification-1",
        reviewer_required=True,
    )
    assert DispatchDecision.model_validate_json(decision.model_dump_json()) == decision
    with pytest.raises(ValidationError):
        DispatchDecision.model_validate({**decision.model_dump(), "reviewer_required": False})
    payload = decision.model_dump()
    payload.pop("policy_version")
    with pytest.raises(ValidationError):
        DispatchDecision.model_validate(payload)


def test_evidence_packet_missing_intents_fails_closed() -> None:
    with pytest.raises(ValidationError):
        EvidencePacket.model_validate(
            {
                **CTX,
                "packet_id": "packet-1",
                "corpus_version": "corpus-1",
                "intents": [],
                "retrieval_trace": {
                    "queries": [],
                    "candidate_ids": [],
                    "ranking_version": "ranking-1",
                    "embedding_version": "embedding-1",
                    "latency_ms": 0,
                },
            }
        )


def test_routing_supports_configured_product_or_function_queue() -> None:
    route = RoutingDecision(
        **CTX,
        decision_id="route-1",
        route_type=RouteType.SPECIALIST,
        queue_id="queue-mtap-support",
        reason_codes=("ROUTE_SPECIALIST",),
        service_target="PT4H",
        policy_version="policy-1",
    )
    assert RoutingDecision.model_validate_json(route.model_dump_json()) == route
    with pytest.raises(ValidationError):
        RoutingDecision.model_validate({**route.model_dump(), "queue_id": None})


def test_tool_action_structured_gates_and_receipt_round_trip() -> None:
    action = ToolAction(
        **CTX,
        action_id="action-1",
        tool_type="send_approved_response",
        tool_version="1",
        typed_input={"message_id": "message-1"},
        authorization=ToolAuthorization(
            actor_type=ActorType.HUMAN,
            actor_ref="reviewer-1",
            capability="message.send",
            grant_id="grant-1",
        ),
        policy_decision_id="policy-decision-1",
        policy_version="policy-1",
        dry_run=ToolDryRun(status=PassStatus.PASSED, validated_at=datetime(2026, 1, 1, tzinfo=UTC)),
        idempotency_key="case-1:run-1:send:1",
        status=ToolActionStatus.SUCCEEDED,
        attempts=1,
        receipt=ToolReceipt(request_id="request-1", status=ReceiptStatus.DELIVERED),
    )
    assert ToolAction.model_validate_json(action.model_dump_json()) == action


@pytest.mark.parametrize("missing", ["authorization", "policy_version", "dry_run", "idempotency_key"])
def test_tool_action_missing_required_gate_fails_closed(missing: str) -> None:
    payload = {
        **CTX,
        "action_id": "action-1",
        "tool_type": "route_case",
        "tool_version": "1",
        "typed_input": {},
        "authorization": {"actor_type": "SYSTEM", "actor_ref": "runtime", "capability": "case.route", "grant_id": "g"},
        "policy_decision_id": "p",
        "policy_version": "policy-1",
        "dry_run": {"status": "PASSED", "validated_at": "2026-01-01T00:00:00Z"},
        "idempotency_key": "key",
        "status": "AUTHORIZED",
    }
    payload.pop(missing)
    with pytest.raises(ValidationError):
        ToolAction.model_validate(payload)


def test_tool_success_without_valid_receipt_fails_closed() -> None:
    with pytest.raises(ValidationError):
        ToolAction.model_validate(
            {
                **CTX,
                "action_id": "a",
                "tool_type": "send",
                "tool_version": "1",
                "typed_input": {},
                "authorization": {
                    "actor_type": "SYSTEM",
                    "actor_ref": "runtime",
                    "capability": "send",
                    "grant_id": "g",
                },
                "policy_decision_id": "p",
                "policy_version": "policy-1",
                "dry_run": {"status": "PASSED", "validated_at": "2026-01-01T00:00:00Z"},
                "idempotency_key": "key",
                "status": "SUCCEEDED",
                "receipt": {"request_id": "r", "status": "UNKNOWN"},
            }
        )
