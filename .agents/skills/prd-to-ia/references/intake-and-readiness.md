# Intake And Readiness

Use this reference to convert the PRD into a traceable source ledger before modeling IA.

## Source Handling

Accept PRDs as file paths, pasted text, or named artifacts from the current conversation. If several PRDs or versions are present, identify the one being used and note any version/date available in the handoff.

Do not inspect secret-bearing config or unrelated project files to infer requirements.

## Source Ledger

Create a compact source ledger with these fields:

| Field | Meaning |
| --- | --- |
| `id` | Stable local id such as `REQ-001`, `GOAL-001`, or `NOGOAL-001` |
| `source` | Section heading, file path, paragraph, or quoted short phrase |
| `type` | `goal`, `user`, `role`, `feature`, `object`, `constraint`, `non-goal`, `metric`, `risk`, `open-question` |
| `statement` | Requirement or fact in normalized wording |
| `notes` | Ambiguity, conflict, or relation to other facts |

Keep quotes short. Use paraphrase for most source material.

## Feature Normalization

Normalize feature statements into this shape:

`actor -> intent/task -> object/content -> action -> outcome`

If any part is missing, leave it blank and record the gap. Do not invent an actor, object, or outcome just to make the row complete.

## Gap Classification

Use three classes:

| Class | Meaning | Action |
| --- | --- | --- |
| `blocking` | Prevents a reliable IA handoff | Ask before continuing or produce only readiness findings |
| `non-blocking` | Affects detail but not core structure | Continue and record in assumptions/questions |
| `design-time` | Can be resolved during UI design without changing IA | Record only if useful |

Blocking gaps include:

- No identifiable primary user, role, or actor.
- No product goal or core job.
- No core scope or usable feature set.
- No core object/content type for a product that depends on object manipulation.
- Conflicting requirements that change navigation, permissions, lifecycle, or safety boundaries.
- A PRD that is mostly solution styling or implementation notes rather than product requirements.

## Assumption Rules

Only make assumptions that connect source-backed facts into an IA model. Each assumption must include:

| Field | Meaning |
| --- | --- |
| `assumption` | The inferred IA decision |
| `basis` | The source-backed facts that support it |
| `confidence` | `low`, `medium`, or `high` |
| `impact` | What changes if the assumption is wrong |
| `validation_question` | The question to confirm later |

Never assume a new core feature, user role, permission level, data object, monetization model, or compliance requirement.

## Readiness Assessment

Before modeling, produce or internally maintain:

- Source used.
- Scope summary.
- Blocking gaps, if any.
- Non-blocking gaps.
- Design-time questions.
- Explicit non-goals and exclusions.

Completion check: every relevant PRD section is represented in the source ledger, gap list, non-goals, or exclusions.
