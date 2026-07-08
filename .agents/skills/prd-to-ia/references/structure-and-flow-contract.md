# Structure And Flow Contract

Use this reference to turn the IA model into UI design inputs.

## Feature Placement Matrix

Every source-backed feature must be placed or explicitly not placed.

| Field | Meaning |
| --- | --- |
| `feature id` | Source ledger id |
| `feature` | Normalized feature statement |
| `navigation area` | Top-level or local area |
| `screen/route` | Screen or route that exposes it |
| `object/action` | Object and action it supports |
| `flow` | Flow where it appears |
| `status` | `placed`, `unplaced`, `excluded`, or `unresolved` |
| `rationale` | Short reason |

Do not hide uncertain features inside generic screens. If placement is unclear, use `unplaced` or `unresolved`.

## Navigation Model

Define information structure, not visual navigation styling.

For each navigation area:

| Field | Meaning |
| --- | --- |
| `area` | Product area or route group |
| `purpose` | Job it helps users complete |
| `primary roles` | Roles that use it |
| `primary objects` | Objects exposed here |
| `entry points` | How users arrive |
| `contains` | Screens or subareas |
| `source/rationale` | Source ids or assumption basis |

Keep top-level areas few and task/object aligned. Avoid adding settings, admin, or analytics areas unless source-backed or strongly implied by operational requirements.

## Route-To-Screen Map

For each route or route group:

| Field | Meaning |
| --- | --- |
| `route` | Route path or conceptual route |
| `screen` | Screen name |
| `role access` | Roles that can access it |
| `primary object` | Object instance or collection |
| `entry source` | Navigation, deep link, notification, previous flow, etc. |
| `exit paths` | Where users can go next |
| `tag` | Traceability tag |

Use conceptual routes if implementation routing is unknown.

## Screen Contracts

Every proposed screen needs a contract:

| Field | Meaning |
| --- | --- |
| `screen id/name` | Stable local name |
| `purpose` | User goal for the screen |
| `primary role` | Main actor |
| `primary object` | Object or collection shown |
| `source features` | Source ids supported |
| `entry points` | How users arrive |
| `exit paths` | Expected next destinations |
| `primary actions` | Main actions available |
| `secondary actions` | Supporting actions |
| `content priorities` | What information matters most |
| `states` | Required UI states |
| `permission rules` | Role restrictions |
| `dependencies` | Required data, prior steps, or object state |
| `unresolved` | Questions affecting the screen |

Screen contracts must not specify visual layout, styling, component libraries, color, typography, or pixel-level UI.

## Critical Flow Specs

Create critical flows for:

- Primary user jobs.
- Cross-role handoffs.
- Object lifecycle transitions.
- High-risk, permission-sensitive, destructive, or irreversible actions.
- AI generation/review/fallback flows when relevant.

Flow spec fields:

| Field | Meaning |
| --- | --- |
| `flow` | Flow name |
| `actor(s)` | Roles involved |
| `goal` | Desired outcome |
| `preconditions` | Required state before start |
| `trigger` | What starts it |
| `main path` | Numbered steps |
| `branches` | Alternate paths and decisions |
| `failure/empty states` | What happens when data, access, or system support is missing |
| `completion state` | Observable end state |
| `source/rationale` | Source ids or assumption basis |

Use Mermaid only when it clarifies sequence or branching. Tables are often better for design handoff.

## State Coverage Matrix

For each screen or flow, cover relevant states:

| State | Include when |
| --- | --- |
| `success` | Normal completed view or flow |
| `empty` | No content, no results, or first-use state |
| `loading` | Data or generation is in progress |
| `error` | System or validation failure |
| `permission` | Access denied, limited role, or approval needed |
| `fallback` | Alternate route when expected support is unavailable |

Do not force every state onto every screen. Mark `not applicable` when there is a clear reason.

Completion check: every screen is tied to objects, actions, roles, states, and source/rationale; every feature is placed, unplaced, excluded, or unresolved.
