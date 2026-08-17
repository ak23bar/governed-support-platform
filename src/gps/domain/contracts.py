from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field, model_validator

from gps.domain.base import ContextualContract, Contract, RunContextContract, utc_now
from gps.domain.enums import (
    ActorType,
    CanonicalBlockType,
    CaseState,
    CorpusPublicationStatus,
    DispatchMode,
    EnvironmentName,
    EvidenceCoverage,
    HumanAction,
    OutcomeDisposition,
    PassStatus,
    PolicyEffect,
    ReceiptStatus,
    ResolutionType,
    RouteType,
    RunStatus,
    SourceDocumentStatus,
    ToolActionStatus,
)


class CompatibilityTuple(Contract):
    runtime_version: str = Field(min_length=1)
    application_package_version: str = Field(min_length=1)
    workflow_version: str = Field(min_length=1)
    corpus_version: str = Field(min_length=1)
    policy_version: str = Field(min_length=1)
    model_profile_version: str = Field(min_length=1)
    adapter_versions: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def versions_must_be_explicit(self) -> CompatibilityTuple:
        values = (
            self.runtime_version,
            self.application_package_version,
            self.workflow_version,
            self.corpus_version,
            self.policy_version,
            self.model_profile_version,
            *self.adapter_versions,
        )
        if any(value.lower() in {"latest", "current", "*"} for value in values):
            raise ValueError("mutable version aliases are incompatible")
        return self


class SupportCase(ContextualContract):
    case_id: str = Field(min_length=1)
    channel: str = Field(min_length=1)
    external_thread_ref: str | None = None
    requester_ref: str = Field(min_length=1)
    state: CaseState
    version: int = Field(ge=1)
    active_run_id: str | None = None
    category: str | None = None
    risk_flags: tuple[str, ...] = ()
    route: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    closed_at: datetime | None = None


class RequestRun(ContextualContract):
    run_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    run_number: int = Field(ge=1)
    trigger: str = Field(min_length=1)
    environment: EnvironmentName
    compatibility: CompatibilityTuple
    status: RunStatus
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    failure_class: str | None = None


class SourceLink(Contract):
    label: str = Field(min_length=1)
    url: str = Field(min_length=1)


class CanonicalBlock(Contract):
    block_id: str = Field(min_length=1)
    block_type: CanonicalBlockType
    heading_path: tuple[str, ...] = ()
    ordinal: int = Field(ge=1)
    text: str = Field(min_length=1)
    links: tuple[SourceLink, ...] = ()
    source_locator: str = Field(min_length=1)


class SourceDocument(ContextualContract):
    document_id: str = Field(min_length=1)
    canonical_url: str = Field(min_length=1)
    title: str = Field(min_length=1)
    product: str = Field(min_length=1)
    category: str = Field(min_length=1)
    language: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    status: SourceDocumentStatus
    effective_from: datetime | None = None
    effective_to: datetime | None = None
    current_version_id: str | None = None

    @model_validator(mode="after")
    def approved_document_has_current_version(self) -> SourceDocument:
        if self.status is SourceDocumentStatus.APPROVED and self.current_version_id is None:
            raise ValueError("approved source document requires a current version")
        if self.effective_from and self.effective_to and self.effective_to < self.effective_from:
            raise ValueError("source document effective dates are invalid")
        return self


class SourceDocumentVersion(ContextualContract):
    version_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    content_hash: str = Field(min_length=1)
    raw_snapshot_ref: str = Field(min_length=1)
    blocks: tuple[CanonicalBlock, ...] = Field(min_length=1)
    generated_markdown_ref: str = Field(min_length=1)
    structural_diff_ref: str = Field(min_length=1)
    links: tuple[SourceLink, ...] = ()
    fetched_at: datetime
    published_at: datetime | None = None
    parser_version: str = Field(min_length=1)


class DocumentChunk(ContextualContract):
    chunk_id: str = Field(min_length=1)
    document_version_id: str = Field(min_length=1)
    ordinal: int = Field(ge=1)
    heading_path: tuple[str, ...] = ()
    block_ids: tuple[str, ...] = Field(min_length=1)
    block_types: tuple[CanonicalBlockType, ...] = Field(min_length=1)
    text: str = Field(min_length=1)
    locator: str = Field(min_length=1)
    canonical_url: str = Field(min_length=1)
    chunk_hash: str = Field(min_length=1)
    embedding_version: str = Field(min_length=1)


class CorpusVersion(ContextualContract):
    corpus_version: str = Field(min_length=1)
    document_version_ids: tuple[str, ...] = Field(min_length=1)
    parser_version: str = Field(min_length=1)
    chunker_version: str = Field(min_length=1)
    embedding_version: str = Field(min_length=1)
    validation_report_ref: str = Field(min_length=1)
    structural_diff_ref: str = Field(min_length=1)
    approval_actor: str | None = None
    approved_at: datetime | None = None
    publication_status: CorpusPublicationStatus

    @model_validator(mode="after")
    def approved_corpus_has_recorded_approval(self) -> CorpusVersion:
        if self.publication_status is CorpusPublicationStatus.APPROVED and (
            self.approval_actor is None or self.approved_at is None
        ):
            raise ValueError("approved corpus requires an approval actor and timestamp")
        return self


class SourceSpan(Contract):
    span_id: str = Field(min_length=1)
    document_version_id: str = Field(min_length=1)
    chunk_id: str = Field(min_length=1)
    heading_path: tuple[str, ...]
    canonical_url: str = Field(min_length=1)
    quote: str = Field(min_length=1)


class EvidenceIntent(Contract):
    intent_id: str = Field(min_length=1)
    normalized_intent: str = Field(min_length=1)
    coverage: EvidenceCoverage
    source_spans: tuple[SourceSpan, ...] = ()
    missing_requirements: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()


class RetrievalTrace(Contract):
    queries: tuple[str, ...]
    candidate_ids: tuple[str, ...]
    ranking_version: str = Field(min_length=1)
    embedding_version: str = Field(min_length=1)
    latency_ms: int = Field(ge=0)


class EvidencePacket(RunContextContract):
    packet_id: str = Field(min_length=1)
    corpus_version: str = Field(min_length=1)
    intents: tuple[EvidenceIntent, ...] = Field(min_length=1)
    retrieval_trace: RetrievalTrace


class IntentResolution(Contract):
    intent_id: str = Field(min_length=1)
    state: ResolutionType
    evidence_span_ids: tuple[str, ...] = ()
    unresolved_requirements: tuple[str, ...] = ()


class ResolutionDecision(RunContextContract):
    decision_id: str = Field(min_length=1)
    evidence_packet_id: str | None = None
    state: ResolutionType
    per_intent: tuple[IntentResolution, ...] = ()
    allowed_response_scope: tuple[str, ...] = ()
    unresolved_questions: tuple[str, ...] = ()
    proposed_response: str | None = None
    rationale_codes: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def substantive_resolution_requires_evidence(self) -> ResolutionDecision:
        if self.state is ResolutionType.RESOLVE and not self.evidence_packet_id:
            raise ValueError("RESOLVE requires an EvidencePacket")
        return self


class VerificationResult(RunContextContract):
    verification_id: str = Field(min_length=1)
    checks: dict[str, PassStatus] = Field(default_factory=dict)
    claims: tuple[str, ...] = ()
    support_mappings: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    procedure_checks: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    unsupported_claims: tuple[str, ...] = ()
    pass_status: PassStatus
    verifier_version: str = Field(min_length=1)


class PolicyDecision(RunContextContract):
    policy_decision_id: str = Field(min_length=1)
    policy_version: str = Field(min_length=1)
    evaluated_rules: tuple[str, ...] = Field(min_length=1)
    effect: PolicyEffect
    reason_codes: tuple[str, ...] = Field(min_length=1)
    decided_at: datetime = Field(default_factory=utc_now)


class DispatchDecision(RunContextContract):
    decision_id: str = Field(min_length=1)
    outcome: DispatchMode
    reason_codes: tuple[str, ...] = Field(min_length=1)
    policy_decision_id: str = Field(min_length=1)
    policy_version: str = Field(min_length=1)
    verification_result_id: str = Field(min_length=1)
    reviewer_required: bool

    @model_validator(mode="after")
    def reviewer_gate_matches_outcome(self) -> DispatchDecision:
        if self.outcome is DispatchMode.HUMAN_APPROVAL and not self.reviewer_required:
            raise ValueError("HUMAN_APPROVAL requires a reviewer")
        if self.outcome is DispatchMode.AUTOMATIC and self.reviewer_required:
            raise ValueError("AUTOMATIC cannot require pre-dispatch review")
        return self


class RoutingDecision(RunContextContract):
    decision_id: str = Field(min_length=1)
    route_type: RouteType
    queue_id: str | None = None
    team_id: str | None = None
    owner_id: str | None = None
    reason_codes: tuple[str, ...] = Field(min_length=1)
    service_target: str | None = None
    policy_version: str = Field(min_length=1)

    @model_validator(mode="after")
    def route_has_configured_target(self) -> RoutingDecision:
        if self.route_type is RouteType.NONE:
            if any((self.queue_id, self.team_id, self.owner_id)):
                raise ValueError("NONE route cannot name an owner target")
        elif not any((self.queue_id, self.team_id, self.owner_id)):
            raise ValueError("owned route requires queue, team, or owner")
        return self


class ToolAuthorization(Contract):
    actor_type: ActorType
    actor_ref: str = Field(min_length=1)
    capability: str = Field(min_length=1)
    grant_id: str = Field(min_length=1)


class ToolDryRun(Contract):
    status: PassStatus
    validated_at: datetime


class ToolReceipt(Contract):
    request_id: str = Field(min_length=1)
    status: ReceiptStatus
    failure_code: str | None = None
    reconciled_at: datetime | None = None


class ToolAction(RunContextContract):
    action_id: str = Field(min_length=1)
    tool_type: str = Field(min_length=1)
    tool_version: str = Field(min_length=1)
    typed_input: dict[str, Any]
    authorization: ToolAuthorization
    policy_decision_id: str = Field(min_length=1)
    policy_version: str = Field(min_length=1)
    dry_run: ToolDryRun
    idempotency_key: str = Field(min_length=1)
    status: ToolActionStatus
    attempts: int = Field(default=0, ge=0)
    receipt: ToolReceipt | None = None

    @model_validator(mode="after")
    def execution_state_requires_valid_gates(self) -> ToolAction:
        active = {
            ToolActionStatus.AUTHORIZED,
            ToolActionStatus.EXECUTING,
            ToolActionStatus.SUCCEEDED,
            ToolActionStatus.FAILED,
            ToolActionStatus.UNKNOWN,
        }
        if self.status in active and self.dry_run.status is not PassStatus.PASSED:
            raise ValueError("authorized/executed actions require a passed dry run")
        if self.status is ToolActionStatus.SUCCEEDED and (
            self.receipt is None or self.receipt.status not in {ReceiptStatus.ACCEPTED, ReceiptStatus.DELIVERED}
        ):
            raise ValueError("SUCCEEDED requires a validated success receipt")
        if self.status in {ToolActionStatus.FAILED, ToolActionStatus.UNKNOWN} and self.receipt is None:
            raise ValueError("failed or unknown actions require a receipt for reconciliation")
        return self


class EnvironmentConfig(Contract):
    environment: EnvironmentName
    tenant_id: str = Field(min_length=1)
    application_id: str = Field(min_length=1)
    deployment_target: str = Field(min_length=1)
    provider_profile_refs: tuple[str, ...] = Field(min_length=1)
    external_side_effects_enabled: bool = False
    approved_test_recipient_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def local_environment_has_no_external_effects(self) -> EnvironmentConfig:
        if self.environment is EnvironmentName.LOCAL and self.external_side_effects_enabled:
            raise ValueError("local environment cannot enable external side effects")
        return self


class HumanDecision(RunContextContract):
    decision_id: str = Field(min_length=1)
    actor_id: str = Field(min_length=1)
    action: HumanAction
    expected_case_version: int = Field(ge=1)
    reason_code: str = Field(min_length=1)
    structured_changes: dict[str, Any] = Field(default_factory=dict)
    text_diff: str | None = None
    decided_at: datetime = Field(default_factory=utc_now)


class AuditEvent(RunContextContract):
    event_id: str = Field(min_length=1)
    sequence: int = Field(ge=1)
    actor_type: ActorType
    actor_ref: str = Field(min_length=1)
    event_type: str = Field(min_length=1)
    payload: dict[str, Any]
    payload_hash: str = Field(min_length=1)
    occurred_at: datetime = Field(default_factory=utc_now)
    recorded_at: datetime = Field(default_factory=utc_now)


class FinalOutcome(RunContextContract):
    outcome_id: str = Field(min_length=1)
    disposition: OutcomeDisposition
    dispatch_status: ReceiptStatus
    external_refs: tuple[str, ...] = ()
    close_reason: str = Field(min_length=1)
    timing_summary: dict[str, float] = Field(default_factory=dict)
    quality_flags: tuple[str, ...] = ()


class FeedbackEvent(ContextualContract):
    """Immutable outcome evidence attached to a case after resolution."""

    feedback_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    rating: int | None = None
    feedback_type: str | None = Field(default=None, min_length=1)
    comment: str = Field(min_length=1)
    received_at: datetime

    @model_validator(mode="after")
    def rating_or_type_is_present(self) -> FeedbackEvent:
        if self.rating is None and self.feedback_type is None:
            raise ValueError("feedback requires a rating or feedback type")
        return self


class ReopenEvent(ContextualContract):
    """Immutable link from a preserved prior outcome to a new processing run."""

    reopen_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    prior_outcome_id: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    new_message_or_event_ref: str = Field(min_length=1)
    reopened_at: datetime
    new_run_id: str = Field(min_length=1)
