# AI Product Addendum

Read this before readiness classification when the product involves AI, RAG, agents, LLM output, retrieval, evals, prompts, tool use, or model behavior.

## Required AI Contract Fields

Add ledger rows or blocking questions for these fields:

- AI role: what the model does for the user.
- Input contract: user data, files, messages, retrieved context, or tool outputs the AI receives.
- Output contract: format, tone, structure, allowed actions, and user-visible result.
- Data source: where grounding context comes from and what must not be used.
- Fallback behavior: what happens when the model, retrieval, tool, or external API fails.
- Guardrails: safety, privacy, permission, hallucination, and misuse boundaries.
- Evaluation seam: how useful, grounded, correct, or safe output will be checked.
- Observability: what should be logged or inspected without storing secrets or unnecessary private data.

## Blocking AI Gaps

Mark the ledger `Blocked` if any of these are missing and the PRD would misrepresent the product without them:

- AI role is unclear.
- Input or output contract is unclear.
- Grounding data source is unclear for RAG or retrieval-heavy features.
- Fallback behavior is absent for user-facing AI output.
- Evaluation seam is absent for core AI behavior.

Non-blocking details should stay in `Open Questions`, including exact model choice, prompt wording, eval thresholds, metric names, and final copy.

## Compile Notes

Do not turn model choice, prompt details, or eval thresholds into requirements unless the user confirmed them. Preserve them as assumptions or open questions when they are inferred.