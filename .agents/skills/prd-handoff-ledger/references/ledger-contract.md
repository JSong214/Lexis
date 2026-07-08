# Ledger Contract

Use this contract to turn completed discovery into a confirmable ledger. The ledger is the source boundary for `$to-prd`.

## Source Rules

- Treat explicit user decisions as stronger than assistant recommendations.
- Treat later explicit user confirmations as overriding earlier assumptions or recommendations.
- Treat assistant recommendations from `grill-me` or `grilling` as unconfirmed until the user accepts them.
- Treat a named plan file as source material only when the user names it, the file itself states accepted scope, or the current request clearly points to it.
- Treat repo evidence as current implementation context or constraint. Do not convert it into product intent unless user source material confirms that intent.
- Preserve conflicts instead of smoothing them away.
- Do not invent features to fill a schema section.

## Ledger Item Schema

Use stable IDs such as `D1`, `R1`, `A1`, `Q1`, `X1`, and `K1`.

```text
ID:
Category:
Statement:
Source Pointer:
Confirmation Level: confirmed | user-accepted | unconfirmed | assumed | repo-evidence
Confidence: high | medium | low
Downstream Use: requirement | context | non-goal | risk | open-question | none
```

Categories:

- `Confirmed Decision`: User-confirmed behavior, scope, goal, non-goal, or accepted plan point.
- `Unconfirmed Recommendation`: Assistant recommendation, proposed answer, or likely direction not clearly accepted by the user.
- `Explicit Assumption`: Narrow assumption needed to make the ledger readable.
- `Repo Evidence`: Codebase, API, schema, test, documentation, or existing behavior fact.
- `Open Question`: Non-blocking unknown or unresolved detail.
- `Conflict`: Contradiction with no clear latest user decision.
- `Out of Scope / Rejected`: Rejected, deferred, non-MVP, or explicitly excluded direction.
- `Risk`: Product, technical, data, privacy, rollout, or operational risk.

## Output Shape

```markdown
# PRD Handoff Ledger / Decision Ledger

## Status
Ready for confirmation | Blocked | Confirmed

## Source Summary
Name the conversation, `grill-me`/`grilling` run, plan file, repo evidence, or user-provided source.

## Product Frame
- Problem:
- Target User / Actor:
- MVP Boundary:

## Ledger
| ID | Category | Statement | Source Pointer | Confirmation Level | Confidence | Downstream Use |
| --- | --- | --- | --- | --- | --- | --- |

## Rejected Scope
List confirmed exclusions and deferred directions.

## Risks
List meaningful risks only.

## Open Questions
List unresolved items. Mark blocking questions clearly.

## Downstream Contract For `$to-prd`
State what `$to-prd` may compile into requirements and what it must preserve as assumptions, non-goals, risks, or open questions.
```

## Readiness Rules

First generated ledgers can only be `Ready for confirmation` or `Blocked`. Use `Confirmed` only when the user has explicitly confirmed this exact ledger or provides a ledger they state is already confirmed.

Mark `Blocked` and ask exactly one question when any of these are true:

- No source material is visible or named.
- The core problem is unknown.
- The target user or actor is unknown.
- The MVP or feature boundary is completely unknown.
- The source contains a core-scope contradiction with no clear latest user decision.
- For AI products, required AI contract fields are missing after reading `ai-product-addendum.md`.

If blocked, ask the highest-leverage question in this order: source, core problem, target user, MVP boundary, core conflict, AI contract.

Mark `Ready for confirmation` when the ledger can be reviewed without misrepresenting the product. Put non-blocking gaps in `Open Questions`.

## Compile Contract

`$to-prd` may compile only these into requirements:

- `Confirmed Decision`
- `Repo Evidence` used as implementation context, not intent
- `Explicit Assumption` that remains labeled as an assumption

`$to-prd` must not upgrade these into requirements:

- `Unconfirmed Recommendation`
- `Open Question`
- `Conflict`
- `Risk`
- `Out of Scope / Rejected`