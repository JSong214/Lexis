# Decision Ledger

Build a Decision Ledger before drafting the PRD. The ledger is the source boundary for the PRD.

## Schema

Use these categories:

- `Confirmed Decision`: A user-confirmed decision, accepted plan point, or source document statement that describes intended product behavior or scope.
- `Repo Evidence`: A current codebase, API, schema, test, or documentation fact. Repo evidence proves current state, not product intent.
- `Explicit Assumption`: A narrow assumption needed to make the PRD readable. Mark it as an assumption in the PRD.
- `Open Question`: A non-blocking unknown, unresolved branch, implementation detail, or future decision.
- `Out of Scope / Rejected`: A boundary the user rejected, deferred, or explicitly excluded.
- `Source Pointer`: A short pointer to the conversation turn, plan section, file path, issue, or repo artifact behind the item.

Recommended ledger row:

```text
ID:
Category:
Statement:
Source Pointer:
Confidence: high | medium | low
PRD Use: requirement | context | non-goal | risk | open-question | none
```

## Extraction Rules

- Treat later explicit user confirmations as overriding earlier assumptions or assistant recommendations.
- Treat user decisions as stronger than assistant suggestions.
- Treat a source plan file as confirmed only when the user names it as source material or the file itself states accepted scope.
- Treat repo evidence as implementation context. Do not turn current code shape into product intent unless the user or source material confirms it.
- Treat assistant recommendations during `grill-me` as unconfirmed until the user accepts them.
- Treat rejected ideas, deferred phases, and "not MVP" statements as `Out of Scope / Rejected`.
- Keep conflicting decisions visible. Use the latest explicit user decision when there is a clear override; otherwise put the conflict in `Open Questions`.
- Do not infer new features to fill a template section.

## PRD Traceability

Every functional requirement and acceptance criterion must trace back to one of:

- a `Confirmed Decision`
- `Repo Evidence`
- an `Explicit Assumption`

Prefer concise source notes over verbose citations. Use ledger IDs in the PRD only when they improve clarity.
