# AI Product Addendum

Read this reference before IA modeling when the PRD includes AI, chat, agents, generated content, recommendations, retrieval, automation, evaluation, or model-driven decisions.

## AI-Specific IA Objects

Consider whether the PRD requires these objects:

| Object | Use when |
| --- | --- |
| `input` | User prompt, instruction, uploaded file, selected source, parameter, or form input |
| `generation request` | A submitted AI job or turn |
| `generated output` | AI-created text, data, decision, image, plan, summary, or recommendation |
| `source/citation` | Evidence, retrieved document, reference, or provenance item |
| `conversation/thread` | Multi-turn context or history |
| `review item` | Output requiring human approval, edit, acceptance, or rejection |
| `evaluation signal` | Rating, correction, test result, metric, or feedback |
| `policy/safety event` | Blocked, flagged, redacted, or restricted output |

Only include objects supported or strongly implied by the PRD.

## Input Contract

For AI input surfaces, model:

- Required inputs.
- Optional parameters.
- Supported sources/uploads.
- Validation and missing-input states.
- Role restrictions.
- Whether input is one-shot, iterative, or threaded.
- What context the AI can use.

## Generated Output States

Generated output often needs states beyond normal CRUD:

- `draft`.
- `submitting`.
- `generating`.
- `partial`.
- `complete`.
- `needs-review`.
- `accepted`.
- `edited`.
- `rejected`.
- `failed`.
- `fallback-used`.
- `blocked`.
- `expired`.

Use only states that affect UI behavior, permissions, or flows.

## Trust, Evidence, And Review

When relevant, model:

- Confidence indicators.
- Citations or provenance.
- Explanation/rationale visibility.
- Human review, edit, approve, reject, retry, or regenerate actions.
- Audit/history requirements.
- Error and fallback paths.

Do not add trust UI just because the product uses AI. Add it when the PRD implies accuracy, safety, review, compliance, traceability, or user decision support.

## History And Threading

If the AI interaction is conversational or iterative, model:

- Thread or session object.
- Turn-level input/output.
- Saved history.
- Resume/reopen entry points.
- Context reset or branch behavior when supported by the PRD.

## Admin, Eval, And Operations

Only create admin/eval surfaces when the PRD implies operations, monitoring, quality review, prompt management, model settings, feedback review, or evaluation.

Potential surfaces:

- Output review queue.
- Feedback/evaluation dashboard.
- Source management.
- Prompt/configuration management.
- Safety or policy events.
- Usage limits or cost visibility.

Mark these as `unresolved` when implied but underspecified.

## AI Flow Checks

Critical AI flows should cover:

- Input preparation.
- Submission.
- Generation/loading.
- Output inspection.
- Accept/edit/retry/reject.
- Citation/provenance inspection when relevant.
- Failure, fallback, blocked, or unsafe output.
- History and later retrieval when relevant.

Completion check: AI objects, states, review needs, fallback, history/threading, and eval/admin visibility are modeled, excluded, or unresolved with rationale.
