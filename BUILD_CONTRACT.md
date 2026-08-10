# GPS / MOHID V1 Build Contract

**Status:** Active execution contract for the frozen V1 baseline

**Derived from:** Governed Support Automation Platform Living Reference v1.5 and MOHID Problem and First Implementation Living Specification v0.6

**Authority:** This file is a non-authoritative implementation derivative. If it conflicts with either living PDF, the living PDFs control. Do not use this file to revise, reinterpret, or bypass them.

## 1. Product and current objective

GPS is the Governed Platform for Support: a configurable governed-support platform that converts approved organizational knowledge into evidence-backed support decisions, determines whether a proposed action may execute, routes uncertain or restricted cases to humans, and preserves one auditable Support Case record across automated and human work.

GPS is not a generic chatbot, unrestricted agent framework, replacement help desk, universal connector platform, generic MCP platform, or autonomous decision-maker.

MOHID Support Automation V1 is the first reference implementation and the current execution priority. Its canonical objective is to test whether MOHID's authoritative HelpDocs can support governed automation of repetitive support requests while uncertain or restricted cases route to the appropriate humans and the full case lifecycle remains reconstructable.

The proof sequence is fixed:

1. **mTAP:** first bounded technical and operational proof using Fahad's real regression cases.
2. **KIOSK:** first reuse test after the mTAP acceptance gate passes, without rewriting the canonical runtime lifecycle.

General GPS architecture work must not delay the active MOHID gate unless a platform-level defect directly blocks implementation.

## 2. Repository strategy

Create a new repository for GPS and MOHID V1. Keep `legacy-prototype-v1` read-only as a historical baseline, regression-fixture source, and record of earlier behavior.

Only deliberately reviewed, redacted, and provenance-recorded assets may be ported. Do not transplant legacy architecture into the new core. ADR-0001 records the allowed and prohibited reuse boundary.

The frozen living PDFs and this derivative packet belong in the new repository. Coding agents must never edit the frozen PDFs. Any material specification change returns to the product owner and requires a versioned living-document revision outside an implementation shortcut.

## 3. Current execution boundary: Package A

Package A establishes the baseline and knowledge compiler. It contains three ordered epics.

### E01 - Repository, CI, domain contracts, and provider fakes

Establish the repository and package structure, Python project tooling, versioned domain schemas and enums, semantic provider protocols, contract-compliant fakes, test structure, local PostgreSQL development setup, a migration-framework shell, CI, formatting, linting, static typing, secret scanning, dependency checks, `.env.example`, one-command local bootstrap, and acceptance-test shells for E02 and E03.

E01 does not implement provider-backed behavior. Its exit gate is a fresh checkout that can be set up and exercised with one documented command and whose required CI checks are green.

### E02 - PostgreSQL Support Case, Request Run, and audit persistence

Make Support Case, Request Run, state transitions, and ordered Audit Events durable in PostgreSQL. Add migrations, repositories, manual intake, optimistic concurrency, append-only audit behavior, and a transactional-outbox shell.

The E02 exit gate requires idempotent intake; case and run survival across restart; safe concurrent-write conflicts; an ordered event for every transition; and reconstruction of an authorized tenant-scoped dry-run case.

### E03 - mTAP HelpDocs knowledge compiler and corpus publication

Build the structure-preserving knowledge compiler using a fake and an approved HTML/fixture-backed `KnowledgeSourceProvider`. Preserve raw snapshots, canonical structured blocks, deterministic Markdown, hashes, structural diffs, versioned chunks, controlled publication, approval, and sync reporting.

An official HelpDocs API or export is not an E03 prerequisite. The E03 exit gate requires the shared source-provider contract suite to pass; five golden mTAP pages to preserve material structure; unchanged synchronization to be idempotent; changed, removed, deprecated, redirected, and failed-fetch behavior to be safe; and every published chunk to trace to its canonical block, document version, and URL.

Package B and Package C remain later milestones. Do not decompose or implement them merely to make Package A look complete.

## 4. Mandatory domain boundaries

The durable unit of truth is the **Support Case**. A case may contain multiple immutable, version-pinned **Request Runs**. Runs never overwrite one another.

The core must preserve separate typed contracts for:

- evidence and source provenance;
- resolution: `RESOLVE`, `CLARIFY`, `ESCALATE`, `REJECT`, or `NO_ACTION`;
- dispatch: `AUTOMATIC`, `HUMAN_APPROVAL`, or `DENIED`;
- routing: ownership independent of resolution and dispatch;
- verification and deterministic policy;
- tool intent, authorization, execution, idempotency, receipt, and reconciliation;
- attributable human decisions;
- append-only, ordered Audit Events; and
- final outcome, feedback, and reopening.

Customer-facing text is never the sole representation of a decision. Unknown enum values and incompatible versions fail closed.

The runtime/application boundary is mandatory:

- The **shared governed runtime** owns lifecycle execution, case/run state, provider invocation, retrieval and verification mechanics, the policy floor, permissions, tool authorization and idempotency, secrets, audit, retries, recovery, and kill switches.
- The **versioned MOHID application package** declares approved knowledge, terminology, taxonomy, routing, templates, category autonomy, permitted capabilities within the platform floor, provider-profile references, and evaluation cases.
- The application package contains no credentials, provider SDKs, arbitrary executable workflow code, or replacement policy gate.
- Every Request Run pins an immutable compatibility tuple covering runtime, application package, workflow, corpus, policy, model profile, and adapter versions. Missing or incompatible versions fail closed; configuration changes affect only later runs.

The knowledge boundary is also mandatory:

```text
approved source -> raw snapshot -> canonical structured block tree
canonical block tree -> generated review artifact + reproducible search projections
```

Generated Markdown and embeddings are derivatives. Neither may replace the canonical blocks or erase headings, procedures, prerequisites, warnings, tables, links, ordering, versions, locators, or provenance.

## 5. Governance invariants

All implementation must preserve these rules:

1. Every meaningful request becomes a durable Support Case.
2. Evidence precedes substantive resolution or consequential action.
3. Retrieval score is not factual confidence and never authorizes dispatch by itself.
4. Resolution, dispatch, and routing remain independently stored and queryable.
5. Models may propose; deterministic runtime code validates, authorizes, executes, and records.
6. Missing evidence, conflicts, failed or unavailable verification, provider failure, policy uncertainty, failed persistence, unavailable authority, or kill-switch activation reduces autonomy.
7. Clarification, escalation, rejection, and no action are valid successful outcomes.
8. Every side effect requires a durable intent and idempotency key before execution.
9. Failed or ambiguous tool and delivery receipts remain open for reconciliation; they never silently become success.
10. Every consequential AI action, human decision, tool result, timing interval, and final outcome remains reconstructable.
11. Human edits are attributable and version-checked; substantive edits return to verification.
12. Gold evaluation outcomes cannot change without explicit product-owner approval and a recorded dataset revision.
13. Objective timing may be recorded, but employee intent or motive must never be inferred.
14. Tenant knowledge, policy, data, permissions, and search namespaces remain isolated.

## 6. Provider and protocol rules

The product owns semantic capability contracts. Provider SDKs and transport payloads stay inside adapters.

E01 must define the seams needed by the frozen specification, including:

- `ModelProvider`
- `EmbeddingProvider`
- `VectorStore`
- `ObjectStore`
- `CaseRepository`
- `KnowledgeSourceProvider`
- deferred `KnowledgeQueryProvider`
- `InboundMessageProvider`
- `OutboundMessageProvider`
- `ToolExecutor`
- `EventPublisher`
- `IdentityProvider`

For each active boundary:

- create a local fake and contract tests before a live adapter;
- implement only the approved provider needed for the current issue;
- run the same semantic contract suite against the fake and approved adapter;
- keep provider SDKs, credentials, response bodies, and protocol-specific objects out of domain contracts;
- do not build parallel real providers for theoretical portability;
- do not add an implicit runtime fallback chain; and
- do not claim an integration passes when only its fake passes.

REST, SDK, export, crawler, webhook, database, direct adapter, and MCP-backed adapter are replaceable mechanisms beneath semantic contracts. MCP is optional and deferred for the mTAP proof. It is not the runtime abstraction, business policy, authorization layer, or an E01 requirement.

## 7. External-action prohibition

E01 and E02 run locally with synthetic or redacted data and fakes. They must have no network side effects.

Historical replay and acceptance shells are side-effect free. Package A performs no customer-facing send and enables no automatic dispatch.

Later Package C testing may use only explicitly approved test inputs and recipients in an authorized sandbox. No customer-facing action or automatic dispatch is permitted until the required offline replay, shadow mode, universal human approval, category-specific release gate, and explicit product-owner/MOHID approvals have passed.

Never commit credentials or create a code path that can silently activate a development shortcut in staging or production.

## 8. Explicit V1 non-scope

Do not add any of the following to satisfy Package A:

- voice, mobile, or kiosk integration;
- broad self-service multi-tenancy or second-tenant productization;
- connector marketplaces or arbitrary no-code workflow execution;
- generic MCP infrastructure, MCP hosting, discovery, or administration;
- live runtime HelpDocs querying or HelpDocs write-back/publication;
- generalized CRM or help-desk replacement;
- unrestricted arbitrary-API access;
- multiple production providers per boundary;
- model fallback chains;
- multi-agent supervisor systems;
- employee scoring, leaderboards, or motive inference;
- billing, licensing, or commercial packaging;
- destructive or privileged autonomous account actions;
- Kubernetes or speculative enterprise-scale infrastructure;
- a complete policy engine, SON, retrieval, embeddings, Office 365, Mandrill, Gemini production access, or automatic dispatch inside E01.

## 9. Test and acceptance-gate doctrine

Implementation begins from a failing acceptance, regression, or provider-contract test that expresses the issue's required behavior.

Use the smallest relevant ladder:

1. unit tests for deterministic domain invariants;
2. provider-contract tests for fakes and any authorized adapter;
3. integration tests for PostgreSQL, transactions, recovery, and later boundary composition;
4. regression/replay tests for historical MOHID failures;
5. security tests for tenant isolation, permissions, redaction, secrets, and untrusted inputs;
6. evaluation tests for fixed expected outcomes; and
7. end-to-end tests only in an authorized environment with external actions constrained by the rollout stage.

Do not weaken, skip, delete, or rewrite a test merely to make CI pass. Do not silently change gold outcomes. A local green run is evidence, not a substitute for GitHub Actions. GitHub Actions is the authoritative automated merge gate.

E01 is accepted only when a clean checkout can use the documented bootstrap command and all required formatting, linting, typing, unit, contract, integration-shell, security, secret, dependency, and repository checks are green.

## 10. Decision discipline

Do not silently convert an unresolved detail into architecture.

- A durable implementation choice belongs in a **repository ADR**.
- A performance-sensitive choice belongs in a measured **implementation experiment**.
- Legitimate future work belongs in the **backlog**.
- Provider access, source approval, routing ownership, retention, adjudication, or operational authority belongs in a **client-gated decision**.
- A change to a frozen platform invariant or MOHID requirement returns to the **living specification owner**.

## 11. Agent stop and escalation rules

Stop work on the affected scope and report the issue when:

- the assigned issue or acceptance criteria are ambiguous;
- the two living PDFs appear to conflict;
- implementation would require editing a frozen PDF or weakening a platform invariant;
- a proposed shortcut collapses runtime, application, or provider boundaries;
- a gold outcome or benchmark label appears wrong;
- a required test can pass only by reducing its protection;
- work requires live credentials, unapproved data, recipients, or external side effects;
- a client-gated dependency blocks the claimed acceptance criterion;
- an unrequested provider, MCP layer, framework, or infrastructure expansion appears necessary;
- the change crosses into another issue, epic, or branch; or
- persistence, verification, authorization, audit, or recovery cannot fail closed.

The report must name the exact contradiction or missing decision, the affected acceptance criterion, the safest state the system can maintain, and the smallest owner decision needed. Continue only on independent in-scope work whose acceptance claim remains honest.
