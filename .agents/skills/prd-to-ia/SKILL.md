---
name: prd-to-ia
description: Turn an existing PRD, product brief, feature spec, or confirmed requirements artifact into UI-ready information architecture. Use when the user asks for IA, information architecture, sitemap, route map, screen inventory, screen contracts, task flows, user flows, navigation structure, or a UI design handoff derived from a PRD.
---

# PRD To IA

## Contract

Compile an existing PRD into an IA handoff for UI design. Do not run a new product discovery process, rewrite the PRD, create visual design, choose components, or invent product scope.

Tag every non-trivial IA item as one of:

- `source-backed`: directly supported by the PRD.
- `inferred`: a limited IA assumption needed to connect source-backed facts.
- `unresolved`: a question or conflict that affects structure.
- `excluded`: explicitly out of scope or intentionally not modeled.

## Workflow

1. Confirm the PRD source and output target.
   - Accept a file path, pasted PRD text, or named upstream artifact.
   - If no PRD is available or readable, ask for it.
   - If no output target is specified, deliver the IA handoff in chat.
   - Completion criterion: the PRD source is readable and the output behavior is known.

2. Run intake and readiness.
   - Read `references/intake-and-readiness.md`.
   - Extract only PRD-supported facts.
   - Classify gaps as blocking, non-blocking, or design-time questions.
   - Stop and ask concise questions only for blocking gaps.
   - Completion criterion: every relevant PRD section is accounted for as a fact, gap, non-goal, risk, or excluded item.

3. Apply the AI product lens when relevant.
   - If the PRD includes AI, chat, agents, generated content, recommendations, automation, retrieval, evaluation, or model-driven decisions, read `references/ai-product-addendum.md` before modeling.
   - Completion criterion: AI-specific objects, states, permissions, fallback needs, and review surfaces are either modeled or marked unresolved/excluded.

4. Build the IA model.
   - Read `references/ia-model-contract.md`.
   - Model roles, tasks, domain objects, content types, actions, lifecycle states, and permissions.
   - Completion criterion: every model item has a traceability tag and no inferred item is presented as PRD fact.

5. Define structure and flows.
   - Read `references/structure-and-flow-contract.md`.
   - Produce the feature placement matrix, navigation model, route map, screen inventory, screen contracts, critical flows, and state coverage.
   - Completion criterion: every source-backed feature is placed, marked unplaced with a reason, or excluded with a source-backed rationale.

6. Produce the IA handoff.
   - Read `references/handoff-output-contract.md`.
   - Use the required output schema unless the user requested a narrower artifact.
   - Completion criterion: the handoff is usable by UI design without needing to infer screen purpose, object ownership, entry points, actions, or required states.

7. Run the quality gate.
   - No PRD feature is silently dropped.
   - No proposed screen lacks a goal, primary object, entry point, source/rationale, actions, states, and permission notes.
   - No inferred role, object, action, state, or permission appears without an assumption tag.
   - Critical flows include success, empty, loading, error, permission, and fallback states where relevant.
   - AI products include input contract, generated output states, confidence/citation/review needs, fallback, history/threading, and eval/admin visibility where relevant.
   - Visual design, layout, styling, component-library choices, and implementation architecture are excluded.
   - Completion criterion: failed checks are fixed, moved to `Unresolved`, or explicitly excluded with rationale.

## Output Discipline

Prefer structured tables and short flow specs over essay-style IA commentary. If the PRD is too thin for a complete IA handoff, produce a readiness assessment and the highest-confidence partial artifacts instead of filling gaps with invented structure.
