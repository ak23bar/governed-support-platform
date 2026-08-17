# Repository Decision Register

This register indexes repository-level architecture decisions for GPS / MOHID V1. It is an implementation derivative,
not a replacement for either frozen living specification.

The authority order is:

1. Governed Support Automation Platform Living Reference v1.5;
2. MOHID Problem and First Implementation Living Specification v0.6; and
3. repository ADRs for implementation choices not already settled above.

MOHID v0.6 Section 23 contains the canonical product decision register. Repository ADRs record narrower implementation
decisions and may not duplicate, reinterpret, weaken, or override Platform v1.5 or MOHID v0.6. A conflict must be
resolved by correcting the derivative or escalating a living-specification revision to the product owner.

## Statuses

- **Proposed:** under review and not authoritative for implementation.
- **Accepted:** approved for repository implementation.
- **Superseded:** replaced by a later accepted ADR; both records remain available.
- **Rejected:** considered and explicitly not adopted.

## Registered ADRs

| ADR | Title | Status | Date | Scope |
| --- | --- | --- | --- | --- |
| [ADR-0001](ADR-0001-new-v1-repository.md) | Create a New GPS / MOHID V1 Repository | Accepted | 2026-07-27 | Repository strategy and legacy reuse boundary |

New records use [ADR-TEMPLATE.md](ADR-TEMPLATE.md). Do not create an ADR when the living specifications already settle
the decision or when the question belongs to a measured experiment, backlog item, or product-owner/client authority.
