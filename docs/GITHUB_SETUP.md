# GitHub Planning and Bootstrap Guide

**Derived from:** Governed Support Automation Platform Living Reference v1.5 and MOHID Problem and First Implementation Living Specification v0.6

**Authority:** This file is a non-authoritative implementation derivative. If it conflicts with either living PDF, the living PDFs control. GitHub metadata must not create product requirements beyond the frozen specifications.

## 1. Bootstrap order

1. Create the new repository, recommended name `governed-support-platform`.
2. Commit the two frozen living PDFs, this execution packet, and no application implementation.
3. Record ADR-0001 as Accepted.
4. Tag the frozen Platform v1.5 / MOHID v0.6 specification baseline.
5. Create the milestones, labels, and project board below.
6. Create E01, E02, and E03 from the issue bodies below.
7. Put E01 in **Ready**; leave E02 and E03 in **Backlog** until their dependencies pass.
8. Open one E01 branch with Codex as primary implementer and ChatGPT Project as independent reviewer; the user retains merge authority.
9. Merge only after E01's clean-checkout GitHub Actions gate is green.

The exact default-branch protection settings and baseline-tag spelling are repository conventions to settle during bootstrap. A suggested tag is `spec-baseline-platform-v1.5-mohid-v0.6`; record the chosen value in `docs/STATUS.md`.

## 2. Initial milestones

| Milestone | Current scope | Planning rule |
| --- | --- | --- |
| **Package A - Foundation and Knowledge Compiler** | E01-E03: repository/contracts/fakes, durable case/audit persistence, and versioned mTAP knowledge compiler | Active execution focus; decompose only as each bounded issue is activated |
| **Package B - Retrieval and Governed Decisions** | Evaluated retrieval, Evidence Packets, typed decisions, verification, and policy | Keep milestone-level only until Package A evidence is sufficient |
| **Package C - SON and Company Integrations** | SON review, human decisions, Office 365 test intake, Mandrill approved-test delivery, and receipt reconciliation | Keep milestone-level only; client access remains a named dependency |

Do not fully decompose Packages B and C during repository bootstrap.

### Package A milestone exit gate

Package A closes only when:

- a clean checkout runs through the documented bootstrap;
- the MOHID application package validates and hydrates;
- cases and Request Runs survive restart with ordered audit history;
- ten approved redacted regression fixtures enter idempotently;
- fake and approved HTML/fixture source adapters pass the same contract suite;
- roughly 8-15 approved mTAP pages, with the final count set by the real category boundary, form one versioned corpus;
- unchanged synchronization is idempotent;
- five golden pages preserve every material instruction, warning, ordering relation, link, and heading;
- every generated chunk traces to a canonical block, document version, exact URL, and content hash; and
- corpus publication records validation, structural review, and knowledge-owner approval.

If approved pages, fixtures, or an approver are missing, local compiler work may continue, but the milestone remains blocked for the affected publication claim.

## 3. Recommended labels

| Label | Use |
| --- | --- |
| `package:A` | Package A work |
| `package:B` | Package B work |
| `package:C` | Package C work |
| `epic:E01` | Repository, CI, contracts, and fakes |
| `epic:E02` | Case/run/audit persistence |
| `epic:E03` | HelpDocs knowledge compiler |
| `type:contract` | Schema, protocol, or invariant |
| `type:test` | Test harness, fixture, or quality gate |
| `type:persistence` | Database, migration, repository, concurrency, or outbox |
| `type:knowledge` | Source acquisition, compilation, versioning, or corpus publication |
| `type:decision` | ADR, policy decision, or owner adjudication |
| `blocked:client` | Requires client access, approval, data, or owner |
| `blocked:decision` | Requires an unresolved product or repository decision |
| `agent:codex` | Codex is the primary implementer or assigned reviewer |
| `agent:claude` | Claude Code is the primary implementer |
| `priority:blocker` | Blocks the active acceptance gate |
| `priority:high` | High priority inside the active package |

Apply only labels that describe the current issue. A label does not authorize work outside the issue body.

## 4. Project board

Create these columns:

1. **Backlog**
2. **Ready**
3. **In Progress**
4. **Review**
5. **Blocked**
6. **Done**

Movement rules:

- **Ready:** dependencies and acceptance criteria are clear.
- **In Progress:** one primary implementer and branch are active.
- **Review:** implementation is complete enough for independent review; required CI may still be running.
- **Blocked:** the exact missing dependency and owner are recorded.
- **Done:** acceptance evidence exists, required GitHub Actions checks are green, review is complete, and the user has accepted/merged the work.

## 5. Initial issue: E01

### Title

`[E01] Repository, CI, Domain Contracts, and Provider Fakes`

### Labels

`package:A`, `epic:E01`, `type:contract`, `type:test`, `agent:codex`, `priority:blocker`

### Specification references

- Platform v1.5: Sections 6, 10-12, and 14-15.
- MOHID v0.6: Sections 2.1, 7-9, 18, 20.1 E01, 21, and 24.
- `BUILD_CONTRACT.md`
- ADR-0001

### Active package and epic

- Package: A - Foundation and Knowledge Compiler
- Epic: E01

### Deliverable

A new-repository scaffold that establishes versioned domain language, semantic provider seams and fakes, local development/test infrastructure, and objective CI without implementing provider-backed product behavior.

### In scope

- repository and package structure aligned to MOHID v0.6;
- Python project tooling;
- domain schemas and enums for case/run, evidence, resolution, verification, policy, dispatch, routing, tool action, human decision, audit event, and outcome boundaries;
- explicit application-package schema/validation shell and compatibility-tuple contract;
- semantic provider protocols listed in `BUILD_CONTRACT.md`;
- contract-compliant local fakes, including `KnowledgeSourceProvider` and the deferred `KnowledgeQueryProvider` seam;
- test directories and fixtures;
- local PostgreSQL development setup;
- migration-framework shell without E02 business migrations;
- CI for formatting, linting, static typing, unit/contract/integration-shell checks, secret scanning, and dependency/license checks;
- `.env.example` with no secrets;
- one documented local bootstrap command; and
- failing or pending acceptance-test shells for E02 persistence and E03 knowledge compilation.

### Explicit out of scope

- HelpDocs parsing or production acquisition logic;
- corpus publication behavior;
- retrieval, embeddings, pgvector behavior, or evidence construction;
- generic MCP infrastructure or a production MCP server;
- live Gemini/GCP access;
- Office 365 or Mandrill adapters;
- model fallback chains;
- policy implementation beyond contract shells;
- tool execution or automatic dispatch;
- SON;
- voice, mobile, or kiosk integration; and
- Packages B or C implementation.

### Dependencies

- frozen Platform v1.5 and MOHID v0.6;
- approved new-repository decision in ADR-0001;
- repository creation and branch access.

Client provider access is not required for the E01 local scaffold.

### Acceptance criteria

- A fresh checkout can be set up and exercise the API/test services with one documented command.
- Required domain schemas and enums validate and reject unknown values.
- Resolution, dispatch, and routing remain separate typed contracts.
- Support Case and immutable Request Run version contexts are represented.
- The MOHID application package can be validated/hydrated into an immutable compatibility-tuple representation without credentials or executable workflow code.
- Each provider fake passes its semantic contract suite.
- No provider SDK or transport-specific object enters domain contracts.
- E02 and E03 acceptance-test shells exist and fail/skip only for an explicit unimplemented boundary, not due to a broken harness.
- Formatting, linting, typing, unit, contract, integration-shell, secret, dependency, and license checks run in GitHub Actions.
- No network side effect or live credential is required.
- GitHub Actions is green from a clean checkout.

### Required tests

- schema serialization/round trip;
- invalid and unknown enum rejection;
- compatibility-tuple validation;
- application-package policy-floor negative fixture;
- fake-provider contract suites;
- tenant/context isolation fixtures at contract boundaries;
- E02 and E03 acceptance shells;
- secret scan;
- dependency and license checks; and
- clean bootstrap smoke test.

### Primary implementer

Codex.

### Reviewer

ChatGPT Project. The user remains merge authority.

### Definition of done

One documented command initializes the clean checkout and runs or starts the required local services; versioned contracts and fakes are the single language later epics reference; all required GitHub Actions checks are green; review finds no architecture drift; `docs/STATUS.md` records the accepted commit/PR and next E02 criterion.

## 6. Initial issue: E02

### Title

`[E02] PostgreSQL Support Case, Request Run, and Audit Persistence`

### Labels

`package:A`, `epic:E02`, `type:persistence`, `type:test`, `agent:claude`, `priority:high`

### Specification references

- Platform v1.5: Sections 6, 8-12.
- MOHID v0.6: Sections 7, 8, 14, 18.3, 20.1 E02, 21, and 24.
- `BUILD_CONTRACT.md`
- accepted E01 contracts.

### Active package and epic

- Package: A - Foundation and Knowledge Compiler
- Epic: E02

### Deliverable

Durable PostgreSQL persistence for Support Case, immutable Request Run, state transitions, and ordered append-only Audit Events, with idempotent manual intake, optimistic concurrency, and a transactional-outbox shell.

### In scope

- versioned migrations for the bounded E02 table set;
- repositories conforming to accepted E01 contracts;
- idempotent manual intake;
- tenant/application-scoped access;
- immutable Request Run version tuple;
- compare-and-swap case transitions;
- ordered append-only Audit Events and payload hashes;
- atomic state/event behavior where required;
- transaction rollback and restart reconstruction;
- transactional-outbox shell without live execution; and
- a no-action dry-run persistence path.

### Explicit out of scope

- HelpDocs compiler or corpus tables beyond an explicitly required shared migration seam;
- retrieval, embeddings, evidence, model calls, verification, or policy behavior;
- external tools, Office 365, Mandrill, or live providers;
- automatic dispatch;
- full SON;
- all later E02 table families in one issue unless separately approved; and
- E03 or Package B implementation.

### Dependencies

- E01 accepted with clean-checkout GitHub Actions green.
- Local disposable PostgreSQL/testcontainers path.
- A production PostgreSQL target is client-gated and not required for local E02 contract acceptance; production-readiness claims remain blocked without it.

### Acceptance criteria

- Duplicate intake is idempotent.
- A Support Case and Request Run survive restart.
- Request Run configuration/version bindings cannot be mutated in place.
- Concurrent writes using stale case versions fail safely.
- Every valid transition creates an ordered Audit Event.
- Required state and event writes roll back together on failure.
- Audit history is append-only; corrections create later events.
- Cross-tenant reads/writes are denied.
- A manual case advances through a no-action dry run with no external side effect.
- The case and its runs/events can be reconstructed under authorized tenant context.
- Relevant CI checks are green.

### Required tests

- migration up/down in a disposable database;
- transaction rollback;
- idempotent duplicate intake;
- optimistic-concurrency conflict;
- cross-tenant negative access;
- Request Run immutability;
- Audit Event sequence and payload-hash checks;
- restart/reconstruction;
- outbox-shell durability without execution; and
- no-action dry-run acceptance test.

### Primary implementer

Claude Code, beginning from the first approved failing persistence test.

### Reviewer

Codex. The user remains merge authority.

### Definition of done

The bounded migration and repository behavior are reviewed; a manual case/run can be created, safely advanced, restarted, reconstructed, and queried with ordered audit history; all required tests and GitHub Actions checks pass; no external action path exists; `docs/STATUS.md` identifies the accepted gate and next E03 criterion.

## 7. Initial issue: E03

### Title

`[E03] mTAP HelpDocs Knowledge Compiler and Corpus Publication`

### Labels

`package:A`, `epic:E03`, `type:knowledge`, `type:contract`, `type:test`, `agent:claude`, `priority:high`

### Specification references

- Platform v1.5: Sections 10.1-10.3 and 11-14.
- MOHID v0.6: Sections 3.3, 9, 14, 18.2-18.5, 20.1 E03, 21.2, and 24.
- `BUILD_CONTRACT.md`
- accepted E01 contracts and E02 persistence behavior.

### Active package and epic

- Package: A - Foundation and Knowledge Compiler
- Epic: E03

### Deliverable

A deterministic, structure-preserving mTAP HelpDocs compiler that produces raw snapshots, canonical block trees, generated Markdown, reproducible search projections, structural diffs, approval records, immutable corpus versions, and machine-readable sync reports.

### In scope

- fake and approved HTML/fixture-backed `KnowledgeSourceProvider`;
- approved source discovery and bounded fetch behavior;
- raw snapshot metadata and hashes;
- boilerplate removal;
- canonical blocks preserving headings, lists, procedures, prerequisites, warnings, tables, links, ordinal, and source locator;
- deterministic Markdown generated from canonical blocks;
- structure-aware deterministic chunks generated from the same blocks;
- new/changed/unchanged/removed/deprecated/redirected/failed-fetch classification;
- structural diff;
- unpublished candidate and knowledge-owner-approved immutable corpus publication;
- rollback to a prior corpus version;
- five golden mTAP parser fixtures;
- approved mTAP page/fixture inventory; and
- sync report and audit records.

### Explicit out of scope

- live runtime HelpDocs querying;
- HelpDocs write-back, autonomous knowledge edits, or external publication;
- requiring an official HelpDocs API/export;
- generic MCP infrastructure or MCP-shaped domain contracts;
- embeddings or retrieval implementation beyond reproducible projection seams explicitly required by E03;
- model-authored canonical content;
- KIOSK or later category expansion;
- production-wide corpus migration; and
- Package B retrieval optimization.

### Dependencies

- E01 accepted.
- Bounded E02 persistence needed for document/corpus publication records.
- Approved mTAP HTML pages or fixtures and acquisition permission.
- Named knowledge owner/corpus approver for a production-candidate publication claim.

If source approval is missing, fixture-backed compiler work may continue, but production-candidate publication remains `blocked:client`. Official HelpDocs API/export access is not required.

### Acceptance criteria

- Fake and approved HTML/fixture source adapters pass one `KnowledgeSourceProvider` contract suite.
- Five golden mTAP pages preserve every material heading, list, procedure step/order, prerequisite, warning, table context, link, and source locator.
- Raw snapshot, canonical blocks, generated Markdown, and search projections remain linked and versioned.
- Markdown and chunks derive from the same canonical blocks and cannot disagree on instruction order or source identity.
- Every published chunk resolves to one exact canonical URL, document version, heading/block range, and content hash.
- Re-running unchanged input creates no duplicate document version or current chunk.
- Changed content replaces current projections only after validation and recorded approval.
- Removed/deprecated content cannot enter an automatic-dispatch Evidence Packet.
- Redirect relationships are preserved.
- A failed fetch cannot delete or replace the last good published version.
- Structural diffs classify material content, hierarchy, procedure, warning, link, and metadata changes.
- Publication creates one immutable corpus version with approval and sync report.
- Relevant GitHub Actions checks are green.

### Required tests

- source-provider contract suite;
- golden canonical JSON and Markdown fixtures;
- source-fidelity and ordering checks;
- boilerplate removal;
- redirect, removal, and deprecation behavior;
- partial-fetch failure;
- unchanged-sync idempotency;
- deterministic block/chunk identifiers and hashes;
- structural-diff classification;
- approval-required publication;
- corpus rollback; and
- exact source/locator round trip.

### Primary implementer

Claude Code.

### Reviewer

Codex. The user remains merge authority.

### Definition of done

A repeatable command builds a reviewable mTAP corpus candidate from approved fixtures/pages, records approval where authority exists, publishes one immutable version, safely handles change and failure cases, and explains every indexed chunk's origin. All required tests and GitHub Actions checks pass; any missing production source approval remains an explicit client blocker.

## 8. Required issue template

Use this body for every future issue:

```markdown
## Specification references
- Exact living-spec sections and controlling derivative/ADR.

## Active package and epic
- Package:
- Epic:

## Deliverable
- One observable product or engineering outcome.

## In scope
- Explicit allowed work.

## Explicit out of scope
- Explicit exclusions.

## Dependencies
- Prior issue, decision, credential, dataset, environment, or owner.

## Acceptance criteria
- Observable pass/fail statements.

## Required tests
- Unit, contract, integration, replay, security, evaluation, or end-to-end.

## Primary implementer
- One owner.

## Reviewer
- One independent reviewer. The user retains merge authority.

## Risks and failure behavior
- How the change fails closed and how recovery is represented.

## Evidence
- CI link, logs, migration output, replay report, screenshot, or other acceptance artifact.

## Definition of done
- Code reviewed, required tests and GitHub Actions green, status/ADR updated, evidence linked.
```

If an exact implementation detail is not settled by the living papers, identify it as a repository ADR, measured experiment, backlog item, or client-gated decision. Do not silently turn it into an acceptance requirement.
