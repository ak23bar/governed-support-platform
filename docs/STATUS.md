# GPS / MOHID V1 Status

**Derived from:** Governed Support Automation Platform Living Reference v1.5 and MOHID Problem and First Implementation Living Specification v0.6

**Authority:** This file is a non-authoritative implementation derivative. If it conflicts with either living PDF, the living PDFs control.

## Current resumption state

| Field | Current value |
| --- | --- |
| Current package | Package A |
| Current epic | Pre-E01 repository bootstrap |
| Current issue | Repository baseline |
| Current issue state | In progress; frozen specifications and execution-control files are being assembled and verified |
| Current branch | `chore/repository-baseline` |
| Repository status | Created and cloned; baseline changes not yet merged to `main` |
| Architecture baseline | Platform v1.5 / MOHID v0.6 |
| Last completed gate | Architecture freeze |
| Current blockers | None |
| Next immediate criterion | Verify, commit, push, and merge the frozen repository baseline |
| Next acceptance gate | Complete E01 with clean-checkout bootstrap and GitHub Actions green |
| Latest CI result | Not available; CI is not yet implemented |

## Active execution order

1. Approve this execution packet.
2. Create the new `governed-support-platform` repository.
3. Commit the frozen living specifications and execution packet without modifying the PDFs.
4. Tag the frozen specification baseline.
5. Configure GitHub milestones, E01-E03 issues, labels, and board.
6. Assign bounded E01 scaffolding to Codex.
7. Repair until a fresh checkout passes the documented bootstrap and GitHub Actions is green.
8. Audit and accept E01.
9. Open the first bounded E02 persistence issue for Claude Code.

## Client-gated dependencies

These are not current blockers for execution-packet approval or contract-first E01 work. They become blockers only for the acceptance claims shown in the living specification.

| Dependency | Needed for | Safe state while missing |
| --- | --- | --- |
| HelpDocs inventory, approved HTML/fixtures, source status, acquisition permission, and corpus approver | E03 production-candidate corpus publication | Build against approved fixtures; do not claim a production-candidate corpus is approved |
| Official HelpDocs API/export details | Optional future acquisition-adapter decision | Not required for mTAP or Package A; do not build generic MCP infrastructure |
| GCP/Gemini model and embedding endpoints, quotas, region, and owner | Provider integration and performance claims | Use contract fakes; keep integration explicitly blocked |
| Approved PostgreSQL/pgvector, object storage, hosting target, backups, secrets, and operator | Integrated durability, recovery, and deployment gates | Use local PostgreSQL/test infrastructure; do not claim production readiness |
| Office 365 mailbox ownership, Graph consent/scopes or forwarding path, and test messages | Package C channel integration | Replay or fake intake only |
| Mandrill sender, credentials, approved test recipients, and receipt semantics | Package C outbound integration | Fake provider only; no outbound action |
| L1/L2/specialist/manager queues, route owners, reviewer, retention policy, incident owner, and acceptance authority | Routing-value claims, shadow mode, and pilot | Preserve typed routing seams; do not claim operational acceptance |
| Redacted case bodies, expected sources/outcomes, and adjudicator access | Evaluation and value proof | Keep baseline provisional; never silently change gold outcomes |

## Update rules

- Update this file after an issue, branch, acceptance gate, blocker, or CI result changes.
- Record only objective evidence. A local agent statement does not replace a GitHub Actions result.
- Keep client access gaps named; do not mark an integration complete because its fake passes.
- If a material specification change is required, stop implementation and return to the living-document owner.

## Future-session update template

```markdown
## Status update - YYYY-MM-DD

- Current package:
- Current epic:
- Current issue:
- Current branch:
- Primary implementer:
- Reviewer:
- Last accepted commit or PR:
- Last completed gate:
- Current blockers:
- Next acceptance criterion:
- Latest CI result and link:
- Decisions or ADRs added:
- Handoff note:
```
