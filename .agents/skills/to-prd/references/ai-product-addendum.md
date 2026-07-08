# AI Product Addendum

Read this only when the PRD involves AI, RAG, agents, LLM behavior, retrieval, model output, evaluation, or tool use.

Use these checks to enrich the PRD. Do not replace the main PRD template.

## Add Or Check These Sections

- `AI Behavior Contract`: What the AI should produce, for whom, from what inputs, and with what constraints.
- `Data Boundary`: What data sources may be used, what must not be used, and whether user data or external data is involved.
- `Grounding And Retrieval`: For RAG, name retrieval sources, citation/provenance expectations, stale-data behavior, and fallback when retrieval is weak.
- `Evaluation`: Define success signals, eval cases, human review needs, regression checks, and unacceptable failures.
- `Fallbacks`: Describe empty states, low-confidence responses, model/API failure, rate limits, and degraded behavior.
- `Safety And Permissions`: For agents or tool use, define what actions require confirmation, what actions are disallowed, and what audit trail is needed.
- `Observability`: Include logging, traces, token/cost metrics, latency, error classes, and feedback capture when relevant.
- `Cost And Latency`: Capture constraints when user experience, budget, or scalability depends on them.
- `Privacy And Compliance`: Flag sensitive data, retention, access control, and external provider exposure.

## Rules

- Do not invent eval thresholds, model names, prompts, or safety policies. If not confirmed, list them as `Open Questions`.
- Treat model choice as implementation detail unless the product behavior depends on a specific model capability.
- For AI features, acceptance criteria must include at least one behavior-level success case and one failure or fallback case when the source material supports it.
- For agentic features, acceptance criteria must cover permission boundaries and irreversible actions when those actions are in scope.
