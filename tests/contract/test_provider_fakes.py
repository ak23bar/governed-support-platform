from hashlib import sha256

import pytest

from gps.domain.contracts import AuditEvent, RequestRun, SupportCase
from gps.domain.enums import ActorType, CaseState, ReceiptStatus, RunStatus
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
    CaseRepository,
    EmbeddingBatch,
    EmbeddingProvider,
    EventPublisher,
    IdentityProvider,
    InboundMessageProvider,
    KnowledgeQueryProvider,
    KnowledgeSource,
    KnowledgeSourceProvider,
    ModelProvider,
    ModelRequest,
    ObjectArtifact,
    ObjectStore,
    OutboundEnvelope,
    OutboundMessageProvider,
    ToolExecutor,
    ToolRequest,
    VectorRecord,
    VectorStore,
)


def test_all_local_fakes_satisfy_runtime_protocols() -> None:
    pairs = [
        (FakeModelProvider(), ModelProvider),
        (FakeEmbeddingProvider(), EmbeddingProvider),
        (FakeVectorStore(), VectorStore),
        (FakeObjectStore(), ObjectStore),
        (FakeCaseRepository(), CaseRepository),
        (FakeKnowledgeSourceProvider(), KnowledgeSourceProvider),
        (FakeKnowledgeQueryProvider(), KnowledgeQueryProvider),
        (FakeInboundMessageProvider(), InboundMessageProvider),
        (FakeOutboundMessageProvider(), OutboundMessageProvider),
        (FakeToolExecutor(), ToolExecutor),
        (FakeEventPublisher(), EventPublisher),
        (FakeIdentityProvider(), IdentityProvider),
    ]
    assert all(isinstance(fake, protocol) for fake, protocol in pairs)


def test_model_and_embedding_fakes_return_typed_results() -> None:
    request = ModelRequest(
        tenant_id="t",
        application_id="a",
        case_id="c",
        run_id="r",
        profile_version="fake-1",
        prompt="hello",
        timeout_seconds=1,
    )
    model = FakeModelProvider().generate(request)
    batch = EmbeddingBatch(
        tenant_id="t",
        application_id="a",
        texts=("hello",),
        model_version="fake-1",
    )
    embedding = FakeEmbeddingProvider().embed(batch)
    assert model.redacted_receipt == {"fake": True}
    assert len(embedding.vectors[0]) == embedding.dimension


def test_storage_and_repository_fakes_are_tenant_isolated(compatibility) -> None:
    store = FakeObjectStore()
    artifact = ObjectArtifact(
        tenant_id="tenant-a",
        application_id="app",
        key="raw/1",
        version="1",
        content=b"safe",
        content_hash=sha256(b"safe").hexdigest(),
        retention="test",
    )
    store.put(artifact)
    assert store.get("tenant-a", "app", "raw/1", "1") == artifact
    with pytest.raises(KeyError):
        store.get("tenant-b", "app", "raw/1", "1")

    repository = FakeCaseRepository()
    case = SupportCase(
        tenant_id="tenant-a",
        application_id="app",
        case_id="case-1",
        channel="manual",
        requester_ref="synthetic",
        state=CaseState.RECEIVED,
        version=1,
    )
    repository.put_case(case)
    with pytest.raises(KeyError):
        repository.get_case("tenant-b", "app", "case-1")
    run = RequestRun(
        tenant_id="tenant-a",
        application_id="app",
        case_id="case-1",
        run_id="run-1",
        run_number=1,
        trigger="manual",
        environment="local",
        compatibility=compatibility,
        status=RunStatus.RECEIVED,
    )
    repository.put_run(run)
    progressed = run.model_copy(update={"status": RunStatus.NORMALIZED})
    repository.put_run(progressed)
    assert repository.get_run("tenant-a", "app", "run-1") == progressed


def test_vector_and_knowledge_fakes_filter_tenant_context() -> None:
    vectors = FakeVectorStore()
    vectors.upsert(
        (
            VectorRecord(
                tenant_id="tenant-a",
                application_id="app",
                record_id="v1",
                corpus_version="c1",
                document_id="d1",
                vector=(1.0,),
            ),
        )
    )
    query = VectorRecord(
        tenant_id="tenant-b",
        application_id="app",
        record_id="q",
        corpus_version="c1",
        document_id="q",
        vector=(1.0,),
    )
    assert vectors.search(query, 5) == ()

    provider = FakeKnowledgeSourceProvider()
    source = KnowledgeSource(
        tenant_id="tenant-a",
        application_id="app",
        source_id="s1",
        canonical_url="https://example.invalid/s1",
        title="Synthetic",
        version="1",
    )
    provider.add(
        AcquiredDocument(
            tenant_id="tenant-a",
            application_id="app",
            source=source,
            media_type="text/html",
            content=b"fixture",
            content_hash=sha256(b"fixture").hexdigest(),
        )
    )
    assert provider.discover("tenant-a", "app") == (source,)
    assert provider.discover("tenant-b", "app") == ()


def test_message_tool_identity_and_event_fakes_have_no_side_effects() -> None:
    inbound = FakeInboundMessageProvider().normalize("tenant-a", "app", b"fixture")
    assert inbound.body == "fixture"
    envelope = OutboundEnvelope(
        tenant_id="tenant-a",
        application_id="app",
        case_id="case-1",
        run_id="run-1",
        message_id="m1",
        recipient_ref="approved-test",
        body="fixture",
        authorization_ref="auth-1",
        idempotency_key="key-1",
    )
    assert FakeOutboundMessageProvider().send(envelope).status is ReceiptStatus.ACCEPTED
    tool = ToolRequest(
        tenant_id="tenant-a",
        application_id="app",
        case_id="case-1",
        run_id="run-1",
        action_id="a1",
        capability="fixture",
        authorization_ref="auth-1",
        idempotency_key="key-2",
        input={},
    )
    executor = FakeToolExecutor()
    assert executor.execute(tool).redacted_details["dry_run"] is True
    with pytest.raises(PermissionError, match="dry-run"):
        executor.execute(tool.model_copy(update={"dry_run": False, "idempotency_key": "key-3"}))
    identity = FakeIdentityProvider().authenticate("synthetic-valid", "tenant-a", "app")
    assert identity.tenant_id == "tenant-a"
    event = AuditEvent(
        tenant_id="tenant-a",
        application_id="app",
        case_id="case-1",
        run_id="run-1",
        event_id="e1",
        sequence=1,
        actor_type=ActorType.SYSTEM,
        actor_ref="test",
        event_type="TEST",
        payload={},
        payload_hash="hash",
    )
    publisher = FakeEventPublisher()
    publisher.publish(event)
    assert publisher.events == [event]
