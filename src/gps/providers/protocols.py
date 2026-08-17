from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from pydantic import Field

from gps.domain.base import ContextualContract, Contract, RunContextContract
from gps.domain.contracts import AuditEvent, RequestRun, SupportCase
from gps.domain.enums import ReceiptStatus


class ModelRequest(RunContextContract):
    profile_version: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    timeout_seconds: float = Field(gt=0)


class ModelResult(Contract):
    text: str
    model_version: str = Field(min_length=1)
    usage: dict[str, int]
    redacted_receipt: dict[str, Any]


class EmbeddingBatch(ContextualContract):
    texts: tuple[str, ...] = Field(min_length=1)
    model_version: str = Field(min_length=1)


class EmbeddingResult(Contract):
    vectors: tuple[tuple[float, ...], ...]
    model_version: str = Field(min_length=1)
    dimension: int = Field(gt=0)


class VectorRecord(ContextualContract):
    record_id: str = Field(min_length=1)
    corpus_version: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    vector: tuple[float, ...] = Field(min_length=1)
    metadata: dict[str, str] = Field(default_factory=dict)


class VectorMatch(Contract):
    record_id: str = Field(min_length=1)
    score: float
    metadata: dict[str, str] = Field(default_factory=dict)


class ObjectArtifact(ContextualContract):
    key: str = Field(min_length=1)
    version: str = Field(min_length=1)
    content: bytes
    content_hash: str = Field(min_length=1)
    retention: str = Field(min_length=1)


class KnowledgeSource(ContextualContract):
    source_id: str = Field(min_length=1)
    canonical_url: str = Field(min_length=1)
    title: str = Field(min_length=1)
    version: str = Field(min_length=1)
    metadata: dict[str, str] = Field(default_factory=dict)


class AcquiredDocument(ContextualContract):
    source: KnowledgeSource
    media_type: str = Field(min_length=1)
    content: bytes
    content_hash: str = Field(min_length=1)


class KnowledgeQuery(ContextualContract):
    query: str = Field(min_length=1)
    corpus_version: str = Field(min_length=1)


class KnowledgeHit(Contract):
    source_id: str = Field(min_length=1)
    document_version: str = Field(min_length=1)
    canonical_url: str = Field(min_length=1)
    locator: str = Field(min_length=1)
    text: str = Field(min_length=1)


class NormalizedMessage(ContextualContract):
    message_id: str = Field(min_length=1)
    thread_id: str = Field(min_length=1)
    sender_ref: str = Field(min_length=1)
    subject: str
    body: str = Field(min_length=1)


class OutboundEnvelope(RunContextContract):
    message_id: str = Field(min_length=1)
    recipient_ref: str = Field(min_length=1)
    body: str = Field(min_length=1)
    authorization_ref: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)


class ProviderReceipt(Contract):
    request_id: str = Field(min_length=1)
    status: ReceiptStatus
    redacted_details: dict[str, Any] = Field(default_factory=dict)


class ToolRequest(RunContextContract):
    action_id: str = Field(min_length=1)
    capability: str = Field(min_length=1)
    authorization_ref: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1)
    input: dict[str, Any]
    dry_run: bool = True


class Identity(ContextualContract):
    actor_id: str = Field(min_length=1)
    roles: tuple[str, ...]
    claims: dict[str, str] = Field(default_factory=dict)


@runtime_checkable
class ModelProvider(Protocol):
    def generate(self, request: ModelRequest) -> ModelResult: ...


@runtime_checkable
class EmbeddingProvider(Protocol):
    def embed(self, request: EmbeddingBatch) -> EmbeddingResult: ...


@runtime_checkable
class VectorStore(Protocol):
    def upsert(self, records: tuple[VectorRecord, ...]) -> None: ...

    def delete(self, tenant_id: str, application_id: str, record_ids: tuple[str, ...]) -> None: ...

    def search(self, query: VectorRecord, limit: int) -> tuple[VectorMatch, ...]: ...

    def healthy(self) -> bool: ...


@runtime_checkable
class ObjectStore(Protocol):
    def put(self, artifact: ObjectArtifact) -> None: ...

    def get(self, tenant_id: str, application_id: str, key: str, version: str) -> ObjectArtifact: ...


@runtime_checkable
class CaseRepository(Protocol):
    def put_case(self, case: SupportCase) -> None: ...

    def get_case(self, tenant_id: str, application_id: str, case_id: str) -> SupportCase: ...

    def put_run(self, run: RequestRun) -> None: ...

    def get_run(self, tenant_id: str, application_id: str, run_id: str) -> RequestRun: ...

    def append_event(self, event: AuditEvent) -> None: ...


@runtime_checkable
class KnowledgeSourceProvider(Protocol):
    def discover(
        self, tenant_id: str, application_id: str, checkpoint: str | None = None
    ) -> tuple[KnowledgeSource, ...]: ...

    def fetch(self, tenant_id: str, application_id: str, source_id: str) -> AcquiredDocument: ...


@runtime_checkable
class KnowledgeQueryProvider(Protocol):
    """Deferred live-query seam; no production implementation exists in E01."""

    def search(self, request: KnowledgeQuery) -> tuple[KnowledgeHit, ...]: ...

    def retrieve(self, tenant_id: str, application_id: str, source_id: str, version: str) -> KnowledgeHit: ...


@runtime_checkable
class InboundMessageProvider(Protocol):
    def normalize(self, tenant_id: str, application_id: str, payload: bytes) -> NormalizedMessage: ...


@runtime_checkable
class OutboundMessageProvider(Protocol):
    def send(self, envelope: OutboundEnvelope) -> ProviderReceipt: ...

    def reconcile(self, request_id: str) -> ProviderReceipt: ...


@runtime_checkable
class ToolExecutor(Protocol):
    def execute(self, request: ToolRequest) -> ProviderReceipt: ...

    def reconcile(self, request_id: str) -> ProviderReceipt: ...


@runtime_checkable
class EventPublisher(Protocol):
    def publish(self, event: AuditEvent) -> None: ...


@runtime_checkable
class IdentityProvider(Protocol):
    def authenticate(self, credential: str, tenant_id: str, application_id: str) -> Identity: ...
