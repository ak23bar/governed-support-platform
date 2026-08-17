from enum import StrEnum


class StrictEnum(StrEnum):
    """String enum whose constructor rejects every unknown value."""


class ResolutionType(StrictEnum):
    RESOLVE = "RESOLVE"
    CLARIFY = "CLARIFY"
    ESCALATE = "ESCALATE"
    REJECT = "REJECT"
    NO_ACTION = "NO_ACTION"


class DispatchMode(StrictEnum):
    AUTOMATIC = "AUTOMATIC"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"
    DENIED = "DENIED"


class RouteType(StrictEnum):
    NONE = "NONE"
    CENTRAL = "CENTRAL"
    LEVEL_1 = "LEVEL_1"
    LEVEL_2 = "LEVEL_2"
    SPECIALIST = "SPECIALIST"
    MANAGER = "MANAGER"


class CaseState(StrictEnum):
    RECEIVED = "RECEIVED"
    PROCESSING = "PROCESSING"
    AWAITING_CLARIFICATION = "AWAITING_CLARIFICATION"
    AWAITING_REVIEW = "AWAITING_REVIEW"
    ROUTED = "ROUTED"
    DISPATCH_PENDING = "DISPATCH_PENDING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    FAILED = "FAILED"


class RunStatus(StrictEnum):
    RECEIVED = "RECEIVED"
    NORMALIZED = "NORMALIZED"
    CLASSIFIED = "CLASSIFIED"
    EVIDENCE_READY = "EVIDENCE_READY"
    RESOLUTION_PROPOSED = "RESOLUTION_PROPOSED"
    VERIFIED = "VERIFIED"
    DISPATCH_DECIDED = "DISPATCH_DECIDED"
    AWAITING_REVIEW = "AWAITING_REVIEW"
    APPROVED = "APPROVED"
    EDITED = "EDITED"
    CLARIFICATION_REQUESTED = "CLARIFICATION_REQUESTED"
    ESCALATED = "ESCALATED"
    REJECTED = "REJECTED"
    REROUTED = "REROUTED"
    AUTO_DISPATCHED = "AUTO_DISPATCHED"
    DISPATCHED = "DISPATCHED"
    CLOSED = "CLOSED"
    INTAKE_REJECTED = "INTAKE_REJECTED"
    PROCESSING_FAILED = "PROCESSING_FAILED"
    ACTION_FAILED = "ACTION_FAILED"
    DISPATCH_FAILED = "DISPATCH_FAILED"
    DEAD_LETTERED = "DEAD_LETTERED"
    CANCELLED = "CANCELLED"


class PassStatus(StrictEnum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    UNAVAILABLE = "UNAVAILABLE"


class PolicyEffect(StrictEnum):
    ALLOW = "ALLOW"
    REQUIRE_REVIEW = "REQUIRE_REVIEW"
    DENY = "DENY"


class ToolActionStatus(StrictEnum):
    PROPOSED = "PROPOSED"
    AUTHORIZED = "AUTHORIZED"
    DENIED = "DENIED"
    EXECUTING = "EXECUTING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class HumanAction(StrictEnum):
    APPROVE = "APPROVE"
    EDIT = "EDIT"
    REJECT = "REJECT"
    OVERRIDE = "OVERRIDE"
    CLARIFY = "CLARIFY"
    ESCALATE = "ESCALATE"
    REROUTE = "REROUTE"


class ActorType(StrictEnum):
    HUMAN = "HUMAN"
    SERVICE = "SERVICE"
    MODEL = "MODEL"
    SYSTEM = "SYSTEM"


class OutcomeDisposition(StrictEnum):
    RESOLVED = "RESOLVED"
    CLARIFIED = "CLARIFIED"
    ESCALATED = "ESCALATED"
    REJECTED = "REJECTED"
    NO_ACTION = "NO_ACTION"


class ReceiptStatus(StrictEnum):
    ACCEPTED = "ACCEPTED"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class EvidenceCoverage(StrictEnum):
    SUFFICIENT = "SUFFICIENT"
    PARTIAL = "PARTIAL"
    NONE = "NONE"
    CONFLICTED = "CONFLICTED"


class EnvironmentName(StrictEnum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class SourceDocumentStatus(StrictEnum):
    APPROVED = "APPROVED"
    DEPRECATED = "DEPRECATED"
    REMOVED = "REMOVED"
    DRAFT = "DRAFT"


class CanonicalBlockType(StrictEnum):
    PARAGRAPH = "paragraph"
    ORDERED_STEPS = "ordered_steps"
    WARNING = "warning"
    TABLE = "table"
    LINK = "link"


class CorpusPublicationStatus(StrictEnum):
    UNPUBLISHED = "UNPUBLISHED"
    APPROVED = "APPROVED"
