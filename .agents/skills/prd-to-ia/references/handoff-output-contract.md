# Handoff Output Contract

Use this reference to produce the final IA handoff.

## Default Output Schema

Use these sections unless the user asks for a narrower artifact:

1. Source And Scope Summary.
2. Readiness Assessment.
3. Normalized Feature Inventory.
4. Role / Permission Model.
5. Domain Object And Content Model.
6. Object Lifecycle And State Model.
7. Feature Placement Matrix.
8. Navigation And Route Model.
9. Screen Inventory With Screen Contracts.
10. Critical Flow Specs.
11. State Coverage Matrix.
12. Assumptions, Open Questions, Risks.
13. Traceability Matrix.

If the output would be too long, prioritize:

1. Readiness Assessment.
2. Feature Placement Matrix.
3. Screen Contracts.
4. Critical Flow Specs.
5. Traceability Matrix.

## Section Requirements

### Source And Scope Summary

Include source used, product goal, primary users, core scope, explicit non-goals, and excluded material.

### Readiness Assessment

List blocking gaps first. If blocking gaps remain, stop after the readiness assessment or produce clearly marked partial IA artifacts.

### Normalized Feature Inventory

Use normalized feature rows from intake. Preserve source ids.

### Role / Permission Model

Include roles and a compact permission matrix. Mark unresolved permissions rather than assuming access.

### Domain Object And Content Model

Include only objects/content needed by UI structure and flows. Avoid database or API design.

### Object Lifecycle And State Model

Show user-visible or flow-critical states and transitions.

### Feature Placement Matrix

Show where each PRD feature appears. Include `unplaced`, `excluded`, and `unresolved` rows.

### Navigation And Route Model

Show navigation areas and route-to-screen mapping. Use conceptual routes when implementation routes are unknown.

### Screen Inventory With Screen Contracts

Each screen must include purpose, primary role, primary object, source features, entry points, exit paths, actions, content priorities, states, permission rules, dependencies, and unresolved questions.

### Critical Flow Specs

Describe main path, branches, failure/empty/permission states, completion state, and source/rationale.

### State Coverage Matrix

Cover success, empty, loading, error, permission, and fallback states where relevant.

### Assumptions, Open Questions, Risks

Separate assumptions from questions and risks. Each assumption needs basis, confidence, impact, and validation question.

### Traceability Matrix

Use:

| Source id | PRD fact/requirement | IA artifact | Decision | Tag | Open issue |
| --- | --- | --- | --- | --- | --- |

## Quality Gate

Before finalizing, verify:

- Each major PRD feature appears in the placement matrix.
- Each screen has a complete screen contract.
- Each model item and screen decision has a traceability tag.
- Unplaced features are visible and explained.
- Assumptions do not introduce new core product scope.
- Open questions are not mixed with confirmed requirements.
- AI-specific requirements are handled through `ai-product-addendum.md` when relevant.
- The handoff avoids visual design, layout, component, implementation, and styling recommendations.

If a check fails, revise the handoff or mark the issue unresolved. Do not silently smooth over the failure.
