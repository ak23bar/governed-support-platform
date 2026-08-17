from hashlib import sha256

import pytest

from gps.domain.contracts import AuditEvent, RequestRun, SupportCase
from gps.domain.enums import ActorType, CaseState, ReceiptStatus, RunStatus
from gps.providers.protocols import (
    AcquiredDocument,
    EmbeddingResult,
    KnowledgeHit,
    KnowledgeQuery,
    KnowledgeSource,
    ModelResult,
)


def test_model_provider_returns_typed_versioned_result(model_provider, model_request) -> None:
    result = model_provider.generate(model_request)
    assert isinstance(result, ModelResult)
    assert result.model_version


def test_embedding_provider_returns_typed_versioned_batch(embedding_provider, embedding_batch) -> None:
    result = embedding_provider.embed(embedding_batch)
    assert isinstance(result, EmbeddingResult)
    assert result.model_version
    assert len(result.vectors) == len(embedding_batch.texts)
    assert all(len(vector) == result.dimension for vector in result.vectors)


def test_vector_store_is_tenant_and_application_isolated(vector_store, vector_record) -> None:
    vector_store.upsert((vector_record,))
    assert any(match.record_id == vector_record.record_id for match in vector_store.search(vector_record, 1))
    other = vector_record.model_copy(update={"tenant_id": "t2", "record_id": "q"})
    assert vector_store.search(other, 1) == ()
    other_application = vector_record.model_copy(update={"application_id": "a2", "record_id": "q2"})
    assert vector_store.search(other_application, 1) == ()
    assert vector_store.healthy() is True


def test_object_store_is_versioned_isolated_and_idempotent(
    object_store, object_artifact, object_store_missing_error
) -> None:
    object_store.put(object_artifact)
    object_store.put(object_artifact)
    assert (
        object_store.get(
            object_artifact.tenant_id,
            object_artifact.application_id,
            object_artifact.key,
            object_artifact.version,
        )
        == object_artifact
    )
    with pytest.raises(object_store_missing_error):
        object_store.get(
            "other",
            object_artifact.application_id,
            object_artifact.key,
            object_artifact.version,
        )


def test_case_repository_semantics(case_repository, case_repository_missing_error, compatibility) -> None:
    case = SupportCase(
        tenant_id="t",
        application_id="a",
        case_id="c",
        channel="manual",
        requester_ref="synthetic",
        state=CaseState.RECEIVED,
        version=1,
    )
    case_repository.put_case(case)
    assert case_repository.get_case("t", "a", "c") == case
    with pytest.raises(case_repository_missing_error):
        case_repository.get_case("other", "a", "c")
    run = RequestRun(
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
    case_repository.put_run(run)
    case_repository.put_run(run.model_copy(update={"status": RunStatus.NORMALIZED}))
    assert case_repository.get_run("t", "a", "r").status is RunStatus.NORMALIZED


def test_knowledge_source_provider_is_tenant_isolated(knowledge_source_provider, prepare_knowledge_source) -> None:
    source = KnowledgeSource(
        tenant_id="t",
        application_id="a",
        source_id="s",
        canonical_url="https://example.invalid/s",
        title="Synthetic",
        version="1",
    )
    document = AcquiredDocument(
        tenant_id="t",
        application_id="a",
        source=source,
        media_type="text/html",
        content=b"x",
        content_hash=sha256(b"x").hexdigest(),
    )
    prepare_knowledge_source(document)
    assert source in knowledge_source_provider.discover("t", "a")
    assert knowledge_source_provider.fetch("t", "a", "s") == document
    assert knowledge_source_provider.discover("other", "a") == ()


def test_deferred_knowledge_query_seam_is_isolated(knowledge_query_provider, prepare_knowledge_query) -> None:
    hit = KnowledgeHit(
        source_id="s",
        document_version="1",
        canonical_url="https://example.invalid/s",
        locator="h1",
        text="synthetic mtap",
    )
    prepare_knowledge_query("t", "a", hit)
    request = KnowledgeQuery(tenant_id="t", application_id="a", query="mtap", corpus_version="c1")
    assert hit in knowledge_query_provider.search(request)
    assert knowledge_query_provider.retrieve("t", "a", "s", "1") == hit
    assert knowledge_query_provider.search(request.model_copy(update={"tenant_id": "other"})) == ()


def test_inbound_provider_is_context_scoped(inbound_message_provider, inbound_payload) -> None:
    first = inbound_message_provider.normalize("t", "a", inbound_payload)
    assert first.tenant_id == "t" and first.application_id == "a"


def test_outbound_provider_is_idempotent_and_reconcilable(outbound_message_provider, outbound_envelope) -> None:
    first = outbound_message_provider.send(outbound_envelope)
    assert outbound_message_provider.send(outbound_envelope) == first
    assert outbound_message_provider.reconcile(first.request_id) == first
    assert first.status in {ReceiptStatus.ACCEPTED, ReceiptStatus.DELIVERED}


def test_tool_executor_is_idempotent_and_reconcilable(tool_executor, tool_request) -> None:
    receipt = tool_executor.execute(tool_request)
    assert tool_executor.execute(tool_request) == receipt
    assert tool_executor.reconcile(receipt.request_id) == receipt
    assert receipt.status in {ReceiptStatus.ACCEPTED, ReceiptStatus.DELIVERED}


def test_event_publisher_preserves_the_audit_event(event_publisher, observe_published_events) -> None:
    event = AuditEvent(
        tenant_id="t",
        application_id="a",
        case_id="c",
        run_id="r",
        event_id="e",
        sequence=1,
        actor_type=ActorType.SYSTEM,
        actor_ref="runtime",
        event_type="TEST",
        payload={},
        payload_hash="hash",
    )
    event_publisher.publish(event)
    assert event in observe_published_events()


def test_identity_provider_authenticates_or_fails_closed(
    identity_provider,
    valid_identity_credential,
    invalid_identity_credential,
    identity_failure_error,
) -> None:
    identity = identity_provider.authenticate(valid_identity_credential, "t", "a")
    assert identity.tenant_id == "t" and identity.application_id == "a"
    with pytest.raises(identity_failure_error):
        identity_provider.authenticate(invalid_identity_credential, "t", "a")
