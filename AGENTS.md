# Repository Instructions for Coding Agents

**Derived from:** Governed Support Automation Platform Living Reference v1.5 and MOHID Problem and First Implementation Living Specification v0.6

**Authority:** This file is a non-authoritative implementation derivative. If it conflicts with either living PDF, the living PDFs control. Coding agents must not edit the frozen PDFs or treat this file as a third architecture document.

## Mission

Build the smallest accepted MOHID V1 vertical slice inside the GPS governed-support boundaries. The current execution focus is Package A: E01, E02, and E03. mTAP is the first proof; KIOSK is blocked until the mTAP acceptance gate passes.

Default to execution against the active issue. Do not expand architecture to anticipate later products, providers, tenants, or channels.

## Required reading before work

Before changing files, read:

1. both frozen living specifications;
2. `BUILD_CONTRACT.md`;
3. `docs/STATUS.md`;
4. the active issue and its acceptance criteria; and
5. any accepted ADR directly governing the change.

Then state or verify:

- active package;
- active epic and issue;
- branch;
- primary implementer;
- reviewer;
- deliverable;
- explicit non-scope;
- required tests; and
- current blockers.

If any of these are missing or contradictory, stop and surface the gap before implementation.

## Ownership model

Use one issue, one branch, one primary implementer, one independent reviewer, and one human merge decision.

- **User:** product owner, architect, scope authority, expected-outcome authority, and merge authority.
- **Codex:** repository scaffolding, CI, bounded parallel work, tests, and independent PR review.
- **Claude Code:** primary implementation, debugging, integration, and refactoring after the E01 scaffold is accepted.
- **Gemini AI Pro:** external research, provider/GCP investigation, document-grounded analysis, and adversarial evaluation. Its output is advisory until reconciled.
- **Hermes:** deferred project-operations automation around proven commands and workflows; not part of the runtime or current critical path.
- **GitHub Actions:** authoritative automated quality and merge gate.

Do not have multiple primary implementers edit the same feature branch concurrently.

## Permanent implementation invariants

- Every meaningful request becomes a durable Support Case.
- A Support Case is the human-facing unit of truth; Request Runs are immutable, version-pinned attempts.
- Evidence precedes substantive resolution or consequential action.
- Retrieval score is not factual confidence.
- Resolution, dispatch, and routing are separate typed decisions.
- Models may propose; deterministic runtime code validates, authorizes, executes, and records.
- Unknown enum values, incompatible versions, missing evidence, failed verification, policy uncertainty, failed persistence, provider failure, or unavailable authority fail closed.
- Clarification, escalation, rejection, and no action are valid outcomes.
- Side effects require durable intent, idempotency, authorization, and receipt handling.
- Human edits and overrides are attributable, version-checked, and re-verified when substantive.
- Audit Events are append-only and ordered; corrections create new records.
- Source hierarchy, procedures, prerequisites, warnings, links, versions, locators, and provenance must survive compilation.
- Tenant and application identity remain explicit and isolated.
- Objective behavior may be measured; employee intent or motive may not be inferred.

## Runtime, application, and provider boundaries

Preserve the shared-runtime/application-package split:

- Runtime code owns lifecycle, state, provider invocation, verification mechanics, policy floor, permissions, authorization, audit, retries, recovery, and kill switches.
- `applications/mohid-support/` declares versioned MOHID knowledge, terminology, taxonomy, routing, templates, autonomy constraints, provider-profile references, and evaluations.
- The MOHID package must contain no credentials, SDKs, arbitrary executable workflow code, or bypass for a runtime control.
- Each Request Run pins its runtime, application-package, workflow, corpus, policy, model-profile, and adapter versions.

Use provider-neutral semantic contracts. Provider SDKs and transport payloads stay inside adapters. Write fakes and contract tests before live adapters. Implement only the company-approved adapter required by an active issue.

MCP is an optional adapter mechanism below semantic contracts. Do not create generic MCP infrastructure, a production MCP server, MCP discovery/hosting/administration, or MCP-shaped domain objects for the mTAP proof.

## Knowledge compiler boundary

Preserve four linked representations:

1. raw source snapshot;
2. canonical structured document;
3. deterministic human-readable derivative;
4. reproducible search projections.

The canonical structured blocks are the source for both generated Markdown and search projections. Do not flatten authoritative content, silently rewrite it with a model, reorder procedures, detach warnings or prerequisites, or treat Markdown/embeddings as the sole source of truth.

## Working rules

- Work only within the assigned issue and epic.
- Start from a failing test that expresses the required behavior.
- Implement the smallest change that satisfies the active acceptance criteria.
- Inspect existing contracts before adding or changing fields.
- Prefer explicit typed behavior over free-form orchestration.
- Avoid speculative abstractions and premature shared frameworks.
- Add a repository ADR for a durable implementation decision not settled by the living papers.
- Use a measured experiment for chunking, retrieval, reranking, orchestration, or provider choices whose value is empirical.
- Keep client-gated dependencies named; do not replace them with an alternate production stack.
- Keep external actions disabled unless the active issue explicitly authorizes a constrained test environment.
- Preserve unrelated user changes in a dirty worktree.
- Update `docs/STATUS.md` with objective evidence when the issue state, branch, blocker, acceptance gate, or CI result changes.

Classify every new proposal before acting on it:

- **REQUIRED:** needed for a current invariant or acceptance gate;
- **BENEFICIAL:** improves the bounded implementation without expanding scope;
- **EXPERIMENTAL:** requires measured evidence before adoption;
- **DEFERRED:** legitimate later work that is not required now; or
- **OVERENGINEERING:** abstraction or infrastructure without demonstrated need.

Place the result in the appropriate living-paper revision, repository ADR, measured experiment, backlog issue, or no active artifact. Coding agents do not revise living papers.

## Test and CI rules

Run the checks relevant to the issue, including formatting, linting, static typing, unit, provider-contract, integration, replay, security, evaluation, and end-to-end checks as applicable.

Never:

- weaken, skip, delete, or rewrite tests merely to make CI pass;
- silently change gold evaluation outcomes;
- substitute a fake-provider pass for a live-adapter integration claim;
- allow replay to trigger external actions;
- accept a provider receipt without validating its status;
- mark a failed or indeterminate action as dispatched or closed; or
- treat local success as a replacement for GitHub Actions.

An issue is merge-ready only when its acceptance criteria are demonstrated, required tests pass, relevant documentation and decision records are current, and GitHub Actions is green.

## Initial E01 boundary

E01 may create:

- repository and package structure;
- Python tooling;
- versioned domain schemas and enums;
- semantic provider protocols and local fakes;
- unit, contract, integration-shell, security, and acceptance-test structure;
- local PostgreSQL development setup;
- migration-framework shell;
- CI, formatting, linting, typing, secret scanning, dependency checks;
- `.env.example`;
- one-command local bootstrap; and
- E02/E03 acceptance-test shells.

E01 must not implement HelpDocs parser logic, retrieval, embeddings, MCP, live Gemini access, Office 365, Mandrill, automatic dispatch, complete policy behavior, SON, voice, or kiosk support.


### Legacy repository

Agents may inspect `https://github.com/ak23bar/legacy-prototype-v1`
read-only, using audited baseline `main@6eba0ff75d92`.

It is historical evidence, not V1 architecture authority.

Do not modify it or bulk-copy from it. Any port requires explicit review,
provenance, redaction where applicable, and V1 contract/test validation.

## Stop conditions

Stop the affected work and report assumptions, contradictions, blockers, and out-of-scope findings when:

- acceptance criteria are unclear;
- the living specifications conflict or appear to require revision;
- a change would weaken a mandatory boundary or test;
- the requested behavior requires changing a gold outcome;
- credentials, data, recipients, or authority are missing;
- the work crosses issue or epic scope;
- a new provider, framework, MCP layer, or infrastructure commitment is being introduced without approval; or
- failure cannot be represented safely and durably.

Do not guess. Report the exact affected criterion, evidence, safest current behavior, and required owner decision.

## Completion report

At the end of an issue, report:

- issue and branch;
- files and contracts changed;
- tests added or selected first;
- checks run and results;
- acceptance evidence;
- assumptions and unresolved blockers;
- ADR or status updates; and
- any out-of-scope finding for backlog or owner decision.
