# ADR-0001: Create a New GPS / MOHID V1 Repository

- **Status:** Accepted
- **Date:** 2026-07-27
- **Decision owner:** Akbar Aman
- **Derived from:** Governed Support Automation Platform Living Reference v1.5 and MOHID Problem and First Implementation Living Specification v0.6

## Authority

This ADR is a non-authoritative implementation derivative. If it conflicts with either living PDF, the living PDFs control. It records the closed repository strategy only; it does not revise the frozen architecture.

## Context

The legacy prototype proved a basic deployed transport loop and supplied valuable regression evidence, including Fahad's real email-style tests and observed retrieval, conversation-state, provider-quota, and delivery failures.

Its architecture does not satisfy the frozen V1 contracts. It relies on patterns explicitly excluded from the new core, including flattened knowledge, fixed-size chunks, one-primary-article RAG, ephemeral flat-file state, implicit model fallback, and legacy channel/provider choices.

Building V1 in place would make it easy to inherit those assumptions accidentally, blur the frozen specification baseline, and confuse regression evidence with current architecture. The MOHID v0.6 open repository decision is now closed by the product owner.

## Decision

Create a new repository for GPS and MOHID V1, recommended name:

```text
governed-support-platform
```

Keep `legacy-prototype-v1` read-only as:

- a historical technical baseline;
- a source of reviewed and redacted fixtures;
- a regression reference for known behavior and failures; and
- evidence for measured old-versus-new comparisons.

Do not develop V1 on a branch inside the legacy architecture. Do not bulk-copy the legacy repository.

Commit the two frozen living PDFs and this execution packet to the new repository, preserve the PDF bytes, and tag the specification baseline. The exact repository path and tag spelling are repository conventions to settle during E01; they do not alter this decision.

## Rationale

- Starts implementation from the frozen Platform v1.5 and MOHID v0.6 contracts.
- Prevents excluded legacy patterns from becoming accidental dependencies.
- Makes clean-checkout CI, package boundaries, migrations, provider contracts, and test-first delivery first-class from the first commit.
- Preserves the legacy prototype's real value without granting it architectural authority.
- Creates a clear provenance boundary for any asset deliberately ported into V1.
- Supports independent evaluation against the historical baseline.

## Assets allowed to be ported

An asset may be ported only after deliberate review, redaction where required, provenance recording, and validation against the new contracts and tests.

Allowed candidates include:

- redacted Fahad regression requests, including the clean/noisy mTAP pair;
- adjudicated expected source references, evidence, dispositions, and failure labels;
- selected redacted email fixtures and thread/correction scenarios;
- provider-quota, delivery-failure, and receipt-ambiguity examples;
- MOHID terminology and aliases verified against current authoritative sources; and
- historical behavior needed for a regression or old-versus-new comparison.

Ported fixtures must not silently retain live credentials, customer identifiers, unapproved personal data, or provider-specific objects in domain contracts.

## Assets prohibited from direct reuse

Do not copy these implementations into the new core:

- the FAISS or in-image vector pipeline;
- HelpDocs flattened to `.txt` and fixed character chunks;
- the single-primary-article RAG path;
- the Gemini-Mistral-OpenAI implicit fallback chain;
- the Mailgun inbound/outbound flow;
- Render-specific production assumptions;
- flat JSON or ephemeral-filesystem business persistence;
- customer-facing automatic behavior without the frozen rollout gates; or
- unreviewed source, credential, log, or customer-data dumps.

The concepts behind a prohibited implementation may be re-expressed only when the active issue, frozen contract, and tests require them. No legacy code receives a presumption of reuse.

## Consequences

### Positive

- V1 begins with a clean authority and provenance boundary.
- Repository structure, contracts, migrations, tests, and CI can match the frozen build order.
- Regression fixtures can be imported intentionally and traced to their source.
- The legacy baseline remains available for evidence and comparison.

### Costs

- The scaffold, CI, persistence shell, and adapters must be established again under the new contracts.
- Reusable fixtures require review and redaction before import.
- Any useful legacy behavior must be proven by tests rather than copied by assumption.

### Required controls

- Keep the legacy repository read-only.
- Maintain a manifest or PR evidence for each ported asset's source, redaction status, and intended test.
- Reject unreviewed bulk migration.
- Never edit the frozen living PDFs in the implementation repository.
- If a derivative conflicts with the PDFs, correct the derivative or escalate a living-document revision to the product owner.

## Relationship to execution

This ADR unblocks E01. It does not authorize source implementation beyond the bounded E01 issue, create provider access, or close any client-gated dependency.

## Agent access to the legacy baseline

Coding and review agents may inspect the legacy repository as a read-only
historical source:

https://github.com/ak23bar/legacy-prototype-v1

The audited baseline is:

main @ 6eba0ff75d92

Agent access is permitted only to:

- inspect earlier implementation behavior;
- recover reviewed regression evidence and fixtures;
- understand documented failure modes;
- compare old and new behavior; and
- identify narrowly reusable assets for explicit human review.

The legacy repository has no authority over V1 architecture.

Agents must not:

- push, branch, open implementation PRs, or otherwise modify the legacy repository;
- bulk-copy legacy source into V1;
- infer current V1 requirements from legacy implementation choices;
- silently port fixtures, customer data, credentials, logs, or provider-specific objects; or
- treat later legacy commits as part of the audited baseline without a new audit note.

Any asset ported into V1 requires explicit provenance, review, applicable
redaction, and validation against the current V1 contracts and tests.