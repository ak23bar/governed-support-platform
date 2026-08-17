from collections.abc import Callable

import pytest

from gps.domain.contracts import AuditEvent
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
    VectorRecord,
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
def vector_record() -> VectorRecord:
    return VectorRecord(
        tenant_id="t1",
        application_id="a1",
        record_id="v",
        corpus_version="c1",
        document_id="d",
        vector=(1.0,),
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
