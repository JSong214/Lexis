---
name: to-prd
description: Compile confirmed planning decisions into a scoped PRD.
disable-model-invocation: true
---

# To PRD

Compile existing planning decisions into a PRD. Do not restart discovery.

## Pipeline

1. Identify the source material:
   - current conversation
   - a selected plan file
   - a prior `grill-me` or `grilling` discussion
   - repo evidence, only when needed to ground implementation or testing decisions already in scope

   If no source material is visible or named, ask one source question and stop.

2. Read `references/decision-ledger.md`.
   Extract a Decision Ledger before drafting. Keep confirmed decisions, repo evidence, assumptions, open questions, and rejected scope separate.

3. Read `references/readiness-and-stop-rules.md`.
   If a stop rule is met, ask exactly one concise blocking question and stop. Put non-blocking gaps in `Open Questions`.

4. Read `references/prd-template-and-quality-bar.md`.

5. If the product involves AI, RAG, agents, LLM behavior, model output, retrieval, evaluation, or tool use, also read `references/ai-product-addendum.md`. Use it as an addendum, not as a second PRD template.

6. Draft the PRD.
   Every requirement must trace to a Confirmed Decision, Repo Evidence, or Explicit Assumption from the Decision Ledger. Do not convert suggestions, unresolved ideas, or inferred nice-to-haves into requirements.

7. Determine the delivery target:
   - If the user only asks to generate, draft, create, or turn discussion into a PRD, respond in chat.
   - If the user explicitly asks to write a file, update a file, publish an issue, create a tracker item, or apply labels, read `references/publishing-targets.md` first and perform only that requested side effect.
   - If the target is ambiguous and a side effect was requested, ask one target question and stop.

## Completion Criteria

- The Decision Ledger exists before the PRD draft.
- Requirements are sourced from confirmed decisions, repo evidence, or explicit assumptions.
- Non-goals and open questions are preserved instead of silently resolved.
- User stories are proportional to confirmed user-visible behavior, not made long for length's sake.
- No file write, issue creation, label change, or tracker update happens without an explicit user request.
