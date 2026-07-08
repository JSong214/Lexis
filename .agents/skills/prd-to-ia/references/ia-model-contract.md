# IA Model Contract

Use this reference to build the information model that later drives screens and flows.

## Traceability Tags

Apply one tag to every role, task, object, action, state, permission, and screen-relevant content item:

| Tag | Use when |
| --- | --- |
| `source-backed` | Directly supported by the PRD |
| `inferred` | Needed IA connective tissue based on source-backed facts |
| `unresolved` | Important but unclear or conflicting |
| `excluded` | Out of scope, not needed for IA, or deliberately not modeled |

Include source ids for `source-backed` and `inferred` items. Include a question for `unresolved` items.

## Required Model Artifacts

Build only artifacts needed by the PRD. The default set is:

1. Role and actor model.
2. Task model.
3. Domain object and content model.
4. Action model.
5. Object lifecycle and state model.
6. Permission model.

## Role And Actor Model

For each role:

| Field | Meaning |
| --- | --- |
| `role` | User, admin, reviewer, guest, system actor, or external actor |
| `goal` | What the role is trying to accomplish |
| `scope` | What part of the product they use |
| `permissions` | High-level access or control |
| `tag` | Traceability tag |
| `source/rationale` | Source id or assumption basis |

Do not create admin or reviewer roles unless the PRD implies governance, moderation, review, operations, or configuration.

## Task Model

For each task:

| Field | Meaning |
| --- | --- |
| `task` | User job or system-supported task |
| `actor` | Role that performs it |
| `trigger` | What starts the task |
| `object` | Primary object/content involved |
| `outcome` | Observable result |
| `priority` | `critical`, `important`, or `supporting` |
| `tag` | Traceability tag |

Prefer task language over feature language. A feature may support several tasks; a task may require several features.

## Domain Object And Content Model

For each object/content type:

| Field | Meaning |
| --- | --- |
| `object` | Noun the UI must expose or manipulate |
| `description` | Short definition |
| `owner/actor` | Role that creates or controls it |
| `key fields` | Only fields implied by IA, not database schema |
| `related objects` | Parent, child, dependency, or reference |
| `lifecycle states` | State names or unresolved marker |
| `tag` | Traceability tag |

Keep this at product IA level. Do not design database tables or API contracts.

## Action Model

Classify actions as needed:

- Create.
- View/read.
- Edit/update.
- Delete/archive.
- Submit/publish.
- Approve/reject/review.
- Assign/share/invite.
- Import/export.
- Search/filter/sort.
- Generate/regenerate.
- Configure.

For each action, identify actor, object, preconditions, resulting state, permission notes, and tag.

## Lifecycle And State Model

For each stateful object:

| Field | Meaning |
| --- | --- |
| `state` | User-visible or flow-critical state |
| `entry condition` | How the object enters this state |
| `available actions` | Actions allowed in this state |
| `next states` | Possible transitions |
| `visible to` | Roles that can see it |
| `tag` | Traceability tag |

Include only states that affect UI structure, permissions, flows, or state coverage.

## Permission Model

Create a compact matrix:

| Role | Object/Area | Can view | Can act | Restrictions | Source/tag |
| --- | --- | --- | --- | --- | --- |

Mark unresolved permissions instead of assuming broad access.

Completion check: every IA model item is tagged, every inferred item has a basis, and every unresolved item has a question.
