# Publishing Targets

Publishing is a side effect. Do not write files, create issues, update trackers, add labels, or modify existing documents unless the user explicitly asks for that action.

## Default Target

If the user says only "generate", "draft", "create", "turn this into", or "make a PRD", respond in chat.

## File Writes

Write or update a file only when the user explicitly asks to write, save, update, or place the PRD somewhere.

Before writing:

- Use the exact path the user provides.
- If no path is provided, ask one target question and stop.
- If updating an existing file, read it first.
- Preserve unrelated content unless the user asks for replacement.

## Issues And Trackers

Create or publish an issue only when the user explicitly asks to create, publish, file, or open an issue or tracker item.

Before publishing:

- Confirm the destination repo or tracker is discoverable from context.
- Do not add `ready-for-agent`, triage, priority, milestone, or area labels unless the user explicitly asks for them or the source workflow explicitly requires them.
- If a requested connector or CLI is unavailable, say so and provide the PRD content instead.

## Unsafe Or Ambiguous Side Effects

Ask one target question and stop when:

- The target repo, project, file path, or tracker is ambiguous.
- The user requested an update but several existing PRD or issue candidates match.
- The PRD has a blocking readiness gap.

Do not infer a side effect from the skill name.
