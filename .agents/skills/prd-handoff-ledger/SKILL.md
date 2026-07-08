---
name: prd-handoff-ledger
description: Build a confirmable PRD Handoff Ledger before PRD generation.
disable-model-invocation: true
---

# PRD Handoff Ledger

Convert completed discovery into a confirmable `PRD Handoff Ledger / Decision Ledger`. Do not draft the PRD.

## Pipeline

1. Identify the source material:
   - current conversation
   - a completed `grill-me` or `grilling` discussion
   - a selected plan file
   - repo evidence, only when needed to clarify decisions already in scope

   If no source is visible or named, ask one source question and stop.

2. Read `references/ledger-contract.md`.
   Extract a candidate ledger. Keep confirmed decisions, assistant recommendations, assumptions, repo evidence, open questions, conflicts, risks, and rejected scope separate.

3. If the product involves AI, RAG, agents, LLM output, retrieval, evals, prompts, tool use, or model behavior, read `references/ai-product-addendum.md`.
   Add AI-specific ledger rows before applying readiness rules.

4. Apply the readiness rules from `references/ledger-contract.md`.
   First generated ledgers can only be `Ready for confirmation` or `Blocked`. Mark `Confirmed` only when the user has already explicitly confirmed this exact ledger or has provided an already-confirmed ledger.

5. Present the ledger and ask the user to confirm or correct it.
   Do not call `$to-prd`, draft a PRD, write files, create issues, apply labels, or publish tracker items unless the user explicitly asks after confirming the ledger.

## Completion Criteria

- The output is a `PRD Handoff Ledger / Decision Ledger`, not a PRD.
- Every important ledger row has a stable ID and either a source pointer or an explicit assumption marker.
- User-confirmed decisions, assistant recommendations, assumptions, repo evidence, open questions, conflicts, risks, and rejected scope are separated.
- Repo evidence is treated as current-state evidence, not automatic product intent.
- Later explicit user confirmations override earlier assumptions or recommendations.
- The ledger includes readiness status and the next blocking question only when blocked.
- The final response asks the user to confirm or correct the ledger.