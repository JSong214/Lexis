# PRD Template And Quality Bar

Use this template as the default shape. Remove sections that do not apply; do not invent content just to fill them.

## Template

```markdown
# <Feature Or Product Name> PRD

## Status

Draft | Ready for review | Ready for implementation

## Source Summary

Briefly name the source material used: conversation, `grill-me` decisions, plan file, repo evidence, or issue.

## Problem

Describe the user's problem in product language.

## Goals

List the outcomes this PRD is meant to achieve.

## Non-Goals

List confirmed exclusions, deferred phases, and rejected directions.

## Users And Actors

Name the primary user, secondary actors, and systems involved.

## Scope

Describe the MVP or feature boundary. Separate must-have scope from confirmed follow-up scope.

## User Journey

Describe the main path from entry point to successful outcome.

## Functional Requirements

List requirements that are traceable to the Decision Ledger.

## User Stories

Include user stories only for user-visible behavior. Keep them proportional to the confirmed scope.

## Acceptance Criteria

Write observable criteria that implementation can be checked against.

## Data, API, And Technical Notes

Include only product-relevant technical decisions, repo constraints, API contracts, data shape expectations, or integration notes.

## Testing Strategy

Describe the highest useful testing seam, external behavior to verify, relevant prior art, and confidence level.

## Risks And Mitigations

List meaningful product, technical, data, rollout, privacy, or operational risks.

## Open Questions

List non-blocking gaps and unresolved decisions.
```

## Quality Bar

- Prefer a scoped PRD over an exhaustive PRD.
- Do not create a long user-story list for its own sake.
- Do not promote brainstorm ideas to requirements.
- Do not hide assumptions. Mark them as assumptions or open questions.
- Keep implementation detail proportional. PRDs may include technical decisions, but should not become code plans.
- Keep non-goals explicit, especially after `grill-me` narrowed scope.
- Use product vocabulary from the repo or source plan when available.
- Describe tests through external behavior and product seams, not internal implementation trivia.
- For recommended testing seams, include confidence: high, medium, or low.
- If the PRD is meant for an implementation agent, make the scope and acceptance criteria actionable enough that the agent can start without re-discovery.
