# English Learning AI Agent MVP Plan

## 1. Product Positioning

Lexis is an English learning application that turns vocabulary data from Maimemo into context-based reading lessons.

The MVP focuses on one core loop:

```text
Sync Maimemo vocabulary data
-> Build a vocabulary profile
-> Generate a structured reading lesson with AI
-> Let the user answer exercises
-> Provide immediate feedback
-> Save lesson history and Lexis context mastery state
```

Lexis does not replace Maimemo's spaced repetition system. Maimemo decides which words should be learned or reviewed. Lexis uses those words to help the learner transfer vocabulary into reading comprehension, grammar understanding, and controlled output.

## 2. Target User

The MVP targets learners preparing for postgraduate entrance English exams, especially learners around the CEFR B1/B2 transition.

The product assumes the learner already has some vocabulary foundation but struggles to use vocabulary in longer reading contexts, sentence analysis, and exam-style comprehension.

## 3. MVP Scope

The MVP must support:

- Email/password account registration and login.
- Per-user data isolation.
- A Maimemo sync architecture.
- A mock Maimemo adapter when the real adapter is not available.
- AI-generated fixed-structure reading lessons.
- Manual lesson generation, without forced daily completion.
- Lightweight word adjustment before lesson generation.
- Immediate per-question feedback.
- Final lesson summary.
- Lexis-owned context mastery state.
- Course history.
- Structured AI output with schema and rule validation.

The technical stack is not finalized in this plan.

## 4. Account And Data Ownership

The MVP is a multi-account product, not a local single-user tool.

Each user account owns its own:

- Maimemo connection configuration.
- Sync snapshots.
- Vocabulary profile.
- Generated lessons.
- Exercise answers.
- Feedback records.
- Lexis context mastery state.
- Lesson history.

All core persisted data must be scoped to a user identity, such as `userId` or an equivalent ownership field.

MVP authentication scope:

- Email/password registration and login.
- No WeChat login in MVP.
- WeChat login may be added later.
- No organization, class, admin, social, leaderboard, or multi-role permission system in MVP.

## 5. Maimemo Sync

The product must include a Maimemo sync architecture from the start.

### Vocabulary Snapshot Persistence For AI Generation

The sync snapshot is immutable input evidence for later lesson generation. Aggregate counts such as trackedWordCount are useful for display, but they are not sufficient for AI retrieval.

The preferred MVP direction is to persist normalized snapshot-word records containing the snapshot identity, user identity, exact word, and source category: new, fuzzy, practice, or mastered. This does not introduce a global word bank, embeddings, or vector retrieval. The existing aggregate vocabulary profile may remain as a read-optimized view of the latest snapshot.

The real Maimemo integration may be unavailable during early development, so the sync layer must be adapter-based:

```text
MaimemoSyncProvider
├─ MockMaimemoSyncProvider
└─ RealMaimemoSyncProvider
```

The mock adapter must return the same shape of data expected from the real adapter so the rest of the learning flow can be developed and tested.

The sync output must include:

- `newWords`: today's newly learned words.
- `reviewWords` or `fuzzyWords`: words Maimemo asks the learner to review today, or words considered uncertain.
- `masteredWordsSample`: a batch of mastered words that can participate in context generation.
- `trackedWordCount`: Maimemo study-record count for display and difficulty reference; it is not an exact mastered-word total.
- `dailyFinishedCount`, `dailyTotalCount`, `dailyStudyTimeMs`: Maimemo daily progress fields; beta data may be zero until the App initializes and auto-syncs the day.
- `fuzzyWords`: recent words whose response is `VAGUE`/`FORGET` or whose study tag is `STICKING`; ordinary review words are not automatically fuzzy.

The MVP strongly requires a mastered-word list sample, not only a mastered-word count. If the real Maimemo adapter cannot provide a mastered-word sample, that adapter is incomplete for the MVP.

Lexis reads Maimemo data but does not write learning results back to Maimemo.

## 6. Secret Handling

Maimemo credentials, tokens, cookies, or authorization data must be treated as secrets.

The MVP must not:

- Store Maimemo plaintext password.
- Store Maimemo plaintext token.
- Print credentials in logs.
- Expose sync credentials to the frontend.

The UI should only show connection state, such as connected, disconnected, failed, and last synced time.

AI Provider credentials are platform-managed in MVP:

- The platform uses one server-side AI Provider key.
- Users do not configure their own AI keys in MVP.
- Provider keys must stay in server-side environment or secret storage.
- Provider keys must not be stored in application database rows, exposed to frontend code, or logged.

Future versions may support other AI models or providers.

## 7. Vocabulary Profile

After sync, Lexis builds a vocabulary profile for the current user.

The profile distinguishes:

- Today's new words.
- Current review or fuzzy words.
- A sample of mastered words.
- Mastered word count.
- Lexis context mastery state from previous lessons.

Maimemo remains the source of scheduling truth. Lexis does not implement its own long-term spaced repetition planner in MVP.

Each lesson uses the latest synced Maimemo learning words for that user. Lexis may lightly filter or arrange the synced words for course generation, but it does not create an independent long-term review plan.

## 8. AI Lesson Generator

### Word Roles In Generation Context

The generation context must preserve word roles instead of passing only one flattened selected-words list:

- Required target words: a small set of words that must be used naturally.
- Priority words: words preferred for reuse when they fit the topic.
- Context words: words allowed to support the passage but not default explanation targets.
- Excluded words: words removed by the user or rejected by the selection policy.
- Source snapshot identity: the exact Maimemo snapshot used for generation.

This preserves the boundary between vocabulary selection and lesson generation, and prevents the model from treating every synchronized word as equally mandatory.

The AI lesson generator is a separate core module.

It receives a structured `LessonGenerationContext`, such as:

```text
examGoal
cefrLevel
newWords
fuzzyWords
masteredWordsSample
trackedWordCount
userWordAdjustments
generationConstraints
```

It outputs a structured `ContextLesson`.

The AI module must not directly depend on Maimemo implementation details. It should consume normalized vocabulary data so future data sources can be added without rewriting lesson generation logic.

## 9. AI Role And Output Contract

### Content And Exercise Traceability

Each exercise must be grounded in the reading content. The structured output should carry internal traceability fields for the source sentence or paragraph, target word, skill, and grading mode. These fields may be hidden from the learner-facing response but are required for validation and later quality evaluation.

AI role:

- Generate a short exam-oriented English reading passage.
- Use the synced vocabulary data to create meaningful context.
- Explain target vocabulary and grammar.
- Generate exercises.
- Evaluate user answers.
- Produce per-question feedback and a final summary.

AI input:

- User's exam target.
- User's CEFR level.
- Today's new words.
- Current fuzzy or review words.
- Mastered-word sample.
- User's light word adjustments.
- Lesson constraints.
- User answers during feedback.

AI output must be structured data, not free-form Markdown only.

The generated lesson must include:

- Reading passage.
- Unknown-word support table.
- Target vocabulary explanation.
- Grammar or long-sentence analysis.
- Vocabulary-in-context exercise.
- Sentence-structure exercise.
- Paragraph-logic exercise.
- Output exercise.
- Per-question answer key or evaluation criteria.
- Final lesson summary fields.

## 10. Lesson Generation Rules

### Naturalness And Word Selection Rules

The following rules refine the basic vocabulary requirements:

- Required target words must appear in the passage or a directly related exercise, with natural collocation and correct part of speech.
- Priority words should be used when they fit the selected context; the system may omit them when inclusion would make the passage unnatural.
- The generator must not force semantically unrelated words into one passage. If the selected words cannot form one coherent context, the selection step should reduce or regroup them before generation.
- A valid lesson must have a coherent topic, logical progression, CEFR-appropriate difficulty, non-repetitive phrasing, and target-word usage that sounds natural in context.

The default MVP target is:

```text
Exam goal: Postgraduate entrance English
Level: CEFR B1/B2 transition
```

Difficulty is controlled by both exam goal and CEFR level.

Article length must be dynamic by level and must never exceed 180 English words.

Recommended starting range:

| CEFR Level | Reading Length |
| --- | ---: |
| A1 | 50-70 words |
| A2 | 70-100 words |
| B1 | 100-140 words |
| B2 | 140-180 words |
| C1 | 160-180 words |
| C2 | 160-180 words |

For C1/C2, difficulty should increase mainly through sentence structure, abstraction, and logical density, not by making the passage longer.

Vocabulary rules:

- Today's new words should appear in the passage and be included in explanation or exercises.
- Fuzzy words should be prioritized for reuse and exercises.
- Mastered words should be used as context-building material.
- Mastered words are not default explanation or exercise targets.
- Extra unfamiliar words must not exceed 5.
- Extra unfamiliar words must have Chinese support.
- Inline Chinese translation should be used sparingly.
- The preferred support method is an unknown-word table below the article.

## 11. Lesson Interaction

The MVP uses a single course workspace as the main experience.

The workspace should include:

- Current user and learning target.
- Maimemo sync state.
- Today's new word count.
- Fuzzy or review word count.
- Mastered vocabulary count.
- Recommended word package for the next lesson.
- Lightweight word adjustment before generation.
- Generate lesson action.
- Current generated lesson.
- Exercise answer areas.
- Immediate feedback area.
- Final lesson summary.
- Recent lesson history entry point.

Lesson generation is manually triggered. The app must not require daily completion, enforce streaks, or punish skipped days.

Before generation, the user may lightly adjust the word package:

- Remove a small number of words.
- Add a word they want to practice.
- Keep the system's automatic selection by default.

The MVP should not include a complex word-bank management or advanced filtering interface.

## 12. Exercise Types

### Question Quality Rules

- Every question must be answerable from the reading passage or its explicitly stated output task.
- Multiple-choice distractors must be plausible, mutually distinguishable, and not depend on irrelevant tricks.
- The four exercise types must test different skills rather than repeat the same comprehension question.
- Objective exercises may use an answer key; output exercises must use criteria or a rubric instead of exact-string matching.

Every MVP lesson must include four exercise types:

- Vocabulary-in-context: test how a new or fuzzy word works in the passage.
- Sentence-structure: test long-sentence, clause, modifier, or sentence-main-structure understanding.
- Paragraph-logic: test main idea, author attitude, cause/effect, contrast, concession, or inference.
- Output practice: use 2-3 target words in a sentence, rewrite, or short expression task.

The product should avoid becoming a simple AI example-sentence generator. The exercises must connect vocabulary with reading, grammar, and context.

## 13. Feedback Flow

The MVP uses per-question immediate feedback plus a final summary.

Flow:

1. User reads the passage.
2. User answers the vocabulary-in-context exercise.
3. System gives immediate explanation and records vocabulary performance.
4. User answers the sentence-structure exercise.
5. System gives immediate sentence analysis and records grammar performance.
6. User answers the paragraph-logic exercise.
7. System gives immediate logic explanation and records comprehension performance.
8. User completes the output practice.
9. AI gives expression feedback.
10. System generates final summary.

The final summary should include:

- Words handled well.
- Words needing reuse.
- Weak grammar points.
- Reading logic weakness, if any.
- Suggested focus for the next generated lesson.

## 14. Lexis Context Mastery State

Lexis maintains its own context mastery state. It does not write back to Maimemo.

Maimemo state answers:

```text
When should this word be reviewed?
```

Lexis context mastery answers:

```text
Can the learner understand and use this word in reading context?
```

Suggested internal state fields:

- Maimemo source state.
- Lexis context mastery state.
- Last seen in lesson time.
- Correct count.
- Mistake count.
- Needs review flag.
- Weakness type.

Possible `weaknessType` values:

- Vocabulary meaning.
- Collocation or usage.
- Sentence structure.
- Paragraph logic.
- Output usage.

## 15. Course History

The MVP must save and allow the user to view historical lessons.

History should include:

- Sync snapshot used for the lesson.
- Generated lesson.
- User answers.
- Per-question feedback.
- Final summary.
- Lesson completion state.
- Generated time.

The MVP does not need:

- Weekly report.
- Monthly report.
- Streak chart.
- Ranking.
- Points system.
- Complex analytics dashboard.

## 16. Quality Validation

### Content Quality Gate

The first quality gate should be deterministic and local. It must additionally check required-word coverage using normalized words or approved inflections, target-word part of speech, unfamiliar-word support, exercise source traceability, grading-mode compatibility, and objective answer-key consistency.

Priority-word coverage should be reported separately from required-word coverage. A separate AI critique-and-repair pass may be added after the baseline validator and fixed regression cases are stable; it is not a prerequisite for the first content-quality slice.

AI generation must pass schema validation and rule validation before being shown as a valid lesson.

Minimum validation:

- Output matches expected schema.
- Passage length fits CEFR constraints.
- Passage length is not above 180 words.
- Required new words are covered.
- Required fuzzy words are covered where possible.
- Extra unfamiliar words are not above 5.
- Unknown-word support exists when needed.
- Four required exercise types exist.
- Grammar or long-sentence analysis exists.
- Final summary fields exist.

Invalid generations should be marked as failed and should allow regeneration. Bad AI output should not silently become a valid lesson.

## 16A. AI Generation Pipeline And Provider Boundary

The generation flow should be implemented as an application service rather than directly in an API route:

1. Load the latest immutable vocabulary snapshot.
2. Normalize, deduplicate, and classify candidate words.
3. Select required, priority, context, and excluded words.
4. Build a coherent topic and lesson constraint plan.
5. Call the configured LLMProvider for structured lesson generation.
6. Run schema, rule, and traceability validation.
7. Retry or regenerate only when the failure policy allows it.
8. Save lesson content, vocabulary provenance, and generation metadata.

LLMProvider remains the provider boundary. Provider-specific request construction, model identifiers, and response parsing must stay inside the provider adapter. The generation service should depend on typed input and output contracts, not on OpenRouter or any future provider API shape.

The MVP does not expose model selection in the frontend, but the backend should record provider name, model name, prompt version, schema version, latency, token usage, retry count, and validation results. This makes later model switching and offline quality comparison possible without changing ContextLesson semantics.

## 17. Non-Goals For MVP

The MVP explicitly does not include:

- Free-form AI Tutor chat.
- Writing learning results back to Maimemo.
- Lexis-owned spaced repetition or memory curve algorithm.
- Forced daily check-in or streak pressure.
- WeChat login.
- User-provided AI Provider keys.
- Multiple AI Provider management UI.
- Organization, class, friend, leaderboard, or admin system.
- Complex learning analytics.
- Listening, speaking, pronunciation scoring, ASR, or audio generation.
- Advanced word-bank management.

## 18. Risks

### AI Quality Evaluation Risk

Quality must also be evaluated against a small fixed set of cases covering target-word naturalness, CEFR fit, passage coherence, exercise differentiation, feedback usefulness, and summary relevance. The fixed cases are regression evidence; they do not replace runtime validation.

### Maimemo Interface Risk

The real Maimemo API, authorization model, sync stability, and available fields are not yet verified.

The largest product dependency is whether the real adapter can retrieve:

- Today's new words.
- Today's review or fuzzy words.
- A mastered-word sample.
- Mastered vocabulary count.

If mastered-word samples cannot be retrieved, the real adapter does not meet the current MVP requirement.

### Security Risk

The product stores user-owned learning records and may need Maimemo sync credentials. Authentication, authorization, secret handling, and data isolation must be treated as security-sensitive from the first implementation slice.

### AI Quality Risk

AI output may fail to follow vocabulary, length, structure, or exercise constraints. The MVP mitigates this through structured output, schema validation, and rule validation.

## 19. Open Questions

The following questions remain intentionally open for the next design pass:

- What is the maximum number of required target words for each lesson level and word-package size?
- Should the first quality slice use only deterministic validation, or also an optional critique-and-repair provider call?

- Which technical stack will be used?
- Which database will be used?
- Which auth implementation will be used?
- How will secrets be encrypted or stored?
- What exact fields can the real Maimemo adapter retrieve?
- How should CEFR levels map to sentence complexity, grammar scope, and Chinese support ratio?
- Which AI Provider and model should be used for the first implementation?
- What exact JSON schema should `ContextLesson` use?

## 20. Implementation Slice Recommendation

The content-quality work should be inserted into the implementation order as follows:

1. Snapshot-word persistence and vocabulary provenance.
2. Structured lesson and exercise traceability schema.
3. Deterministic lesson-quality validation and fixed regression cases.
4. Mock AI lesson generator through the generation service.
5. Real AI Provider integration with provider and model metadata.

The safest first implementation sequence is:

1. Account model and user-scoped data foundation.
2. Mock Maimemo sync adapter.
3. Vocabulary profile builder.
4. Structured lesson schema.
5. Mock AI lesson generator.
6. Course workspace UI.
7. Exercise answer and feedback flow.
8. Course history.
9. Schema and rule validation.
10. Real AI Provider integration.
11. Real Maimemo adapter investigation and integration.

This sequence keeps the learning loop testable before depending on the real Maimemo interface.
