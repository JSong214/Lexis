# Lexis 词汇语境学习 MVP PRD

## Status

Ready for review

## Source Summary

本 PRD 来源于：

- `English Learning AI Agent MVP Plan.md`
- 已确认的 `grill-me -> prd-handoff-ledger` 决策
- 用户对 Open Questions 的补充回答
- Maimemo OpenAPI 相关参考资料：
  - https://open.maimemo.com/#/
  - https://github.com/maimemo/memo-api-cli
  - https://github.com/maimemo/memo-skills/tree/main

本 PRD 只把 Maimemo 公开资料作为 adapter 设计参考，不把真实接口能力视为已经验证完成。

## Decision Ledger

| ID | Category | Statement | Source Pointer | PRD Use |
| --- | --- | --- | --- | --- |
| D1 | Confirmed Decision | Lexis 的核心闭环是同步墨墨词汇数据，生成语境阅读课程，逐题反馈，并保存学习历史和语境掌握状态。 | MVP Plan | requirement |
| D2 | Confirmed Decision | MVP 必须有 Maimemo sync 架构，并提供 `MockMaimemoSyncProvider`。 | MVP Plan | requirement |
| D3 | Confirmed Decision | 真实 Maimemo adapter 必须能提供今日新词、复习或模糊词、已掌握词样本、墨墨词汇记录总数。 | MVP Plan | requirement |
| D4 | Confirmed Decision | 课程生成手动触发，不强制每日完成。 | MVP Plan | requirement |
| D5 | Confirmed Decision | MVP 先做固定结构阅读课程，不做自由聊天式 AI Tutor。 | MVP Plan | requirement |
| D6 | Confirmed Decision | 课程必须覆盖词汇语境、句法理解、段落逻辑、输出练习四类题。 | MVP Plan | requirement |
| D7 | Confirmed Decision | AI 输出必须结构化，并通过 schema 校验和规则校验。 | MVP Plan | requirement |
| D8 | Confirmed Decision | Lexis 不写回墨墨，内部维护自己的语境掌握状态。 | MVP Plan | requirement |
| D9 | Confirmed Decision | MVP 需要账号系统，每个账号的数据独立隔离。 | MVP Plan | requirement |
| D10 | Confirmed Decision | 技术栈为 React + TypeScript 前端，Python + FastAPI 后端。 | 用户补充 | requirement |
| D11 | Confirmed Decision | 数据库为 PostgreSQL，ORM / Migration 为 SQLAlchemy 2.0 + Alembic。 | 用户补充 | requirement |
| D12 | Confirmed Decision | Auth 为邮箱/密码 + 后端 session + HttpOnly cookie。 | 用户补充 | requirement |
| D13 | Confirmed Decision | 平台 AI key 放后端环境变量；用户 Maimemo secret 加密入库，并预留用户 AI token 加密入库能力。 | 用户补充 | requirement |
| D14 | Confirmed Decision | AI Provider MVP 首选 OpenAI，使用 `LLMProvider` abstraction，并提供 `MockLLMProvider`。 | 用户补充 | requirement |
| D15 | Confirmed Decision | 后续提供模型切换能力，但 MVP 不做多模型 UI。 | 用户补充 | non-goal |
| D16 | Confirmed Decision | `ContextLesson` 只存 AI 生成课程内容。 | 用户补充 | requirement |
| D17 | Confirmed Decision | `LessonAttempt` / `ExerciseFeedback` 存用户作答、逐题反馈和最终总结。 | 用户补充 | requirement |
| D18 | Confirmed Decision | MVP 完整支持 CEFR A1-C2，每个等级都要有生成约束、校验规则和测试样例。 | 用户补充 | requirement |
| D19 | Confirmed Decision | 主要用户更正为 CEFR 全阶段学习者。 | 用户补充 | requirement |
| R1 | Risk | Maimemo 真实 adapter 字段需要基于开放平台、memo-api-cli 和 memo-skills 继续验证。 | 用户补充 + 参考资料 | risk |
| R2 | Risk | 账号、session、HttpOnly cookie、加密 secret 和用户数据隔离是安全敏感面。 | MVP Plan + 用户补充 | risk |

## Problem

英语学习者在背单词工具中积累了词汇学习数据，但常见问题是词汇掌握停留在单词层面，不能稳定迁移到阅读语境、句法分析、段落逻辑理解和主动表达中。

Lexis 要解决的问题是：基于用户在墨墨背单词中的当日学习数据，把今日新词、复习或模糊词、已掌握词样本转化为一节可完成、可反馈、可追踪的语境阅读课程。

## Goals

- 支持用户登录后同步自己的 Maimemo 学习数据。
- 使用 Maimemo 当日学习词生成结构化英语阅读课程。
- 让 CEFR A1-C2 全阶段学习者都能获得匹配能力等级的课程。
- 将词汇学习和阅读理解、句法理解、段落逻辑、输出练习结合。
- 保存用户课程历史、作答记录、逐题反馈和最终总结。
- 维护 Lexis 自有的语境掌握状态，但不写回 Maimemo。
- 用结构化输出、schema 校验、规则校验控制 AI 生成质量。
- 以 mock provider 支撑真实 Maimemo / OpenAI 集成前的端到端开发和测试。

## Non-Goals

- MVP 不做自由聊天式 AI Tutor。
- MVP 不写回 Maimemo 学习状态。
- MVP 不自建记忆曲线或长期复习调度。
- MVP 不强制每日打卡，不做 streak 压力机制。
- MVP 不做微信登录，后续可扩展。
- MVP 不做多模型 UI，后续可扩展模型切换。
- MVP 不让用户配置自己的 AI key，但数据模型预留用户 AI token 加密入库能力。
- MVP 不做组织、班级、好友、排行榜、管理员后台。
- MVP 不做听力、口语、发音评分、ASR、音频生成。
- MVP 不做复杂学习报表、周报、月报、积分系统。
- MVP 不做高级词库管理或复杂筛选器。

## Users And Actors

### Primary User

CEFR A1-C2 全阶段英语学习者。

用户可以有不同考试目标或学习目标，但 MVP 的核心体验始终是：把 Maimemo 当日词汇数据转成语境阅读课程。

### External Systems

- Maimemo OpenAPI：提供词汇、学习进度、今日学习项、学习记录等数据参考。
- OpenAI：MVP 首选 AI Provider。

### Internal Actors

- Frontend：React + TypeScript。
- Backend：Python + FastAPI。
- Auth/session layer：邮箱/密码登录，后端 session，HttpOnly cookie。
- Database：PostgreSQL。
- ORM / Migration：SQLAlchemy 2.0 + Alembic。
- Sync layer：`MaimemoSyncProvider`。
- AI layer：`LLMProvider`。

## Scope

### Must Have

- 邮箱/密码注册登录。
- 后端 session + HttpOnly cookie。
- 用户数据隔离。
- Maimemo 连接配置和加密 secret 存储。
- `MockMaimemoSyncProvider`。
- `RealMaimemoSyncProvider` 接口边界。
- `MockLLMProvider`。
- OpenAI-backed `LLMProvider`。
- 词汇画像构建。
- 课程生成工作台。
- 手动触发课程生成。
- 生成前轻量调整词包。
- CEFR A1-C2 生成约束。
- CEFR A1-C2 校验规则。
- CEFR A1-C2 测试样例。
- 结构化 `ContextLesson`。
- `LessonAttempt` 和 `ExerciseFeedback`。
- 逐题即时反馈。
- 最终总结。
- 课程历史查看。
- Lexis 语境掌握状态。
- schema 校验和规则校验。

### Confirmed Follow-Up

- 微信登录。
- 多模型 UI。
- 模型切换功能。
- 用户自带 AI token。
- 更完整的学习统计和长期趋势。

## User Journey

1. 用户注册或登录 Lexis。
2. 用户进入课程工作台。
3. 用户配置 Maimemo 连接，secret 加密保存。
4. 用户点击同步 Maimemo。
5. 系统获取并保存本次 sync snapshot。
6. 系统展示今日新词、复习或模糊词、已掌握词样本、墨墨词汇记录总数。
7. 用户在生成前轻量调整词包。
8. 用户点击生成课程。
9. 系统调用 `LLMProvider` 生成结构化 `ContextLesson`。
10. 系统执行 schema 校验和规则校验。
11. 校验通过后展示文章、陌生词辅助表、语法分析和四类练习。
12. 用户逐题作答。
13. 系统保存 `LessonAttempt` 和 `ExerciseFeedback`，并展示即时反馈。
14. 用户完成课程后，系统生成最终总结。
15. 系统更新 Lexis 语境掌握状态。
16. 用户可在课程历史中查看该课程和反馈。

## Functional Requirements

### Account And Auth

- FR1: 系统必须支持邮箱/密码注册和登录。
- FR2: 系统必须使用后端 session 管理登录态。
- FR3: 登录态 cookie 必须为 HttpOnly。
- FR4: 所有用户数据必须按用户隔离。
- FR5: 未登录用户不得访问同步、课程生成、课程历史、作答反馈等功能。

### Secret Handling

- FR6: 平台 OpenAI key 必须放在后端环境变量或服务端 secret storage 中。
- FR7: 用户 Maimemo secret 必须加密入库。
- FR8: 系统必须预留用户 AI token 加密入库的数据边界，但 MVP 不提供多模型 UI 或 BYOK 流程。
- FR9: Maimemo secret、AI key、用户 AI token 不得返回到前端，不得写入普通日志。

### Maimemo Sync

- FR10: 系统必须定义 `MaimemoSyncProvider` abstraction。
- FR11: 系统必须提供 `MockMaimemoSyncProvider`，用于无真实接口时跑通完整闭环。
- FR12: 系统必须预留 `RealMaimemoSyncProvider`。
- FR13: 同步输出必须标准化为 `newWords`、`reviewWords` 或 `fuzzyWords`、`masteredWordsSample`、`trackedWordCount`。
- FR13a: Settings 必须允许当前用户保存账号级 `CEFR` 与学习目标，并在后续课程生成中使用这些偏好。
- FR13b: `CEFR` 仅允许 A1-C2；学习目标仅允许 General English、CET-4、CET-6、IELTS、TOEFL、Postgraduate Entrance English、Academic English、Workplace English。
- FR14: `masteredWordsSample` 是 MVP 必需数据。若真实接口无法提供，真实 adapter 不算完成。
- FR15: Lexis 不得调用 Maimemo 写入学习状态。

### Vocabulary Profile

- FR16: 系统必须基于最新 sync snapshot 构建用户词汇画像。
- FR17: 词汇画像必须区分今日新词、复习或模糊词、已掌握词样本、墨墨词汇记录总数。
- FR18: Lexis 不得自建长期复习调度；复习调度由 Maimemo 决定。
- FR19: 每次课程默认只使用最新同步的当日学习词。

### Lesson Generation

- FR20: 系统必须定义 `LessonGenerationContext`。
- FR21: `LessonGenerationContext` 至少包含 `examGoal`、`cefrLevel`、`newWords`、`fuzzyWords`、`masteredWordsSample`、`trackedWordCount`、`userWordAdjustments`、`generationConstraints`。
- FR22: 系统必须定义 `LLMProvider` abstraction。
- FR23: MVP 必须提供 `MockLLMProvider`。
- FR24: MVP 首选 OpenAI-backed provider。
- FR25: AI 输出必须为结构化数据。
- FR26: `ContextLesson` 只存 AI 生成的课程内容，不存用户作答或反馈。

### CEFR Constraints

- FR27: MVP 必须完整支持 CEFR A1-C2。
- FR28: 每个 CEFR level 必须有生成约束。
- FR29: 每个 CEFR level 必须有校验规则。
- FR30: 每个 CEFR level 必须有测试样例。
- FR31: 文章最长不得超过 180 英文词。
- FR32: 额外陌生词不得超过 5 个。
- FR33: 额外陌生词必须提供中文辅助。

建议初始长度范围：

| CEFR Level | Reading Length |
| --- | ---: |
| A1 | 50-70 words |
| A2 | 70-100 words |
| B1 | 100-140 words |
| B2 | 140-180 words |
| C1 | 160-180 words |
| C2 | 160-180 words |

### Lesson Content

- FR34: 课程必须包含阅读文章。
- FR35: 课程必须包含陌生词辅助表。
- FR36: 课程必须包含目标词解释。
- FR37: 课程必须包含语法或长难句分析。
- FR38: 课程必须包含词汇语境题。
- FR39: 课程必须包含句法理解题。
- FR40: 课程必须包含段落逻辑题。
- FR41: 课程必须包含输出练习题。
- FR42: 今日新词必须优先进入讲解或练习。
- FR43: 复习或模糊词必须优先进入复现或练习。
- FR44: 已掌握词只作为语境构建材料，不默认作为讲解或练习对象。

### Interaction And Feedback

- FR45: 课程生成必须由用户手动触发。
- FR46: 系统不得强制用户每日完成课程。
- FR47: 用户生成课程前可以轻量调整词包。
- FR48: 用户每提交一道题后，系统必须返回即时反馈。
- FR49: `LessonAttempt` 必须保存用户作答。
- FR50: `ExerciseFeedback` 必须保存逐题反馈。
- FR51: 最终总结必须保存到 `LessonAttempt` 或关联反馈记录中。
- FR52: 完成课程后，系统必须更新 Lexis 语境掌握状态。

### History

- FR53: 系统必须保存课程历史。
- FR54: 用户必须能查看自己的历史课程。
- FR55: 历史课程必须能展示生成课程内容、用户作答、逐题反馈、最终总结。

### Validation

- FR56: 系统必须对 AI 输出执行 schema 校验。
- FR57: 系统必须对 AI 输出执行规则校验。
- FR58: 规则校验必须覆盖文章长度、CEFR 范围、目标词覆盖、额外陌生词数量、四类题完整性、语法分析、最终总结字段。
- FR59: 校验失败的课程不得被标记为有效课程。
- FR60: 校验失败时，系统必须给出失败状态，并允许重新生成。

## AI Behavior Contract

### AI Role

AI 负责把 Maimemo 同步后的词汇数据转化为 CEFR 匹配的英语阅读课程，并对用户作答提供逐题反馈和最终总结。

### AI Inputs

- 用户考试目标或学习目标。
- 用户 CEFR level。
- 今日新词。
- 复习或模糊词。
- 已掌握词样本。
- 墨墨词汇记录总数。
- 用户生成前轻量调整。
- CEFR 生成约束。
- 用户作答。

### AI Outputs

- `ContextLesson`：AI 生成的课程内容。
- `ExerciseFeedback`：逐题反馈。
- Final summary：最终总结。

### AI Constraints

- 不生成自由聊天内容。
- 不把已掌握词作为默认重点讲解对象。
- 不使用超过约束数量的额外陌生词。
- 不超过当前 CEFR level 的长度与难度约束。
- 不在输出中包含 secret、token、内部 prompt、服务端配置。

## Data Boundary

### Allowed Data Sources

- 用户在 Lexis 内的账号和学习记录。
- 用户授权后的 Maimemo sync data。
- 平台 OpenAI provider。
- mock adapter / mock provider 测试数据。

### Disallowed Uses

- 不读取未授权用户数据。
- 不跨用户共享课程、作答、反馈或 secret。
- 不把用户 Maimemo secret 发送给前端。
- 不把平台 AI key 写入数据库。
- 不写回 Maimemo 学习状态。

## Data, API, And Technical Notes

### Tech Stack

- Frontend：React + TypeScript。
- Backend：Python + FastAPI。
- Database：PostgreSQL。
- ORM / Migration：SQLAlchemy 2.0 + Alembic。
- Auth：邮箱/密码 + 后端 session + HttpOnly cookie。
- AI：OpenAI + `LLMProvider` abstraction + `MockLLMProvider`。

### Suggested Core Entities

- `User`
- `Session`
- `MaimemoConnection`
- `MaimemoSyncSnapshot`
- `VocabularyProfile`
- `ContextLesson`
- `LessonAttempt`
- `ExerciseFeedback`
- `ContextMasteryState`
- `LLMCallLog`

### Entity Boundaries

- `ContextLesson` 只保存 AI 生成的课程内容。
- `LessonAttempt` 保存用户对某节课的一次学习过程和最终总结。
- `ExerciseFeedback` 保存每道题的作答、评分或反馈。
- `ContextMasteryState` 保存 Lexis 内部语境掌握状态。
- `MaimemoSyncSnapshot` 保存同步快照，便于追溯某节课使用了哪些词。

### Maimemo Adapter Reference

参考资料显示，`memo-api-cli` 使用 `https://open.maimemo.com/open/` 作为 OpenAPI base URL，并通过 Bearer token 访问；CLI 暴露了 `study progress`、`study today`、`study records`、`study add`、`study advance` 等学习记录命令。当前 PRD 只使用读能力，不要求写入 Maimemo。

参考类型中可见：

- `StudyProgress`: `finished`、`total`、`study_time`
- `StudyTodayItem`: `voc_id`、`voc_spelling`、`order`、`first_response`、`is_new`、`is_finished`
- `StudyRecord`: `voc_id`、`voc_spelling`、`add_date`、`first_study_date`、`last_study_date`、`next_study_date`、`last_response`、`study_count`、`tags`
- `Vocabulary`: `id`、`spelling`

MVP adapter 需要把这些字段或可用等价字段归一化为 Lexis 的 `newWords`、`fuzzyWords`、`masteredWordsSample`、`trackedWordCount`。

`trackedWordCount` 来自 `query_study_records(as_count=true)`，表示墨墨学习记录总量。官方 API 未提供精确的已掌握词总数，因此 UI 不把该数值表述为精确的已掌握词总数。

字段映射采用墨墨官方 `StudyResponse` 语义：`newWords` 来自 `StudyTodayItem.is_new=true`；`fuzzyWords` 来自当日或历史记录中的 `VAGUE`、`FORGET`，以及 `StudyRecord.tags=STICKING`；`masteredWordsSample` 来自 `WELL_FAMILIAR`。普通 `StudyRecord` 查询最多返回 1000 条，因此模糊词与熟知词是近期样本，不表示完整账号统计。

同步同时调用 `get_study_progress`，保存 `dailyFinishedCount`、`dailyTotalCount`、`dailyStudyTimeMs`。如果用户当天未在墨墨 App 初始化或未开启自动同步，这些公测字段可能为零或不准确。

## Fallbacks

- Maimemo 未连接：展示未连接状态，允许使用 mock 数据进行开发或演示。
- Maimemo 同步失败：保存失败状态和错误类型，不清空用户历史课程。
- OpenAI 调用失败：标记生成失败，允许用户重试。
- AI 输出 schema 失败：不展示为有效课程，提示重新生成。
- 规则校验失败：标记失败原因，例如长度超限、题型缺失、陌生词过多。
- 用户未完成课程：保存 attempt draft 或未完成状态，不强制完成。

## Observability

系统应记录：

- Maimemo sync 成功/失败、错误类型、耗时。
- LLM 调用成功/失败、模型名、token 用量、耗时、错误类型。
- AI 输出校验结果。
- 课程生成状态。
- 用户提交练习和反馈生成状态。

系统不得记录：

- Maimemo plaintext secret。
- 平台 AI key。
- 用户 AI token。
- session secret。

## Cost And Latency

MVP 不设定明确 token 成本或延迟阈值，但需要保存 LLM 调用耗时和 token 用量，作为后续模型切换、成本控制和体验优化的基础。

## Privacy And Compliance

- 用户学习数据、作答记录、反馈和 Maimemo secret 都属于用户私有数据。
- 所有用户数据访问必须经过身份校验。
- 服务端调用 OpenAI 时，发送给 AI Provider 的内容应限制在生成课程和反馈所需范围内。
- secret 必须支持后续轮换、撤销或删除。

## User Stories

- 作为学习者，我希望登录后只看到自己的同步记录和课程历史，以保护我的学习隐私。
- 作为学习者，我希望同步 Maimemo 当日学习词，从而不用手动整理今天要练的词。
- 作为学习者，我希望系统把新词、模糊词和已掌握词组成一篇适合我 CEFR 等级的短阅读。
- 作为学习者，我希望每道题提交后立即看到解释，而不是等到整节课结束才知道错因。
- 作为学习者，我希望查看历史课程，复盘之前的文章、作答和反馈。
- 作为开发者，我希望 mock Maimemo 和 mock LLM 能跑通完整闭环，从而不被外部 API 阻塞。

## Acceptance Criteria

- AC1: 未登录用户访问课程工作台时被要求登录。
- AC2: 用户 A 无法读取用户 B 的 sync snapshot、lesson、attempt、feedback、context mastery state。
- AC3: Maimemo secret 加密入库，API 响应不返回明文 secret。
- AC4: 使用 `MockMaimemoSyncProvider` 时，可以生成包含新词、模糊词、已掌握词样本的词汇画像。
- AC5: 使用 `MockLLMProvider` 时，可以生成一节通过 schema 校验的 `ContextLesson`。
- AC6: 每个 CEFR level A1-C2 都有至少一个生成约束测试样例。
- AC7: 任一课程文章超过 180 英文词时，规则校验失败。
- AC8: 额外陌生词超过 5 个时，规则校验失败。
- AC9: 缺少任一四类练习题时，规则校验失败。
- AC10: 校验失败的课程不能进入用户历史中的有效课程列表。
- AC11: 用户逐题提交后，系统保存作答和反馈。
- AC12: 用户完成课程后，系统保存最终总结。
- AC13: 历史课程页面能展示课程内容、用户作答、逐题反馈和最终总结。
- AC14: OpenAI 调用失败时，系统展示生成失败状态并允许重试。
- AC15: 日志中不出现 Maimemo plaintext secret、平台 AI key 或用户 AI token。

## Testing Strategy

Confidence: high

### Unit Tests

- CEFR A1-C2 生成约束。
- AI 输出 schema 校验。
- 规则校验：长度、额外陌生词、题型完整性、目标词覆盖。
- Maimemo sync response normalization。
- Secret encryption/decryption boundary。

### Integration Tests

- 邮箱/密码登录 + session + HttpOnly cookie。
- 用户数据隔离。
- Mock Maimemo sync -> VocabularyProfile -> MockLLM -> ContextLesson。
- LessonAttempt + ExerciseFeedback 保存流程。
- 历史课程查询。

### E2E Tests

- 用户注册登录。
- 同步 mock Maimemo 数据。
- 生成课程。
- 完成四类练习。
- 查看最终总结。
- 重新打开历史课程。

### Security Tests

- 未登录访问拦截。
- 跨用户访问阻断。
- secret 不出现在前端响应。
- secret 不出现在普通日志。

## Risks And Mitigations

### R1: Maimemo Real Adapter Risk

风险：真实 OpenAPI 字段、授权方式、限制和 mastered word sample 能力仍需验证。

缓解：

- 先实现 adapter abstraction。
- 使用 mock adapter 跑通闭环。
- 将 `masteredWordsSample` 作为真实 adapter 完成标准。
- 只读 Maimemo，不写回学习状态。

### R2: AI Quality Risk

风险：AI 输出可能不满足课程结构、CEFR 难度、词汇覆盖或题型要求。

缓解：

- 强制结构化输出。
- schema 校验。
- 规则校验。
- 校验失败不展示为有效课程。
- CEFR A1-C2 均提供测试样例。

### R3: Security Risk

风险：账号、session、HttpOnly cookie、Maimemo secret、平台 AI key 涉及安全敏感面。

缓解：

- 用户数据按 user scope 查询。
- Maimemo secret 加密入库。
- 平台 AI key 只在后端环境变量或 secret storage。
- 普通日志不得输出 secret。
- 安全测试进入 MVP 验收。

### R4: Scope Risk

风险：支持 CEFR A1-C2 会扩大课程生成和测试范围。

缓解：

- 每个等级先定义最小生成约束、校验规则和测试样例。
- 不在 MVP 中加入自由聊天、多模型 UI、复杂报表和听说功能。

## Open Questions

- OpenAI MVP 使用的具体 model 尚未确定。
- `ContextLesson` 的最终 JSON schema 需要在实现前定稿。
- Maimemo real adapter 是否能稳定得到 `masteredWordsSample` 仍需验证。
- 用户 AI token 加密入库的具体启用时机和 UI 不在 MVP 中确定。
- CEFR 到语法范围、句法复杂度、中文辅助比例的详细映射需要在实现设计中细化。

## References

- Maimemo OpenAPI: https://open.maimemo.com/#/
- maimemo/memo-api-cli: https://github.com/maimemo/memo-api-cli
- maimemo/memo-skills: https://github.com/maimemo/memo-skills/tree/main
