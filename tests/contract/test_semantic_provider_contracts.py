from hashlib import sha256

import pytest

from gps.domain.contracts import AuditEvent
from gps.domain.enums import ActorType, CaseState, ReceiptStatus, RunStatus
from gps.providers.protocols import (
    AcquiredDocument,
    EmbeddingResult,
    KnowledgeHit,
    KnowledgeQuery,
    KnowledgeSource,
    ModelResult,
    OptimisticConcurrencyError,
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


def _record_ids(matches) -> set[str]:
    return {match.record_id for match in matches}


def test_vector_store_search_is_scoped_and_filtered(vector_store, vector_records, vector_search_request) -> None:
    vector_store.upsert(vector_records)
    assert _record_ids(vector_store.search(vector_search_request)) == {"target"}
    assert _record_ids(vector_store.search(vector_search_request.model_copy(update={"tenant_id": "t2"}))) == {
        "other-tenant"
    }
    assert _record_ids(vector_store.search(vector_search_request.model_copy(update={"application_id": "a2"}))) == {
        "other-application"
    }
    assert _record_ids(vector_store.search(vector_search_request.model_copy(update={"corpus_version": "c2"}))) == {
        "other-corpus"
    }
    assert _record_ids(vector_store.search(vector_search_request.model_copy(update={"document_id": "d2"}))) == {
        "other-document"
    }
    assert _record_ids(
        vector_store.search(vector_search_request.model_copy(update={"metadata_filters": {"kind": "warning"}}))
    ) == {"other-metadata"}
    assert vector_store.healthy() is True


def test_vector_store_delete_obeys_the_same_scope(
    vector_store, vector_records, vector_search_request, vector_delete_request
) -> None:
    vector_store.upsert(vector_records)
    vector_store.delete(vector_delete_request)
    assert vector_store.search(vector_search_request) == ()
    assert _record_ids(
        vector_store.search(vector_search_request.model_copy(update={"metadata_filters": {"kind": "warning"}}))
    ) == {"other-metadata"}
    assert _record_ids(vector_store.search(vector_search_request.model_copy(update={"corpus_version": "c2"}))) == {
        "other-corpus"
    }


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


def test_case_repository_covers_typed_case_records(
    case_repository,
    case_repository_missing_error,
    support_case,
    request_run,
    case_decision,
    tool_action,
    final_outcome,
) -> None:
    case_repository.put_case(support_case)
    assert case_repository.get_case("t", "a", "c") == support_case
    with pytest.raises(case_repository_missing_error):
        case_repository.get_case("other", "a", "c")
    case_repository.put_run(request_run)
    case_repository.put_run(request_run.model_copy(update={"status": RunStatus.NORMALIZED}))
    assert case_repository.get_run("t", "a", "r").status is RunStatus.NORMALIZED
    case_repository.put_decision(case_decision)
    assert case_repository.get_decision("t", "a", "c", "r", "decision-1") == case_decision
    case_repository.put_action(tool_action)
    assert case_repository.get_action("t", "a", "c", "r", "action-1") == tool_action
    case_repository.put_outcome(final_outcome)
    assert case_repository.get_outcome("t", "a", "c", "r", "outcome-1") == final_outcome
    for getter, record_id in (
        (case_repository.get_decision, "decision-1"),
        (case_repository.get_action, "action-1"),
        (case_repository.get_outcome, "outcome-1"),
    ):
        with pytest.raises(case_repository_missing_error):
            getter("other", "a", "c", "r", record_id)
        with pytest.raises(case_repository_missing_error):
            getter("t", "a", "c", "other-run", record_id)


def test_case_repository_uses_explicit_optimistic_concurrency(case_repository, support_case) -> None:
    case_repository.put_case(support_case)
    updated = support_case.model_copy(update={"state": CaseState.PROCESSING, "version": 2})
    case_repository.put_case(updated, expected_version=1)
    stale = support_case.model_copy(update={"state": CaseState.AWAITING_REVIEW, "version": 2})
    with pytest.raises(OptimisticConcurrencyError):
        case_repository.put_case(stale, expected_version=1)
    assert case_repository.get_case("t", "a", "c") == updated


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
