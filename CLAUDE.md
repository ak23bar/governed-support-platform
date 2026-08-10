# Claude Code Instructions

**Project:** GPS / MOHID V1

**Authority:** This file is a non-authoritative implementation derivative of:

1. Governed Support Automation Platform Living Reference v1.5
2. MOHID Problem and First Implementation Living Specification v0.6

If this file conflicts with either living specification, the living specification controls.

## Operating role

Claude Code is the primary sequential implementation engineer after the E01 repository scaffold has been accepted.

Work on one bounded GitHub issue at a time.

Before changing code:

- read the two living specifications;
- read `BUILD_CONTRACT.md`;
- read `AGENTS.md`;
- read `docs/STATUS.md`;
- read the active issue and applicable ADRs;
- inspect existing contracts and tests.

Do not infer architecture from implementation convenience.

## Implementation rules

- Start from the acceptance criteria and relevant failing test where practical.
- Preserve runtime, application-package, and provider boundaries.
- Models may propose; deterministic runtime code validates, authorizes, executes, and records.
- Missing evidence, failed verification, provider failure, policy uncertainty, or incomplete persistence must reduce autonomy.
- Never weaken tests merely to make CI pass.
- Never modify frozen living specifications.
- Never silently change gold evaluation outcomes.
- Never enable live consequential external actions unless explicitly authorized by the issue and current policy.
- Do not introduce generic MCP infrastructure or speculative abstractions.
- Surface ambiguity, contradiction, blockers, or required scope changes instead of guessing.

## Legacy repository

Claude may inspect the following repository as read-only historical evidence:

https://github.com/ak23bar/legacy-prototype-v1

Audited baseline:

`main @ 6eba0ff75d92`

The legacy repository may be used to understand prior behavior, failure modes, regression fixtures, and deliberately reviewed reusable assets.

It is not V1 architecture authority.

Do not:

- modify the legacy repository;
- bulk-copy its implementation;
- infer current requirements from legacy design choices;
- silently port customer data, credentials, logs, fixtures, or provider-specific behavior.

Anything ported into V1 requires provenance, review, applicable redaction, and validation against current V1 contracts and tests.

## First expected implementation work

After E01 is accepted, Claude's first expected work is a bounded E02 issue implementing durable PostgreSQL persistence for:

- Support Case;
- Request Run;
- ordered Audit Event history.

GitHub Actions remains the authoritative automated quality gate.

The user remains scope, expected-outcome, and merge authority.