from collections.abc import Callable
from datetime import UTC, datetime

import pytest

from gps.domain.contracts import (
    AuditEvent,
    FinalOutcome,
    RequestRun,
    RoutingDecision,
    SupportCase,
    ToolAction,
    ToolAuthorization,
    ToolDryRun,
)
from gps.domain.enums import (
    CaseState,
    OutcomeDisposition,
    PassStatus,
    ReceiptStatus,
    RouteType,
    RunStatus,
    ToolActionStatus,
)
from gps.providers.fakes import (
    FakeCaseRepository,
    FakeEmbeddingProvider,
    FakeEventPublisher,
    FakeIdentityProvider,
    FakeInboundMessageProvider,
    FakeKnowledgeQueryProvider,
    FakeKnowledgeSourceProvider,
    FakeModelProvider,
    FakeObjectStore,
    FakeOutboundMessageProvider,
    FakeToolExecutor,
    FakeVectorStore,
)
from gps.providers.protocols import (
    AcquiredDocument,
    EmbeddingBatch,
    KnowledgeHit,
    ModelRequest,
    ObjectArtifact,
    OutboundEnvelope,
    ToolRequest,
    VectorDeleteRequest,
    VectorRecord,
    VectorSearchRequest,
)


# Approved adapters reuse the semantic test module by substituting provider, input,
# preparation, observation, and failure fixtures here.
@pytest.fixture
def model_provider():
    return FakeModelProvider()


@pytest.fixture
def model_request() -> ModelRequest:
    return ModelRequest(
        tenant_id="t",
        application_id="a",
        case_id="c",
        run_id="r",
        profile_version="p1",
        prompt="x",
        timeout_seconds=1,
    )


@pytest.fixture
def embedding_provider():
    return FakeEmbeddingProvider()


@pytest.fixture
def embedding_batch() -> EmbeddingBatch:
    return EmbeddingBatch(
        tenant_id="t",
        application_id="a",
        texts=("x", "y"),
        model_version="e1",
    )


@pytest.fixture
def vector_store():
    return FakeVectorStore()


@pytest.fixture
def vector_records() -> tuple[VectorRecord, ...]:
    common = {
        "vector": (1.0,),
        "metadata": {"kind": "procedure", "language": "en"},
    }
    return (
        VectorRecord(
            tenant_id="t1",
            application_id="a1",
            record_id="target",
            corpus_version="c1",
            document_id="d1",
            **common,
        ),
        VectorRecord(
            tenant_id="t2",
            application_id="a1",
            record_id="other-tenant",
            corpus_version="c1",
            document_id="d1",
            **common,
        ),
        VectorRecord(
            tenant_id="t1",
            application_id="a2",
            record_id="other-application",
            corpus_version="c1",
            document_id="d1",
            **common,
        ),
        VectorRecord(
            tenant_id="t1",
            application_id="a1",
            record_id="other-corpus",
            corpus_version="c2",
            document_id="d1",
            **common,
        ),
        VectorRecord(
            tenant_id="t1",
            application_id="a1",
            record_id="other-document",
            corpus_version="c1",
            document_id="d2",
            **common,
        ),
        VectorRecord(
            tenant_id="t1",
            application_id="a1",
            record_id="other-metadata",
            corpus_version="c1",
            document_id="d1",
            vector=(1.0,),
            metadata={"kind": "warning", "language": "en"},
        ),
    )


@pytest.fixture
def vector_search_request() -> VectorSearchRequest:
    return VectorSearchRequest(
        tenant_id="t1",
        application_id="a1",
        corpus_version="c1",
        document_id="d1",
        metadata_filters={"kind": "procedure"},
        query_vector=(1.0,),
        limit=10,
    )


@pytest.fixture
def vector_delete_request() -> VectorDeleteRequest:
    return VectorDeleteRequest(
        tenant_id="t1",
        application_id="a1",
        corpus_version="c1",
        document_id="d1",
        metadata_filters={"kind": "procedure"},
    )


@pytest.fixture
def object_store():
    return FakeObjectStore()


@pytest.fixture
def object_artifact() -> ObjectArtifact:
    return ObjectArtifact(
        tenant_id="t",
        application_id="a",
        key="raw/x",
        version="1",
        content=b"x",
        content_hash="2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881",
        retention="test",
    )


@pytest.fixture
def object_store_missing_error() -> type[BaseException]:
    return KeyError


@pytest.fixture
def case_repository():
    return FakeCaseRepository()


@pytest.fixture
def case_repository_missing_error() -> type[BaseException]:
    return KeyError


@pytest.fixture
def support_case() -> SupportCase:
    return SupportCase(
        tenant_id="t",
        application_id="a",
        case_id="c",
        channel="manual",
        requester_ref="synthetic",
        state=CaseState.RECEIVED,
        version=1,
    )


@pytest.fixture
def request_run(compatibility) -> RequestRun:
    return RequestRun(
        tenant_id="t",
        application_id="a",
        case_id="c",
        run_id="r",
        run_number=1,
        trigger="intake",
        environment="local",
        compatibility=compatibility,
        status=RunStatus.RECEIVED,
    )


@pytest.fixture
def case_decision() -> RoutingDecision:
    return RoutingDecision(
        tenant_id="t",
        application_id="a",
        case_id="c",
        run_id="r",
        decision_id="decision-1",
        route_type=RouteType.NONE,
        reason_codes=("NO_ROUTE_REQUIRED",),
        policy_version="policy-1",
    )


@pytest.fixture
def tool_action() -> ToolAction:
    return ToolAction(
        tenant_id="t",
        application_id="a",
        case_id="c",
        run_id="r",
        action_id="action-1",
        tool_type="synthetic",
        tool_version="tool-1",
        typed_input={},
        authorization=ToolAuthorization(
            actor_type="SYSTEM",
            actor_ref="runtime",
            capability="case.route",
            grant_id="grant-1",
        ),
        policy_decision_id="policy-decision-1",
        policy_version="policy-1",
        dry_run=ToolDryRun(status=PassStatus.PASSED, validated_at=datetime(2026, 1, 1, tzinfo=UTC)),
        idempotency_key="action-key-1",
        status=ToolActionStatus.PROPOSED,
    )


@pytest.fixture
def final_outcome() -> FinalOutcome:
    return FinalOutcome(
        tenant_id="t",
        application_id="a",
        case_id="c",
        run_id="r",
        outcome_id="outcome-1",
        disposition=OutcomeDisposition.NO_ACTION,
        dispatch_status=ReceiptStatus.ACCEPTED,
        close_reason="NO_ACTION_REQUIRED",
    )


@pytest.fixture
def knowledge_source_provider():
    return FakeKnowledgeSourceProvider()


@pytest.fixture
def prepare_knowledge_source(
    knowledge_source_provider: FakeKnowledgeSourceProvider,
) -> Callable[[AcquiredDocument], None]:
    """Keep provider-specific source setup outside the semantic assertions."""
    return knowledge_source_provider.add


@pytest.fixture
def knowledge_query_provider():
    return FakeKnowledgeQueryProvider()


@pytest.fixture
def prepare_knowledge_query(
    knowledge_query_provider: FakeKnowledgeQueryProvider,
) -> Callable[[str, str, KnowledgeHit], None]:
    """Keep provider-specific query setup outside the semantic assertions."""

    def prepare(tenant_id: str, application_id: str, hit: KnowledgeHit) -> None:
        knowledge_query_provider.hits[(tenant_id, application_id, hit.source_id, hit.document_version)] = hit

    return prepare


@pytest.fixture
def inbound_message_provider():
    return FakeInboundMessageProvider()


@pytest.fixture
def inbound_payload() -> bytes:
    return b"synthetic"


@pytest.fixture
def outbound_message_provider():
    return FakeOutboundMessageProvider()


@pytest.fixture
def outbound_envelope() -> OutboundEnvelope:
    return OutboundEnvelope(
        tenant_id="t",
        application_id="a",
        case_id="c",
        run_id="r",
        message_id="m",
        recipient_ref="approved-test",
        body="x",
        authorization_ref="auth",
        idempotency_key="key",
    )


@pytest.fixture
def tool_executor():
    return FakeToolExecutor()


@pytest.fixture
def tool_request() -> ToolRequest:
    return ToolRequest(
        tenant_id="t",
        application_id="a",
        case_id="c",
        run_id="r",
        action_id="act",
        capability="case.route",
        authorization_ref="auth",
        idempotency_key="key",
        input={},
        dry_run=True,
    )


@pytest.fixture
def event_publisher():
    return FakeEventPublisher()


@pytest.fixture
def observe_published_events(
    event_publisher: FakeEventPublisher,
) -> Callable[[], tuple[AuditEvent, ...]]:
    """Keep provider-specific observation outside the semantic assertions."""
    return lambda: tuple(event_publisher.events)


@pytest.fixture
def identity_provider():
    return FakeIdentityProvider()


@pytest.fixture
def valid_identity_credential() -> str:
    return "synthetic-valid"


@pytest.fixture
def invalid_identity_credential() -> str:
    return "invalid"


@pytest.fixture
def identity_failure_error() -> type[BaseException]:
    return PermissionError
