from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from gps.domain.contracts import (
    AuditEvent,
    DispatchDecision,
    FinalOutcome,
    HumanDecision,
    PolicyDecision,
    RequestRun,
    ResolutionDecision,
    RoutingDecision,
    SupportCase,
    ToolAction,
    VerificationResult,
)
from gps.domain.enums import ReceiptStatus, RunStatus
from gps.providers.protocols import (
    AcquiredDocument,
    CaseDecision,
    EmbeddingBatch,
    EmbeddingResult,
    Identity,
    KnowledgeHit,
    KnowledgeQuery,
    KnowledgeSource,
    ModelRequest,
    ModelResult,
    NormalizedMessage,
    ObjectArtifact,
    OptimisticConcurrencyError,
    OutboundEnvelope,
    ProviderReceipt,
    ToolRequest,
    VectorDeleteRequest,
    VectorMatch,
    VectorRecord,
    VectorSearchRequest,
)


def _scope(tenant_id: str, application_id: str) -> tuple[str, str]:
    return tenant_id, application_id


@dataclass
class FakeModelProvider:
    text: str = "synthetic response"

    def generate(self, request: ModelRequest) -> ModelResult:
        return ModelResult(
            text=self.text,
            model_version=request.profile_version,
            usage={"input": len(request.prompt), "output": len(self.text)},
            redacted_receipt={"fake": True},
        )


@dataclass
class FakeEmbeddingProvider:
    dimension: int = 3

    def embed(self, request: EmbeddingBatch) -> EmbeddingResult:
        vectors = tuple(tuple(float((len(text) + i) % 11) for i in range(self.dimension)) for text in request.texts)
        return EmbeddingResult(
            vectors=vectors,
            model_version=request.model_version,
            dimension=self.dimension,
        )


@dataclass
class FakeVectorStore:
    records: dict[tuple[str, str, str, str], VectorRecord] = field(default_factory=dict)

    def upsert(self, records: tuple[VectorRecord, ...]) -> None:
        for record in records:
            key = (
                *_scope(record.tenant_id, record.application_id),
                record.corpus_version,
                record.record_id,
            )
            self.records[key] = record

    def delete(self, request: VectorDeleteRequest) -> None:
        keys = [
            key
            for key, record in self.records.items()
            if _vector_record_matches(record, request)
            and (not request.record_ids or record.record_id in request.record_ids)
        ]
        for key in keys:
            self.records.pop(key)

    def search(self, request: VectorSearchRequest) -> tuple[VectorMatch, ...]:
        matches = [
            VectorMatch(record_id=item.record_id, score=1.0, metadata=item.metadata)
            for item in self.records.values()
            if _vector_record_matches(item, request)
        ]
        return tuple(matches[: request.limit])

    def healthy(self) -> bool:
        return True


def _vector_record_matches(record: VectorRecord, request: VectorSearchRequest | VectorDeleteRequest) -> bool:
    return (
        _scope(record.tenant_id, record.application_id) == _scope(request.tenant_id, request.application_id)
        and record.corpus_version == request.corpus_version
        and (request.document_id is None or record.document_id == request.document_id)
        and all(record.metadata.get(key) == value for key, value in request.metadata_filters.items())
    )


@dataclass
class FakeObjectStore:
    artifacts: dict[tuple[str, str, str, str], ObjectArtifact] = field(default_factory=dict)

    def put(self, artifact: ObjectArtifact) -> None:
        key = (
            *_scope(artifact.tenant_id, artifact.application_id),
            artifact.key,
            artifact.version,
        )
        prior = self.artifacts.get(key)
        if prior is not None and prior != artifact:
            raise ValueError("object key/version is immutable")
        if hashlib.sha256(artifact.content).hexdigest() != artifact.content_hash:
            raise ValueError("object content hash does not match")
        self.artifacts[key] = artifact

    def get(self, tenant_id: str, application_id: str, key: str, version: str) -> ObjectArtifact:
        return self.artifacts[(tenant_id, application_id, key, version)]


@dataclass
class FakeCaseRepository:
    cases: dict[tuple[str, str, str], SupportCase] = field(default_factory=dict)
    runs: dict[tuple[str, str, str], RequestRun] = field(default_factory=dict)
    decisions: dict[tuple[str, str, str, str, str], CaseDecision] = field(default_factory=dict)
    actions: dict[tuple[str, str, str, str, str], ToolAction] = field(default_factory=dict)
    outcomes: dict[tuple[str, str, str, str, str], FinalOutcome] = field(default_factory=dict)
    events: list[AuditEvent] = field(default_factory=list)

    def put_case(self, case: SupportCase, *, expected_version: int | None = None) -> None:
        key = (*_scope(case.tenant_id, case.application_id), case.case_id)
        prior = self.cases.get(key)
        if prior == case:
            return
        if prior is None:
            if expected_version is not None:
                raise OptimisticConcurrencyError("case does not exist at the expected version")
        elif expected_version != prior.version or case.version != prior.version + 1:
            raise OptimisticConcurrencyError("case version changed before update")
        self.cases[key] = case

    def get_case(self, tenant_id: str, application_id: str, case_id: str) -> SupportCase:
        return self.cases[(tenant_id, application_id, case_id)]

    def put_run(self, run: RequestRun) -> None:
        key = (*_scope(run.tenant_id, run.application_id), run.run_id)
        prior = self.runs.get(key)
        for stored_key, stored_run in self.runs.items():
            same_attempt_number = (
                stored_key != key
                and stored_run.case_id == run.case_id
                and stored_run.run_number == run.run_number
                and stored_run.tenant_id == run.tenant_id
                and stored_run.application_id == run.application_id
            )
            if same_attempt_number:
                raise ValueError("RequestRun identity and configuration snapshot are immutable")
        if prior is not None:
            immutable_fields = (
                "tenant_id",
                "application_id",
                "case_id",
                "run_id",
                "run_number",
                "trigger",
                "environment",
                "compatibility",
                "started_at",
            )
            if any(getattr(prior, name) != getattr(run, name) for name in immutable_fields):
                raise ValueError("RequestRun identity and configuration snapshot are immutable")
            terminal = {
                RunStatus.CLOSED,
                RunStatus.REJECTED,
                RunStatus.AUTO_DISPATCHED,
                RunStatus.DISPATCHED,
                RunStatus.INTAKE_REJECTED,
                RunStatus.PROCESSING_FAILED,
                RunStatus.ACTION_FAILED,
                RunStatus.DISPATCH_FAILED,
                RunStatus.DEAD_LETTERED,
                RunStatus.CANCELLED,
            }
            if prior.status in terminal and prior != run:
                raise ValueError("terminal RequestRun is immutable; create a new run")
        self.runs[key] = run

    def get_run(self, tenant_id: str, application_id: str, run_id: str) -> RequestRun:
        return self.runs[(tenant_id, application_id, run_id)]

    def put_decision(self, decision: CaseDecision) -> None:
        key = (
            *_scope(decision.tenant_id, decision.application_id),
            decision.case_id,
            decision.run_id,
            _decision_id(decision),
        )
        self.decisions[key] = decision

    def get_decision(
        self,
        tenant_id: str,
        application_id: str,
        case_id: str,
        run_id: str,
        decision_id: str,
    ) -> CaseDecision:
        return self.decisions[(tenant_id, application_id, case_id, run_id, decision_id)]

    def put_action(self, action: ToolAction) -> None:
        key = (*_scope(action.tenant_id, action.application_id), action.case_id, action.run_id, action.action_id)
        self.actions[key] = action

    def get_action(self, tenant_id: str, application_id: str, case_id: str, run_id: str, action_id: str) -> ToolAction:
        return self.actions[(tenant_id, application_id, case_id, run_id, action_id)]

    def put_outcome(self, outcome: FinalOutcome) -> None:
        key = (*_scope(outcome.tenant_id, outcome.application_id), outcome.case_id, outcome.run_id, outcome.outcome_id)
        self.outcomes[key] = outcome

    def get_outcome(
        self, tenant_id: str, application_id: str, case_id: str, run_id: str, outcome_id: str
    ) -> FinalOutcome:
        return self.outcomes[(tenant_id, application_id, case_id, run_id, outcome_id)]

    def append_event(self, event: AuditEvent) -> None:
        if any(existing.event_id == event.event_id for existing in self.events):
            if event in self.events:
                return
            raise ValueError("AuditEvent identity is immutable")
        scoped = [
            item
            for item in self.events
            if _scope(item.tenant_id, item.application_id) == _scope(event.tenant_id, event.application_id)
            and item.case_id == event.case_id
        ]
        if scoped and event.sequence <= scoped[-1].sequence:
            raise ValueError("AuditEvent sequence must increase within a case")
        self.events.append(event)


def _decision_id(decision: CaseDecision) -> str:
    if isinstance(decision, VerificationResult):
        return decision.verification_id
    if isinstance(decision, PolicyDecision):
        return decision.policy_decision_id
    if isinstance(decision, (ResolutionDecision, DispatchDecision, RoutingDecision, HumanDecision)):
        return decision.decision_id
    raise TypeError(f"unsupported decision contract: {type(decision).__name__}")


@dataclass
class FakeKnowledgeSourceProvider:
    documents: dict[tuple[str, str, str], AcquiredDocument] = field(default_factory=dict)

    def add(self, document: AcquiredDocument) -> None:
        if _scope(document.tenant_id, document.application_id) != _scope(
            document.source.tenant_id, document.source.application_id
        ):
            raise ValueError("source and document context must match")
        if hashlib.sha256(document.content).hexdigest() != document.content_hash:
            raise ValueError("acquired content hash does not match")
        key = (
            *_scope(document.tenant_id, document.application_id),
            document.source.source_id,
        )
        self.documents[key] = document

    def discover(
        self, tenant_id: str, application_id: str, checkpoint: str | None = None
    ) -> tuple[KnowledgeSource, ...]:
        del checkpoint
        return tuple(doc.source for key, doc in self.documents.items() if key[:2] == _scope(tenant_id, application_id))

    def fetch(self, tenant_id: str, application_id: str, source_id: str) -> AcquiredDocument:
        return self.documents[(tenant_id, application_id, source_id)]


@dataclass
class FakeKnowledgeQueryProvider:
    hits: dict[tuple[str, str, str, str], KnowledgeHit] = field(default_factory=dict)

    def search(self, request: KnowledgeQuery) -> tuple[KnowledgeHit, ...]:
        return tuple(
            hit
            for key, hit in self.hits.items()
            if key[:2] == _scope(request.tenant_id, request.application_id)
            and request.query.lower() in hit.text.lower()
        )

    def retrieve(self, tenant_id: str, application_id: str, source_id: str, version: str) -> KnowledgeHit:
        return self.hits[(tenant_id, application_id, source_id, version)]


class FakeInboundMessageProvider:
    def normalize(self, tenant_id: str, application_id: str, payload: bytes) -> NormalizedMessage:
        digest = hashlib.sha256(payload).hexdigest()[:16]
        return NormalizedMessage(
            tenant_id=tenant_id,
            application_id=application_id,
            message_id=f"msg_{digest}",
            thread_id=f"thread_{digest}",
            sender_ref="synthetic",
            subject="synthetic",
            body=payload.decode(),
        )


@dataclass
class FakeOutboundMessageProvider:
    receipts: dict[str, ProviderReceipt] = field(default_factory=dict)
    envelopes: dict[str, OutboundEnvelope] = field(default_factory=dict)

    def send(self, envelope: OutboundEnvelope) -> ProviderReceipt:
        prior_envelope = self.envelopes.get(envelope.idempotency_key)
        if prior_envelope is not None and prior_envelope != envelope:
            raise ValueError("idempotency key cannot identify a different outbound request")
        if prior_envelope is not None:
            return self.receipts[envelope.idempotency_key]
        receipt = ProviderReceipt(
            request_id=envelope.idempotency_key,
            status=ReceiptStatus.ACCEPTED,
            redacted_details={"fake": True},
        )
        self.receipts[receipt.request_id] = receipt
        self.envelopes[envelope.idempotency_key] = envelope
        return receipt

    def reconcile(self, request_id: str) -> ProviderReceipt:
        return self.receipts[request_id]


@dataclass
class FakeToolExecutor(FakeOutboundMessageProvider):
    requests: dict[str, ToolRequest] = field(default_factory=dict)

    def execute(self, request: ToolRequest) -> ProviderReceipt:
        if not request.dry_run:
            raise PermissionError("E01 fake permits dry-run tool actions only")
        prior = self.requests.get(request.idempotency_key)
        if prior is not None and prior != request:
            raise ValueError("idempotency key cannot identify a different tool request")
        if prior is not None:
            return self.receipts[request.idempotency_key]
        receipt = ProviderReceipt(
            request_id=request.idempotency_key,
            status=ReceiptStatus.ACCEPTED,
            redacted_details={"dry_run": True},
        )
        self.receipts[receipt.request_id] = receipt
        self.requests[request.idempotency_key] = request
        return receipt


@dataclass
class FakeEventPublisher:
    events: list[AuditEvent] = field(default_factory=list)

    def publish(self, event: AuditEvent) -> None:
        self.events.append(event)


class FakeIdentityProvider:
    def authenticate(self, credential: str, tenant_id: str, application_id: str) -> Identity:
        if credential != "synthetic-valid":
            raise PermissionError("invalid synthetic credential")
        return Identity(
            tenant_id=tenant_id,
            application_id=application_id,
            actor_id="actor_fake",
            roles=("reviewer",),
        )
