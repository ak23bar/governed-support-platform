/**
 * DERIVED from the E01 Python/Pydantic domain contracts in src/gps/domain.
 *
 * The frozen Platform v1.5 and MOHID v0.6 living specifications remain
 * authoritative. Python/Pydantic is the current backend implementation source
 * of truth. This file is a readonly, non-runtime declaration surface for
 * downstream TypeScript consumers; it contains no validation or policy logic.
 */

export type Iso8601Timestamp = string;

export type ResolutionType = "RESOLVE" | "CLARIFY" | "ESCALATE" | "REJECT" | "NO_ACTION";
export type DispatchMode = "AUTOMATIC" | "HUMAN_APPROVAL" | "DENIED";
export type RouteType = "NONE" | "CENTRAL" | "LEVEL_1" | "LEVEL_2" | "SPECIALIST" | "MANAGER";
export type CaseState =
  | "RECEIVED"
  | "PROCESSING"
  | "AWAITING_CLARIFICATION"
  | "AWAITING_REVIEW"
  | "ROUTED"
  | "DISPATCH_PENDING"
  | "RESOLVED"
  | "CLOSED"
  | "FAILED";
export type RunStatus =
  | "RECEIVED"
  | "NORMALIZED"
  | "CLASSIFIED"
  | "EVIDENCE_READY"
  | "RESOLUTION_PROPOSED"
  | "VERIFIED"
  | "DISPATCH_DECIDED"
  | "AWAITING_REVIEW"
  | "APPROVED"
  | "EDITED"
  | "CLARIFICATION_REQUESTED"
  | "ESCALATED"
  | "REJECTED"
  | "REROUTED"
  | "AUTO_DISPATCHED"
  | "DISPATCHED"
  | "CLOSED"
  | "INTAKE_REJECTED"
  | "PROCESSING_FAILED"
  | "ACTION_FAILED"
  | "DISPATCH_FAILED"
  | "DEAD_LETTERED"
  | "CANCELLED";
export type PassStatus = "PASSED" | "FAILED" | "UNAVAILABLE";
export type PolicyEffect = "ALLOW" | "REQUIRE_REVIEW" | "DENY";
export type ToolActionStatus =
  | "PROPOSED"
  | "AUTHORIZED"
  | "DENIED"
  | "EXECUTING"
  | "SUCCEEDED"
  | "FAILED"
  | "UNKNOWN";
export type HumanAction = "APPROVE" | "EDIT" | "REJECT" | "OVERRIDE" | "CLARIFY" | "ESCALATE" | "REROUTE";
export type ActorType = "HUMAN" | "SERVICE" | "MODEL" | "SYSTEM";
export type OutcomeDisposition = "RESOLVED" | "CLARIFIED" | "ESCALATED" | "REJECTED" | "NO_ACTION";
export type ReceiptStatus = "ACCEPTED" | "DELIVERED" | "FAILED" | "UNKNOWN";
export type EvidenceCoverage = "SUFFICIENT" | "PARTIAL" | "NONE" | "CONFLICTED";
export type EnvironmentName = "local" | "development" | "staging" | "production";
export type SourceDocumentStatus = "APPROVED" | "DEPRECATED" | "REMOVED" | "DRAFT";
export type CanonicalBlockType = "paragraph" | "ordered_steps" | "warning" | "table" | "link";
export type CorpusPublicationStatus = "UNPUBLISHED" | "APPROVED";

export interface VersionedContract {
  readonly schema_version: string;
}

export interface ContextualDomainContract extends VersionedContract {
  readonly tenant_id: string;
  readonly application_id: string;
}

export interface RunContextDomainContract extends ContextualDomainContract {
  readonly case_id: string;
  readonly run_id: string;
}

export interface CompatibilityTuple extends VersionedContract {
  readonly runtime_version: string;
  readonly application_package_version: string;
  readonly workflow_version: string;
  readonly corpus_version: string;
  readonly policy_version: string;
  readonly model_profile_version: string;
  readonly adapter_versions: readonly string[];
}

export interface SupportCase extends ContextualDomainContract {
  readonly case_id: string;
  readonly channel: string;
  readonly external_thread_ref: string | null;
  readonly requester_ref: string;
  readonly state: CaseState;
  readonly version: number;
  readonly active_run_id: string | null;
  readonly category: string | null;
  readonly risk_flags: readonly string[];
  readonly route: string | null;
  readonly created_at: Iso8601Timestamp;
  readonly updated_at: Iso8601Timestamp;
  readonly closed_at: Iso8601Timestamp | null;
}

export interface RequestRun extends ContextualDomainContract {
  readonly run_id: string;
  readonly case_id: string;
  readonly run_number: number;
  readonly trigger: string;
  readonly environment: EnvironmentName;
  readonly compatibility: CompatibilityTuple;
  readonly status: RunStatus;
  readonly started_at: Iso8601Timestamp;
  readonly completed_at: Iso8601Timestamp | null;
  readonly failure_class: string | null;
}

export interface SourceLink extends VersionedContract {
  readonly label: string;
  readonly url: string;
}

export interface CanonicalBlock extends VersionedContract {
  readonly block_id: string;
  readonly block_type: CanonicalBlockType;
  readonly heading_path: readonly string[];
  readonly ordinal: number;
  readonly text: string;
  readonly links: readonly SourceLink[];
  readonly source_locator: string;
}

export interface SourceDocument extends ContextualDomainContract {
  readonly document_id: string;
  readonly canonical_url: string;
  readonly title: string;
  readonly product: string;
  readonly category: string;
  readonly language: string;
  readonly owner: string;
  readonly status: SourceDocumentStatus;
  readonly effective_from: Iso8601Timestamp | null;
  readonly effective_to: Iso8601Timestamp | null;
  readonly current_version_id: string | null;
}

export interface SourceDocumentVersion extends ContextualDomainContract {
  readonly version_id: string;
  readonly document_id: string;
  readonly content_hash: string;
  readonly raw_snapshot_ref: string;
  readonly blocks: readonly CanonicalBlock[];
  readonly generated_markdown_ref: string;
  readonly structural_diff_ref: string;
  readonly links: readonly SourceLink[];
  readonly fetched_at: Iso8601Timestamp;
  readonly published_at: Iso8601Timestamp | null;
  readonly parser_version: string;
}

export interface DocumentChunk extends ContextualDomainContract {
  readonly chunk_id: string;
  readonly document_version_id: string;
  readonly ordinal: number;
  readonly heading_path: readonly string[];
  readonly block_ids: readonly string[];
  readonly block_types: readonly CanonicalBlockType[];
  readonly text: string;
  readonly locator: string;
  readonly canonical_url: string;
  readonly chunk_hash: string;
  readonly embedding_version: string;
}

export interface CorpusVersion extends ContextualDomainContract {
  readonly corpus_version: string;
  readonly document_version_ids: readonly string[];
  readonly parser_version: string;
  readonly chunker_version: string;
  readonly embedding_version: string;
  readonly validation_report_ref: string;
  readonly structural_diff_ref: string;
  readonly approval_actor: string | null;
  readonly approved_at: Iso8601Timestamp | null;
  readonly publication_status: CorpusPublicationStatus;
}

export interface SourceSpan extends VersionedContract {
  readonly span_id: string;
  readonly document_version_id: string;
  readonly chunk_id: string;
  readonly heading_path: readonly string[];
  readonly canonical_url: string;
  readonly quote: string;
}

export interface EvidenceIntent extends VersionedContract {
  readonly intent_id: string;
  readonly normalized_intent: string;
  readonly coverage: EvidenceCoverage;
  readonly source_spans: readonly SourceSpan[];
  readonly missing_requirements: readonly string[];
  readonly conflicts: readonly string[];
}

export interface RetrievalTrace extends VersionedContract {
  readonly queries: readonly string[];
  readonly candidate_ids: readonly string[];
  readonly ranking_version: string;
  readonly embedding_version: string;
  readonly latency_ms: number;
}

export interface EvidencePacket extends RunContextDomainContract {
  readonly packet_id: string;
  readonly corpus_version: string;
  readonly intents: readonly EvidenceIntent[];
  readonly retrieval_trace: RetrievalTrace;
}

export interface IntentResolution extends VersionedContract {
  readonly intent_id: string;
  readonly state: ResolutionType;
  readonly evidence_span_ids: readonly string[];
  readonly unresolved_requirements: readonly string[];
}

export interface ResolutionDecision extends RunContextDomainContract {
  readonly decision_id: string;
  readonly evidence_packet_id: string | null;
  readonly state: ResolutionType;
  readonly per_intent: readonly IntentResolution[];
  readonly allowed_response_scope: readonly string[];
  readonly unresolved_questions: readonly string[];
  readonly proposed_response: string | null;
  readonly rationale_codes: readonly string[];
}

export interface VerificationResult extends RunContextDomainContract {
  readonly verification_id: string;
  readonly checks: Readonly<Record<string, PassStatus>>;
  readonly claims: readonly string[];
  readonly support_mappings: Readonly<Record<string, readonly string[]>>;
  readonly procedure_checks: readonly string[];
  readonly conflicts: readonly string[];
  readonly unsupported_claims: readonly string[];
  readonly pass_status: PassStatus;
  readonly verifier_version: string;
}

export interface PolicyDecision extends RunContextDomainContract {
  readonly policy_decision_id: string;
  readonly policy_version: string;
  readonly evaluated_rules: readonly string[];
  readonly effect: PolicyEffect;
  readonly reason_codes: readonly string[];
  readonly decided_at: Iso8601Timestamp;
}

export interface DispatchDecision extends RunContextDomainContract {
  readonly decision_id: string;
  readonly outcome: DispatchMode;
  readonly reason_codes: readonly string[];
  readonly policy_decision_id: string;
  readonly policy_version: string;
  readonly verification_result_id: string;
  readonly reviewer_required: boolean;
}

export interface RoutingDecision extends RunContextDomainContract {
  readonly decision_id: string;
  readonly route_type: RouteType;
  readonly queue_id: string | null;
  readonly team_id: string | null;
  readonly owner_id: string | null;
  readonly reason_codes: readonly string[];
  readonly service_target: string | null;
  readonly policy_version: string;
}

export interface ToolAuthorization extends VersionedContract {
  readonly actor_type: ActorType;
  readonly actor_ref: string;
  readonly capability: string;
  readonly grant_id: string;
}

export interface ToolDryRun extends VersionedContract {
  readonly status: PassStatus;
  readonly validated_at: Iso8601Timestamp;
}

export interface ToolReceipt extends VersionedContract {
  readonly request_id: string;
  readonly status: ReceiptStatus;
  readonly failure_code: string | null;
  readonly reconciled_at: Iso8601Timestamp | null;
}

export interface ToolAction extends RunContextDomainContract {
  readonly action_id: string;
  readonly tool_type: string;
  readonly tool_version: string;
  readonly typed_input: Readonly<Record<string, unknown>>;
  readonly authorization: ToolAuthorization;
  readonly policy_decision_id: string;
  readonly policy_version: string;
  readonly dry_run: ToolDryRun;
  readonly idempotency_key: string;
  readonly status: ToolActionStatus;
  readonly attempts: number;
  readonly receipt: ToolReceipt | null;
}

export interface EnvironmentConfig extends VersionedContract {
  readonly environment: EnvironmentName;
  readonly tenant_id: string;
  readonly application_id: string;
  readonly deployment_target: string;
  readonly provider_profile_refs: readonly string[];
  readonly external_side_effects_enabled: boolean;
  readonly approved_test_recipient_refs: readonly string[];
}

export interface HumanDecision extends RunContextDomainContract {
  readonly decision_id: string;
  readonly actor_id: string;
  readonly action: HumanAction;
  readonly expected_case_version: number;
  readonly reason_code: string;
  readonly structured_changes: Readonly<Record<string, unknown>>;
  readonly text_diff: string | null;
  readonly decided_at: Iso8601Timestamp;
}

export interface AuditEvent extends RunContextDomainContract {
  readonly event_id: string;
  readonly sequence: number;
  readonly actor_type: ActorType;
  readonly actor_ref: string;
  readonly event_type: string;
  readonly payload: Readonly<Record<string, unknown>>;
  readonly payload_hash: string;
  readonly occurred_at: Iso8601Timestamp;
  readonly recorded_at: Iso8601Timestamp;
}

export interface FinalOutcome extends RunContextDomainContract {
  readonly outcome_id: string;
  readonly disposition: OutcomeDisposition;
  readonly dispatch_status: ReceiptStatus;
  readonly external_refs: readonly string[];
  readonly close_reason: string;
  readonly timing_summary: Readonly<Record<string, number>>;
  readonly quality_flags: readonly string[];
}

export interface FeedbackEvent extends ContextualDomainContract {
  readonly feedback_id: string;
  readonly case_id: string;
  readonly source: string;
  readonly rating: number | null;
  readonly feedback_type: string | null;
  readonly comment: string;
  readonly received_at: Iso8601Timestamp;
}

export interface ReopenEvent extends ContextualDomainContract {
  readonly reopen_id: string;
  readonly case_id: string;
  readonly prior_outcome_id: string;
  readonly reason: string;
  readonly new_message_or_event_ref: string;
  readonly reopened_at: Iso8601Timestamp;
  readonly new_run_id: string;
}
