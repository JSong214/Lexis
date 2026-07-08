# Readiness And Stop Rules

`to-prd` is a compiler, not a second interview. Stop only when drafting would misrepresent the product or when a requested side effect cannot be targeted safely.

## Blocking Gaps

Ask exactly one concise question and stop when any of these are true:

- No source material is visible or named.
- The core problem is unknown.
- The target user or actor is unknown.
- The MVP or feature boundary is completely unknown.
- The user requested a file write, issue creation, tracker publish, label change, or update, but the target is ambiguous.
- The source material contains a direct contradiction that changes the core scope and has no clear latest decision.

If multiple blocking gaps exist, ask the highest-leverage question in this order:

1. Source material
2. Core problem
3. Target user
4. Scope boundary
5. Side-effect target

## Non-Blocking Gaps

Do not ask follow-up questions for these. List them in `Open Questions`:

- Exact UI copy
- Final visual design
- Analytics event names
- Detailed edge cases outside the confirmed flow
- Final database field names
- Specific test file locations
- Recommended testing seam when confidence is medium or high
- Model choice, prompt wording, or eval thresholds when the AI behavior contract is already clear
- Nice-to-have ideas that were discussed but not confirmed

## Stop Behavior

When a blocking gap exists:

- Ask one question.
- Explain in one sentence why the PRD would be unsafe or misleading without it.
- Do not draft a partial PRD unless the user explicitly asks for a partial draft.

When no blocking gap exists:

- Draft the PRD.
- Put non-blocking gaps in `Open Questions`.
- Mark assumptions clearly instead of hiding them in requirements.
