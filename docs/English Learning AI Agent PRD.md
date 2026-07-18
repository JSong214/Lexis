# Lexis 词汇语境学习 MVP PRD

## Status

Ready for implementation planning

## Source Summary

本 PRD 来源于：

- `English Learning AI Agent MVP Plan.md`
- 已确认的 `grill-me -> prd-handoff-ledger` 决策
- 用户对 Open Questions 的补充回答
- Maimemo OpenAPI 相关参考资料：
  - https://open.maimemo.com/#/
  - https://github.com/maimemo/memo-api-cli
  - https://github.com/maimemo/memo-skills/tree/main

本次同步还纳入 2026-07-15 至 2026-07-16 `grill-me` 会话中确认的 knowledge-first 生成转向，以及此前确认的 AI 生成质量、词汇快照持久化、生成流程和模型切换预留要求。

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
| D20 | Confirmed Decision | Sync snapshot 是后续课程生成的不可变输入证据；除统计数量外，必须保留具体词项、用户归属、snapshot 归属和来源类别。MVP 不引入全局词库、embedding 或 vector retrieval。 | 当前会话确认 + MVP Plan §5 | requirement |
| D21 | Superseded Decision | 旧版 required、priority、context、excluded 角色模型已由 D29 的 `Anchor/Support/Deferred/Excluded` 模型替代；source snapshot identity 约束继续有效。 | 当前会话确认 + MVP Plan §8 | superseded |
| D22 | Superseded Decision | 旧版 required/priority 自然度规则已由 D29-D30 的候选集合、核心词上限和延后机制替代；不得强行拼接语义无关内容的约束继续有效。 | 当前会话确认 + MVP Plan §10 | superseded |
| D23 | Confirmed Decision | 每道题必须保留文章句子或段落、目标词、能力类型和 grading mode 等内部可追溯信息；output 题使用 criteria 或 rubric，不使用精确字符串匹配。 | 当前会话确认 + MVP Plan §§9, 12 | requirement |
| D24 | Confirmed Decision | 第一阶段质量门禁以本地、确定性校验为主；critique-and-repair 不是第一阶段的必要调用。 | 当前会话确认 + MVP Plan §16 | requirement |
| D25 | Confirmed Decision | 生成流程由独立 application service 编排，provider-specific 请求和响应解析留在 LLMProvider adapter 内；记录 provider、model、prompt/schema version、耗时、token、重试和校验结果。 | 当前会话确认 + MVP Plan §16A | requirement |
| D26 | Confirmed Decision | 使用固定回归样例评估目标词自然度、CEFR 适配、文章连贯性、题目区分度、反馈有效性和总结相关性。 | 当前会话确认 + MVP Plan §18 | requirement |
| D27 | Confirmed Decision | Lexis 的首要内容价值从“覆盖选词的文章”转为“用户愿意读完、能够复述一个核心观点的知识情境”；词汇学习通过该情境自然发生。 | 2026-07-15/16 `grill-me` | requirement |
| D28 | Confirmed Decision | 课程生成前必须依次执行 Word Enrichment、Topic Proposal、关系与自然度校验、用户确认和 Knowledge Brief 构建，再生成 `ContextLesson`。 | 2026-07-15/16 `grill-me` | requirement |
| D29 | Confirmed Decision | 用户选词是候选集合，不是全部进入同一篇正文的硬约束；课程使用 `Anchor words`、`Support words`、`Deferred words`、`Excluded words` 四类角色。 | 2026-07-15/16 `grill-me` | requirement |
| D30 | Confirmed Decision | 每个 `TopicProposal` 允许只使用 1 个 `Anchor word`；CEFR 数量范围是推荐值而非硬性下限，仍按等级执行上限。用户可轻量调整，但系统必须阻止无词义或关系证据的 Anchor。 | 2026-07-17 用户确认 | requirement |
| D31 | Confirmed Decision | 完整课程生成前先展示 2-3 个结构化 `TopicProposal`；每个提案必须说明核心问题、知识点、选用词义、词汇角色和关系链。 | 2026-07-15/16 `grill-me` | requirement |
| D32 | Confirmed Decision | Word Enrichment 优先使用稳定 lexical source；生产环境遇到未覆盖词时，使用已配置的 `LLMProvider` 生成结构化 `WordSemanticProfile` 并通过 schema、词义和关系规则校验。固定 lexical fixtures 仅用于 Mock 与回归测试；MVP 不使用长期兴趣画像影响内容选题。 | 2026-07-17 用户确认 | requirement |
| D33 | Confirmed Decision | 主题规划优先匹配有限、经过整理且保留来源的 evergreen knowledge library。无匹配时可生成仅讨论词义、语法、搭配、语域或语境用法的 language-focused 提案；不得借此生成无来源支持的外部事实、研究、统计或历史主张，无关选词必须标记为 `Deferred` 而非强行关联。 | 2026-07-17 用户确认 | requirement |
| D34 | Confirmed Decision | 每节课只承载一个核心知识点和最多 1-2 个辅助事实；核心知识来源在文章末尾以可展开方式展示。 | 2026-07-15/16 `grill-me` | requirement |
| D35 | Confirmed Decision | 内容使用固定骨架 `核心问题 -> 具体场景 -> 知识揭示 -> 结果/启发`；MVP 只支持解释型场景、微型案例和对比型内容。 | 2026-07-15/16 `grill-me` | requirement |
| D36 | Confirmed Decision | 核心问题在阅读前展示；用户预测完全可选，并可直接阅读或揭示答案。 | 2026-07-15/16 `grill-me` | requirement |
| D37 | Confirmed Decision | 知识理解和词汇迁移必须分开评价；知识题不强制使用目标词，output 题要求在新场景中自然使用至少一个指定 `Anchor word`，MVP 采用相同核心词义的近迁移。 | 2026-07-15/16 `grill-me` | requirement |
| D38 | Confirmed Decision | 主题提案和完整课程分别设置质量门禁；任一门禁失败时不得展示低质量内容，应改推其他提案或请求用户调整词包。 | 2026-07-15/16 `grill-me` | requirement |
| R1 | Risk | Maimemo 真实 adapter 字段需要基于开放平台、memo-api-cli 和 memo-skills 继续验证。 | 用户补充 + 参考资料 | risk |
| R2 | Risk | 账号、session、HttpOnly cookie、加密 secret 和用户数据隔离是安全敏感面。 | MVP Plan + 用户补充 | risk |

## Problem

英语学习者在背单词工具中积累了词汇学习数据，但常见问题是词汇掌握停留在单词层面，不能稳定迁移到阅读语境、句法分析、段落逻辑理解和主动表达中。

现有“用户选词后由 AI 直接生成文章”的路径还引入了第二个问题：用户所选词项可能来自不同词义和语义领域，模型为了覆盖全部词汇容易生成主题牵强、搭配不自然、知识价值不足的文章。Schema、长度和词汇覆盖校验只能证明内容结构完整，不能证明内容值得阅读。

Lexis 要解决的问题是：基于用户在墨墨背单词中的当日学习数据，先理解选词的词义与关系，再优先从可靠的 evergreen knowledge、或在无匹配时从可校验的语言知识中构建一个有核心问题、可复述知识点和自然词汇语境的短课程，并提供可反馈、可追踪的知识理解与词汇迁移练习。

## Goals

- 支持用户登录后同步自己的 Maimemo 学习数据。
- 使用 Maimemo 当日学习词生成结构化、knowledge-first 的英语阅读课程。
- 让 CEFR A1-C2 全阶段学习者都能获得匹配能力等级的课程。
- 将词汇学习和阅读理解、句法理解、段落逻辑、输出练习结合。
- 让每节课围绕一个核心问题和一个可复述的知识点展开。
- 通过 Word Enrichment 和可解释的关系链判断词汇是否适合同一主题。
- 在完整课程生成前提供 2-3 个可选择、可解释的主题提案。
- 优先以稳定 lexical source 和 evergreen knowledge library 约束词义与外部事实；对未覆盖词使用结构化、可校验的 AI language fallback。
- 分开评价知识理解与目标词在新语境中的迁移能力。
- 保存用户课程历史、作答记录、逐题反馈和最终总结。
- 维护 Lexis 自有的语境掌握状态，但不写回 Maimemo。
- 用结构化输出、schema 校验、规则校验控制 AI 生成质量。
- 减少目标词强行植入和文章表达不自然的问题。
- 保留词汇来源与生成过程 provenance，支持后续模型切换和质量比较。
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
- MVP 不引入 embedding、vector retrieval 或全局词库检索。
- MVP 不要求 critique-and-repair 调用作为课程生成的必要阶段。
- MVP 不做高级词库管理或复杂筛选器。
- MVP 不使用长期兴趣画像或兴趣偏好影响课程选题。
- MVP 不生成实时新闻、价格、政策、医学建议或依赖实时验证的知识内容。
- MVP 不允许 AI 在无可靠来源时生成外部事实主题；language fallback 只能讨论词义、语法、搭配、语域和语境用法。
- MVP 不构建通用知识图谱；知识库只保存课程所需的主题、事实、来源、兼容词义和关系定义。
- MVP 不做多角色对话、悬疑解谜、分支任务或连续剧式内容。

## Users And Actors

### Primary User

CEFR A1-C2 全阶段英语学习者。

用户可以有不同考试目标或学习目标，但 MVP 的核心体验始终是：把 Maimemo 当日词汇数据转成语境阅读课程。

### External Systems

- Maimemo OpenAPI：提供词汇、学习进度、今日学习项、学习记录等数据参考。
- OpenAI：MVP 首选 AI Provider。
- Lexical source：优先提供稳定的词义、词性、搭配、语域和难度信息；未覆盖词由已配置的 `LLMProvider` 生成结构化 semantic profile。

### Internal Actors

- Frontend：React + TypeScript。
- Backend：Python + FastAPI。
- Auth/session layer：邮箱/密码登录，后端 session，HttpOnly cookie。
- Database：PostgreSQL。
- ORM / Migration：SQLAlchemy 2.0 + Alembic。
- Sync layer：`MaimemoSyncProvider`。
- AI layer：`LLMProvider`。
- Vocabulary enrichment layer：构建 `WordSemanticProfile`。
- Topic planning layer：匹配知识主题、生成 `TopicProposal` 并执行关系校验。
- Knowledge library layer：提供 `KnowledgeTopic`、`KnowledgeBrief` 和 source provenance。

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
- `LexicalSource` abstraction；versioned lexical fixtures 仅供 Mock 与回归测试。
- 生产环境通过 `LLMProvider` 为 lexical source 未覆盖的任意 Maimemo 词生成结构化 `WordSemanticProfile` 与 language-focused `TopicProposal`。
- Versioned evergreen knowledge fixtures，支持 Mock 环境跑通 curated factual topic 流程。
- 词汇画像构建。
- 课程生成工作台。
- 手动触发课程生成。
- 生成前轻量调整词包。
- Word Enrichment：补充词义、词性、搭配、语域、领域和难度信息。
- `Anchor words`、`Support words`、`Deferred words`、`Excluded words` 角色选择。
- 2-3 个结构化 `TopicProposal` 及词汇关联解释。
- 用户选择主题并轻量调整 `Anchor words`。
- 有限、经过整理的 evergreen factual knowledge library，以及无匹配时受限的 language-focused fallback。
- 每节课一个 `KnowledgeBrief` 及来源 provenance。
- 阅读前核心问题、可选预测、直接揭示答案能力和阅读后 `KnowledgeTakeaway`。
- 解释型场景、微型案例和对比型内容三种 MVP 内容形式。
- CEFR A1-C2 生成约束。
- CEFR A1-C2 校验规则。
- CEFR A1-C2 测试样例。
- 结构化 `ContextLesson`。
- `LessonAttempt` 和 `ExerciseFeedback`。
- 逐题即时反馈。
- 最终总结。
- 课程历史查看。
- Lexis 语境掌握状态。
- 按 sync snapshot 保存可追溯的 normalized snapshot-word records。
- 第一阶段本地确定性质量门禁和固定回归样例。
- 生成流程与 provider/model 运行元数据记录。
- schema 校验和规则校验。

### Confirmed Follow-Up

- AI critique-and-repair 作为后续可选质量增强，不属于第一阶段必需流程。
- Trusted source retrieval 和带引用的实时知识模式。
- 扩大 evergreen knowledge library 的主题范围。
- 多角色对话、悬疑解谜、分支任务和连续剧式内容。
- 用户长期兴趣画像和兴趣驱动选题。
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
5a. 系统将本次 snapshot 中的具体词项按来源类别归一化保存，并保留用户和 snapshot 归属。
6. 系统展示今日新词、复习或模糊词、已掌握词样本、墨墨词汇记录总数。
7. 用户从当前词汇画像中选择候选词；候选词不等于必须全部进入同一节课。
8. 系统优先通过 lexical source 构建或读取 `WordSemanticProfile`；未覆盖词由已配置的 `LLMProvider` 生成结构化 profile，并接受 schema 与规则校验。
9. 系统优先从 evergreen knowledge library 匹配候选 `KnowledgeTopic`，为每个候选主题选择具体词义并建立关系链。
10. 无 curated factual topic 匹配时，系统生成 2-3 个仅限词义、语法、搭配、语域或语境用法的 language-focused 提案；不同方向可各使用 1 个 `Anchor word`，其余无关词标记为 `Deferred`。
11. 系统展示 2-3 个 `TopicProposal`，包括标题、核心问题、知识点、内容形式、选用词义、`Anchor words`、`Support words`、关系解释和暂缓词。
12. 用户选择一个提案，可轻量调整 `Anchor words`；至少保留 1 个有明确词义与关系证据的 Anchor，破坏关联性的调整必须显示警告。
13. 系统确定 `Anchor words`、`Support words`、`Deferred words`、`Excluded words`，构建 `LessonGenerationContext`，并保留 source snapshot identity。
14. 系统为所选提案构建 `KnowledgeBrief`：curated factual topic 保存外部来源；language-focused fallback 保存 provider/model provenance，且事实边界只允许语言知识。两者均限定一个核心知识点和最多 1-2 个辅助事实。
15. 系统调用 `LLMProvider`，根据固定内容骨架和选定内容形式生成结构化 `ContextLesson`。
16. 系统执行 schema 校验、规则校验和完整课程质量门禁；内容不得引入 `KnowledgeBrief` 之外的核心事实。
17. 校验通过后展示核心问题。用户可以选择预测，也可以直接阅读或揭示答案。
18. 系统展示文章、陌生词辅助、语法分析、`KnowledgeTakeaway`、可展开知识来源和四类练习。
19. 用户逐题作答；知识理解题不强制使用目标词，output 题要求在新场景中自然使用至少一个指定 `Anchor word`。
20. 系统保存 `LessonAttempt` 和 `ExerciseFeedback`，并展示即时反馈。
21. 用户完成课程后，系统生成最终总结并更新 Lexis 语境掌握状态。
22. 用户可在课程历史中查看主题、来源、课程内容、作答和反馈。

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

- FR19a: 系统必须保存本次 sync snapshot 中参与课程选择的具体词项，并记录用户、snapshot 和来源类别。
- FR19b: 来源类别至少区分 new、fuzzy、practice、mastered；trackedWordCount 仅作为统计值，不得替代具体词项。
- FR19c: 课程必须能够追溯到生成时使用的 source snapshot identity。
- FR20: 系统必须定义 `LessonGenerationContext`。
- FR21: `LessonGenerationContext` 至少包含 `examGoal`、`cefrLevel`、source snapshot identity、候选词、`WordSemanticProfile`、词汇角色、用户调整、所选 `TopicProposal`、`KnowledgeBrief` 和 generation constraints。
- FR22: 系统必须定义 `LLMProvider` abstraction。
- FR23: MVP 必须提供 `MockLLMProvider`。
- FR24: MVP 首选 OpenAI-backed provider。
- FR25: AI 输出必须为结构化数据。
- FR26: `ContextLesson` 只存 AI 生成的课程内容，不存用户作答或反馈。

- FR21a: `LessonGenerationContext` 必须区分 `Anchor words`、`Support words`、`Deferred words`、`Excluded words`。
- FR21b: `Anchor words` 必须按所选词义自然出现在文章或直接关联的练习中；`Support words` 只在适合主题时使用；`Deferred words` 留待后续课程；`Excluded words` 不得进入本次生成上下文。
- FR21c: 课程生成必须通过独立 application service 编排；LLMProvider adapter 负责 provider-specific 请求、模型标识和响应解析。
- FR21d: 系统必须记录 provider name、model name、prompt version、schema version、耗时、token usage、retry count 和 validation results。
- FR21e: 系统必须优先通过稳定 lexical source 构建或读取 `WordSemanticProfile`；未覆盖词可以交给已配置的 `LLMProvider` 生成结构化 profile，但 topic planner 不得在 profile 未通过 schema 与规则校验前直接使用裸词。
- FR21f: `WordSemanticProfile` 至少包含 lemma、可能词义、part of speech、常见搭配、语域、semantic domain 和难度；多义词必须保留候选词义。
- FR21g: 系统必须先尝试从 evergreen knowledge library 生成 2-3 个 curated factual `TopicProposal`；无匹配时，可由 `LLMProvider` 生成 2-3 个 language-focused 提案，但不得包含无来源支持的外部事实。
- FR21h: `TopicProposal` 至少包含标题、核心问题、核心知识点、内容形式、所选词义、词汇角色、关系链、暂缓词和关联解释。
- FR21i: 每个 `Anchor word` 必须绑定一个明确词义和主题角色；明显存在多个可行词义时，系统应提供不同主题方向；无法消除歧义时不得将该词设为 `Anchor word`。
- FR21j: 多个 Anchor 必须通过共同语义框架或可解释关系链连接；仅共享宽泛 domain tag 不足以证明主题匹配。单 Anchor 提案仍必须提供明确 sense 与关系证据。
- FR21k: 每个提案至少使用 1 个 `Anchor word`，并遵守对应 CEFR 等级上限；CEFR 数量范围是推荐值而非硬性下限。其余候选词必须进入 support、deferred 或 excluded 角色。
- FR21l: 用户可以在提案阶段轻量调整 `Anchor words`；如果调整会破坏主题关系链，系统必须显示警告并阻止低质量课程生成。
- FR21m: 所选主题必须生成结构化 `KnowledgeBrief`，至少包含一个核心事实、最多 1-2 个辅助事实、因果或解释关系、provenance 和不可超出的事实边界；language-focused brief 只能包含可校验的语言事实。
- FR21n: 无法匹配知识库主题时，系统必须优先生成受限的 language-focused 提案；无法形成可靠词义与关系证据时，才拆分、延后或请求用户调整词包。
- FR21o: CEFR 约束语言难度和 Anchor 上限，并提供 Anchor 推荐数量；学习目标只约束练习或表达任务。二者不得作为长期兴趣信号替代词义关系和 topic 匹配。

术语迁移说明：现有实现中的 `required_target_words` 对应 `Anchor words`；`priority_words` 与 `context_words` 迁移为保留 source category 的 `Support words`；`Deferred words` 为新增角色；`excluded_words` 对应 `Excluded words`。本 PRD 以新角色名称为 canonical terminology。

### CEFR Constraints

- FR27: MVP 必须完整支持 CEFR A1-C2。
- FR28: 每个 CEFR level 必须有生成约束。
- FR29: 每个 CEFR level 必须有校验规则。
- FR30: 每个 CEFR level 必须有测试样例。
- FR30a: 每个 `TopicProposal` 至少包含 1 个 `Anchor word`；任何等级均不得超过其 CEFR 上限，所有等级的绝对上限为 5。
- FR30b: 不同 CEFR level 使用以下推荐 `Anchor words` 数量范围；低于推荐下限时允许继续，但 UI 必须明确提示：

| CEFR Level | Recommended Anchor Words |
| --- | ---: |
| A1 | 2-3 |
| A2 | 2-3 |
| B1 | 3-4 |
| B2 | 3-4 |
| C1 | 4-5 |
| C2 | 4-5 |

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

- FR44a: 目标词使用必须满足基本词义、词性和语境搭配要求；文章必须具备连贯主题、逻辑推进和 CEFR 匹配度。
- FR44b: 每道练习题必须能由文章内容或明确的 output task 支撑；题目必须记录 source sentence 或 paragraph、target word、skill 和 grading mode 等内部 traceability。
- FR44c: objective 题使用 answer key；output 题使用 criteria 或 rubric，不使用 exact-string matching。
- FR44d: 每节课必须包含一个核心问题、一个核心知识点和最多 1-2 个辅助事实。
- FR44e: 内容必须遵循 `核心问题 -> 具体场景 -> 知识揭示 -> 结果/启发` 的固定骨架。
- FR44f: MVP 的 `contentMode` 仅允许 explanatory scenario、micro case、comparison 三种值。
- FR44g: `ContextLesson` 至少包含 topic identity、content mode、core question、reading text、selected word senses and roles、`KnowledgeTakeaway`、knowledge sources、词汇辅助、语法分析和四类练习。
- FR44h: 核心知识来源必须在文章末尾以默认收起、可展开的方式展示，不在正文中逐句打断阅读。
- FR44i: 文章不得引入 `KnowledgeBrief` 之外的核心事实，也不得把不确定或实时信息表述为稳定知识。
- FR44j: `KnowledgeTakeaway` 必须用简洁语言重述核心知识点，并与阅读前核心问题直接对应。

### Interaction And Feedback

- FR45: 课程生成必须由用户手动触发。
- FR46: 系统不得强制用户每日完成课程。
- FR47: 用户生成课程前可以选择候选词；系统必须在完整课程生成前展示 2-3 个通过门禁的 `TopicProposal`。
- FR47a: 用户必须选择一个 `TopicProposal`，并可以轻量调整 `Anchor words`；系统必须展示关联性警告。
- FR47b: 阅读前必须展示核心问题；预测为可选操作，用户可以直接阅读或揭示答案。
- FR47c: 知识理解题只检查用户是否理解核心知识，不得强制使用目标词。
- FR47d: Output 题必须要求用户在新场景中自然使用至少一个指定 `Anchor word`，MVP 使用相同核心词义的近迁移。
- FR47e: 知识理解与词汇迁移必须返回可区分的评分或反馈，不能合并成一个模糊结果。
- FR48: 用户每提交一道题后，系统必须返回即时反馈。
- FR49: `LessonAttempt` 必须保存用户作答。
- FR50: `ExerciseFeedback` 必须保存逐题反馈。
- FR51: 最终总结必须保存到 `LessonAttempt` 或关联反馈记录中。
- FR52: 完成课程后，系统必须更新 Lexis 语境掌握状态。

### History

- FR53: 系统必须保存课程历史。
- FR54: 用户必须能查看自己的历史课程。
- FR55: 历史课程必须能展示所选主题、核心问题、知识来源、生成课程内容、用户作答、逐题反馈和最终总结。
- FR55a: 历史课程必须保留生成时的词义选择、词汇角色、source snapshot identity 和 knowledge topic identity，避免后续词典或知识库更新改变历史解释。

### Validation

- FR56: 系统必须对 AI 输出执行 schema 校验。
- FR57: 系统必须对 AI 输出执行规则校验。
- FR57a: 系统必须分别校验 `TopicProposal`、`KnowledgeBrief` 和 `ContextLesson`，不得把全部风险推迟到完整课程生成之后。
- FR58: 规则校验必须覆盖文章长度、CEFR 范围、`Anchor words` 数量与覆盖、选定词义、额外陌生词数量、核心问题、`KnowledgeTakeaway`、知识来源、四类题完整性、语法分析和最终总结字段。
- FR59: 校验失败的课程不得被标记为有效课程。
- FR60: 校验失败时，系统必须给出失败状态，并允许重新生成。

- FR61: 完整课程质量门禁必须检查 anchor-word coverage、approved inflection、所选词义、part of speech、collocation、陌生词中文辅助、题目 traceability、grading mode 和 objective answer key 一致性。
- FR61a: 主题提案门禁必须检查词义是否明确、每个 `Anchor word` 是否有 sense 与 relation evidence、多 Anchor 是否形成可解释关系链、规划模式是否为 curated factual 或受限 language-focused、核心问题是否能由 `KnowledgeBrief` 回答，以及内容形式是否属于 MVP 允许值。
- FR61b: 完整课程门禁必须检查文章是否严格基于 `KnowledgeBrief`、是否只承载一个核心知识点、是否具备固定内容骨架、`KnowledgeTakeaway` 是否回答核心问题，以及知识理解和词汇迁移练习是否分离。
- FR61c: 任一门禁失败时不得展示低质量内容；系统必须改推其他提案、减少或重新分组词汇，或请求用户调整词包。
- FR62: 系统必须维护固定回归样例，覆盖词义选择、关系链完整性、知识事实边界、目标词自然度、CEFR 适配、文章连贯性、题目区分度、知识理解、词汇近迁移、反馈有效性和总结相关性。
- FR62a: 固定回归样例必须包含多义词、不可关联词组、知识库无匹配、用户破坏关联性的调整和课程事实越界等失败案例。
- FR63: critique-and-repair 调用不是第一阶段课程生成的必要条件；是否增加该阶段保留为 Open Question。

## AI Behavior Contract

### AI Role

AI 负责优先在 lexical source 和 evergreen knowledge library 的边界内为用户选词提出可解释主题；未覆盖时，AI 可生成结构化 semantic profile 和仅限语言知识的提案。AI 把已确认的 `KnowledgeBrief` 转化为 CEFR 匹配的英语阅读课程，并对用户作答提供逐题反馈和最终总结，但不得自行扩展事实边界。

### AI Inputs

- 用户考试目标或学习目标。
- 用户 CEFR level。
- 最新 sync snapshot 中的候选词、来源类别和 snapshot identity。
- 候选词对应的 `WordSemanticProfile`。
- evergreen knowledge library 中允许匹配的 `KnowledgeTopic`。
- 用户所选 `TopicProposal`。
- `Anchor words`、`Support words`、`Deferred words`、`Excluded words`。
- 用户在提案阶段的轻量调整。
- 带来源和事实边界的 `KnowledgeBrief`。
- 允许的 content mode。
- CEFR 生成约束。
- 用户作答。

### AI Outputs

- `TopicProposal`：完整课程生成前的结构化主题提案及关联解释。
- `ContextLesson`：AI 生成的课程内容。
- `ExerciseFeedback`：逐题反馈。
- Final summary：最终总结。

### AI Constraints

- 不生成自由聊天内容。
- 不把已掌握词作为默认重点讲解对象。
- 不使用长期兴趣画像决定主题。
- 不在 evergreen knowledge library 之外生成外部事实主题；language-focused fallback 不得包含研究、统计、历史事实或其他无来源主张。
- 不引入 `KnowledgeBrief` 之外的核心事实。
- 不为了覆盖全部候选词强行拼接语义无关内容。
- 不把未消除歧义的多义词设为 `Anchor word`。
- 不使用超过约束数量的额外陌生词。
- 不超过当前 CEFR level 的长度与难度约束。
- 不在输出中包含 secret、token、内部 prompt、服务端配置。

## AI Generation Quality Addendum

### Word Selection And Naturalness

- Sync snapshot 是课程生成的不可变输入证据。
- 用户选词是候选集合，不是全部进入正文的硬约束。
- `Anchor words` 是必须按选定词义自然处理的少量核心词。
- `Support words` 只在适合当前主题时使用，不默认作为解释或练习目标。
- `Deferred words` 留待后续课程，不算本次生成失败。
- `Excluded words` 不得进入本次生成上下文。
- 生成器不得为了覆盖词汇将语义无关的词强行拼接在一篇文章中。
- 有效课程必须具备连贯主题、逻辑推进、CEFR 匹配度和非重复表达。

### Word Enrichment And Topic Matching

- 稳定 lexical source 优先提供词义、词性、搭配、语域、domain 和难度等语义事实，不根据用户兴趣决定主题。
- 对 lexical source 未覆盖的词，`LLMProvider` 必须一次返回所有选词的结构化 `WordSemanticProfile`，并接受 exact-word coverage、schema、sense 和 relation evidence 校验。
- `WordSemanticProfile` 必须保留多义词候选；每个提案必须展示实际选用的 sense。
- `KnowledgeTopic` 必须保存 compatible word senses 和 relation types，使每个 `Anchor word` 都能映射到主题角色。
- 仅共享 Science、Society 等宽泛 domain tag 不足以建立主题；词汇必须形成共同 semantic frame 或可解释关系链。
- 无 knowledge library 匹配时，模型可以按不同词义方向生成 language-focused 提案，并把未使用词标为 `Deferred`；不得为凑齐多词而补造关联。
- 无可靠 sense 或 relation evidence 时，系统必须拆分、延后或拒绝生成。

### Knowledge Brief And Content Shape

- `KnowledgeTopic` 至少保存核心问题、核心知识点、事实、来源、compatible word senses、relation types、CEFR range 和 supported content modes。
- `KnowledgeBrief` 每次只选择一个核心知识点和最多 1-2 个辅助事实。
- 正文使用 `核心问题 -> 具体场景 -> 知识揭示 -> 结果/启发` 的固定骨架。
- 知识来源在正文末尾以可展开区域展示，正文保持连续阅读体验。
- MVP 只允许 explanatory scenario、micro case 和 comparison 三种 content mode。

### Exercise Traceability

每道题必须关联文章句子或段落、目标词、能力类型和 grading mode。Multiple-choice 选项应当具有合理干扰性且彼此可区分；四类题必须考察不同能力。知识理解题可以不绑定 target word，只验证用户是否理解核心知识或因果关系。Output 题必须绑定至少一个指定 `Anchor word`，使用 criteria 或 rubric 检查相同核心词义在新场景中的自然用法，并允许合理的非唯一答案。

### Generation Pipeline And Model Boundary

生成流程依次执行 snapshot 加载、候选词归一化、稳定 lexical/curated knowledge 匹配、必要时 structured language fallback、2-3 个 `TopicProposal` 生成、词义关系与自然度门禁、用户确认、词汇角色确定、`KnowledgeBrief` 构建、结构化 `ContextLesson` 生成、schema/rule/traceability/knowledge-boundary 校验、按策略重试，以及课程内容、词义选择、planning mode、知识来源、词汇 provenance 和生成元数据保存。

LLMProvider 是 provider boundary。MVP 不提供前端模型选择 UI，但后端必须记录 provider、model、prompt version、schema version、latency、token usage、retry count 和 validation results，以支持后续模型切换和离线质量比较。

### Evaluation

固定回归样例至少覆盖多义词 sense 选择、词汇关系链、知识库匹配与无匹配 fallback、知识事实边界、`Anchor words` 自然度、CEFR 适配、文章连贯性、知识理解题、词汇近迁移、题目区分度、反馈有效性和总结相关性。固定样例用于回归验证，不替代运行时 schema/rule/traceability/knowledge-boundary 校验，也不预设尚未确认的评分阈值。

## Data Boundary

### Allowed Data Sources

- 用户在 Lexis 内的账号和学习记录。
- 用户授权后的 Maimemo sync data。
- 稳定 lexical source 提供的词义、词性、搭配、语域、domain 和难度信息。
- 已配置 `LLMProvider` 对用户当前所选词生成的结构化 semantic profile 与 language-focused proposal；不得附带不必要的用户身份或学习历史。
- 经过整理的 evergreen knowledge library 及其 source provenance。
- 平台 OpenAI provider。
- mock adapter / mock provider 测试数据。

### Disallowed Uses

- 不读取未授权用户数据。
- 不跨用户共享课程、作答、反馈或 secret。
- 不把用户 Maimemo secret 发送给前端。
- 不把平台 AI key 写入数据库。
- 不写回 Maimemo 学习状态。
- 不使用长期兴趣画像影响 MVP 主题选择。
- 不把未经可靠来源支持的外部事实写入 `KnowledgeBrief`；language-focused brief 只允许词义、语法、搭配、语域和语境用法事实。
- 不在 MVP 课程生成时调用实时新闻或开放网络检索作为事实来源。

## Data, API, And Technical Notes

### Tech Stack

- Frontend：React + TypeScript。
- Backend：Python + FastAPI。
- Database：PostgreSQL。
- ORM / Migration：SQLAlchemy 2.0 + Alembic。
- Auth：邮箱/密码 + 后端 session + HttpOnly cookie。
- AI：OpenAI + `LLMProvider` abstraction + `MockLLMProvider`。
- Vocabulary semantics：稳定 lexical source 优先，structured `LLMProvider` fallback + `WordSemanticProfile`。
- Knowledge grounding：curated evergreen knowledge library + source provenance；无匹配时使用受限 language-focused brief + provider provenance。

### Suggested Core Entities

- `User`
- `Session`
- `MaimemoConnection`
- `MaimemoSyncSnapshot`
- `VocabularyProfile`
- `WordSemanticProfile`
- `KnowledgeTopic`
- `KnowledgeSource`
- `TopicProposal`
- `KnowledgeBrief`
- `ContextLesson`
- `LessonAttempt`
- `ExerciseFeedback`
- `ContextMasteryState`
- `LLMCallLog`

- `VocabularySnapshotWord`
- `LessonGenerationMetadata` 或等价的 generation metadata 记录

### Entity Boundaries

- `WordSemanticProfile` 保存词汇的稳定语义信息和候选词义，不保存用户掌握状态。
- `KnowledgeTopic` 保存经过整理的主题、核心问题、事实、兼容词义、关系类型、CEFR 范围和允许的 content mode。
- `KnowledgeSource` 保存知识来源信息，并与具体 facts 关联。
- `TopicProposal` 保存或表示一次生成前主题候选、选定词义、词汇角色、关系链和关联解释；它不是有效课程。
- `KnowledgeBrief` 是生成某节课的不可变知识输入，限定核心事实、辅助事实、来源和事实边界。
- `ContextLesson` 只保存 AI 生成的课程内容及其 topic/brief/source references，不保存用户作答或反馈。
- `LessonAttempt` 保存用户对某节课的一次学习过程和最终总结。
- `ExerciseFeedback` 保存每道题的作答、评分或反馈。
- `ContextMasteryState` 保存 Lexis 内部语境掌握状态。
- `MaimemoSyncSnapshot` 保存同步快照，便于追溯某节课使用了哪些词。

- `VocabularySnapshotWord` 保存 snapshot 中的具体词项、用户归属和来源类别，支持课程生成 provenance。
- `LessonGenerationMetadata` 保存各阶段 provider/model、版本、耗时、token、重试和校验结果；最终字段布局仍可在实现设计中确定。

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
- Lexical source 未覆盖或不可用：优先使用带版本的缓存 semantic profile；无可靠缓存时调用已配置 `LLMProvider` 生成结构化 profile，校验失败则停止主题规划。
- Evergreen knowledge library 无匹配或不可用：切换为受限的 language-focused 规划，不生成外部事实主题。
- 词包无法形成多词可靠关系：为不同词义方向生成独立提案，允许只使用 1 个 Anchor，其余词进入 `Deferred`。
- 任一选词无法获得可靠 sense 或 relation evidence：移除对应提案并请求用户重试或调整词包。
- OpenAI 调用失败：标记对应 Topic Proposal、课程、反馈或总结阶段失败，允许用户重试。
- `TopicProposal` 或 `ContextLesson` schema 失败：不展示为有效提案或课程，按阶段重新生成。
- 规则校验失败：标记失败原因，例如长度超限、题型缺失、陌生词过多。
- 用户调整破坏关系链：展示关联性警告，恢复推荐词组或要求重新选择主题。
- 主题提案门禁失败：移除该提案并尝试其他 curated 或 language-focused 提案；没有合格提案时请求调整词包。
- 完整课程门禁失败：课程保持失败状态并允许重试，不得作为有效课程展示。
- critique-and-repair 尚未启用：不阻塞第一阶段生成流程。
- 用户未完成课程：保存 attempt draft 或未完成状态，不强制完成。

## Observability

系统应记录：

- Maimemo sync 成功/失败、错误类型、耗时。
- Lexical source 名称、数据版本、缓存命中和 Word Enrichment 状态。
- 匹配到的 knowledge topic identity、提案数量和提案拒绝原因。
- 每个提案的选定词义、词汇角色、关系校验结果和用户选择结果。
- `KnowledgeBrief`、knowledge source version 和事实边界校验结果。
- Topic Proposal 与完整课程两阶段质量门禁结果。
- LLM 调用成功/失败、模型名、token 用量、耗时、错误类型。
- provider name、model name、prompt/schema version、retry count 和 validation results。
- AI 输出校验结果。
- 课程生成状态。
- 用户提交练习和反馈生成状态。

系统不得记录：

- Maimemo plaintext secret。
- 平台 AI key。
- 用户 AI token。
- session secret。

## Cost And Latency

MVP 不设定明确 token 成本或延迟阈值，但必须按 Word Enrichment、Topic Proposal、ContextLesson、feedback 和 summary 阶段分别记录耗时、调用次数和 token 用量。先生成轻量 Topic Proposal 再生成完整课程，用于减少主题不合格时的完整生成浪费。

## Privacy And Compliance

- 用户学习数据、作答记录、反馈和 Maimemo secret 都属于用户私有数据。
- 所有用户数据访问必须经过身份校验。
- 调用 lexical source 时只发送完成词义查询所需的词项，不发送用户身份、snapshot identity、学习记录或 secret。
- Evergreen knowledge library 不得包含用户私有学习数据。
- 服务端调用 OpenAI 时，发送给 AI Provider 的内容应限制在生成课程和反馈所需范围内。
- secret 必须支持后续轮换、撤销或删除。

## User Stories

- 作为学习者，我希望登录后只看到自己的同步记录和课程历史，以保护我的学习隐私。
- 作为学习者，我希望同步 Maimemo 当日学习词，从而不用手动整理今天要练的词。
- 作为学习者，我希望系统解释哪些词能够自然支持同一个知识主题，而不是把所有选词强行写进一篇文章。
- 作为学习者，我希望在生成完整课程前从 2-3 个主题提案中选择一个，并看见具体词义、核心问题和关联原因。
- 作为学习者，我希望能够轻量调整核心词，并在调整会破坏主题时得到明确提醒。
- 作为学习者，我希望每节课围绕一个值得了解、能够复述的知识点展开，并符合我的 CEFR 等级。
- 作为学习者，我希望阅读后能够查看核心知识来源，区分 AI 改写内容和事实依据。
- 作为学习者，我希望系统分别告诉我是否理解知识，以及是否能在新场景中自然使用目标词。
- 作为学习者，我希望每道题提交后立即看到解释，而不是等到整节课结束才知道错因。
- 作为学习者，我希望查看历史课程，复盘之前的主题、知识来源、文章、作答和反馈。
- 作为开发者，我希望 mock Maimemo、lexical fixtures、knowledge fixtures 和 mock LLM 能跑通完整闭环，从而不被外部 API 阻塞。

## Acceptance Criteria

- AC1: 未登录用户访问课程工作台时被要求登录。
- AC2: 用户 A 无法读取用户 B 的 sync snapshot、lesson、attempt、feedback、context mastery state。
- AC3: Maimemo secret 加密入库，API 响应不返回明文 secret。
- AC4: 使用 `MockMaimemoSyncProvider` 时，可以生成包含新词、模糊词、已掌握词样本的词汇画像。
- AC5: 使用 mock Maimemo、lexical fixtures、knowledge fixtures 和 `MockLLMProvider` 时，可以从选词生成主题提案、确认主题并得到一节通过校验的 `ContextLesson`。
- AC6: 每个 CEFR level A1-C2 都有至少一个生成约束测试样例。
- AC7: 任一课程文章超过 180 英文词时，规则校验失败。
- AC8: 额外陌生词超过 5 个时，规则校验失败。
- AC9: 缺少任一四类练习题时，规则校验失败。
- AC10: 校验失败的课程不能进入用户历史中的有效课程列表。
- AC11: 用户逐题提交后，系统保存作答和反馈。
- AC12: 用户完成课程后，系统保存最终总结。
- AC13: 历史课程页面能展示所选主题、核心问题、知识来源、词义和角色 provenance、课程内容、用户作答、逐题反馈和最终总结。
- AC14: OpenAI 调用失败时，系统展示生成失败状态并允许重试。
- AC15: 日志中不出现 Maimemo plaintext secret、平台 AI key 或用户 AI token。

- AC16: sync snapshot 中参与课程生成的具体词项按来源类别持久化，并可追溯到用户和 snapshot。
- AC17: 生成请求能够区分 `Anchor words`、`Support words`、`Deferred words`、`Excluded words`；未进入本课的候选词不会被强行写入正文。
- AC18: 课程题目包含内部 source traceability 和 grading mode；知识理解题不强制使用目标词，output 题使用 criteria 或 rubric 评价指定 `Anchor word` 的近迁移。
- AC19: 生成记录包含 provider/model、prompt/schema version、latency、token usage、retry count 和 validation results。
- AC20: 固定回归样例覆盖词义选择、关系链、知识事实边界、目标词自然度、CEFR 适配、文章连贯性、知识理解、词汇近迁移、题目区分度、反馈有效性和总结相关性。
- AC21: 每个候选词在主题匹配前都有包含候选 sense、part of speech、collocation、domain 和难度的 `WordSemanticProfile`；fixture 未覆盖的生产词由已配置的 `LLMProvider` 生成结构化 profile。
- AC22: 完整课程生成前展示 2-3 个通过门禁的 `TopicProposal`，每个提案包含核心问题、知识点、内容形式、词义、词汇角色、关系链和关联解释。
- AC23: 无 knowledge library 匹配时，系统生成 2-3 个仅限语言知识的提案；无关词被拆分或标记为 `Deferred`，提案不包含无来源外部事实。
- AC24: 每个提案允许 1 个 `Anchor word`；CEFR 数量范围作为推荐值展示，生成只硬性执行至少 1 个和对应等级上限。
- AC25: 用户调整会破坏主题关系链时，系统显示警告且不生成低质量课程。
- AC26: 有效 `ContextLesson` 只包含一个核心知识点、最多 1-2 个辅助事实，并包含 core question、content mode、`KnowledgeTakeaway` 和可展开 knowledge sources。
- AC27: 用户可以在阅读前选择预测、直接阅读或直接揭示答案，预测不是完成课程的前置条件。
- AC28: 知识理解题不因未使用目标词而判错；output 题要求在新场景中自然使用至少一个指定 `Anchor word`。
- AC29: Topic Proposal 门禁能够拒绝把只共享宽泛 domain、但没有 semantic frame 或关系链的多个词同时设为 Anchor；单 Anchor 仍须具有明确 sense 与 relation evidence。
- AC30: 完整课程门禁能够拒绝引入 `KnowledgeBrief` 之外核心事实的内容。
- AC31: 历史课程保留生成时的 topic、brief、source、词义、词汇角色和 snapshot provenance。

## Testing Strategy

Confidence: high

### Unit Tests

- CEFR A1-C2 生成约束。
- `Anchor words` 至少 1 个、各 CEFR 上限和推荐数量提示。
- `WordSemanticProfile` 归一化、多义词候选和 lexical cache 行为。
- `TopicProposal` schema、词义绑定、词汇角色和关系链校验。
- `KnowledgeBrief` schema、核心/辅助事实数量和 source boundary。
- `ContextLesson` schema、core question、content mode、`KnowledgeTakeaway` 和 knowledge sources。
- 规则校验：长度、额外陌生词、题型完整性、anchor coverage、选定词义和事实边界。
- Maimemo sync response normalization。
- Secret encryption/decryption boundary。

### AI Quality Tests

- `Anchor/Support/Deferred/Excluded` 角色选择和 snapshot provenance。
- 多义词 sense 选择、共同 semantic frame、关系链完整性和宽泛 domain 假阳性。
- 2-3 个提案的差异性、可解释性，以及 curated knowledge identity 或 language fallback planning mode。
- 无主题匹配、用户破坏关系链和 facts 越界的拒绝行为。
- Anchor coverage、approved inflection、part of speech 和 collocation 校验。
- 核心问题、固定内容骨架、单一知识点和 `KnowledgeTakeaway` 一致性。
- 知识理解题、词汇近迁移、source traceability、题型区分度和 output rubric。
- provider/model generation metadata 和失败重试状态。
- 固定回归样例的知识准确性、自然度、CEFR、连贯性、题目、反馈和总结评估。

### Integration Tests

- 邮箱/密码登录 + session + HttpOnly cookie。
- 用户数据隔离。
- Mock Maimemo sync -> VocabularyProfile -> curated fixture 或 structured language fallback -> TopicProposal。
- 用户确认 TopicProposal -> KnowledgeBrief -> MockLLM -> ContextLesson。
- Topic Proposal gate 和完整课程 gate 的失败状态与 fallback。
- LessonAttempt + ExerciseFeedback 保存流程。
- 历史课程查询。

### E2E Tests

- 用户注册登录。
- 同步 mock Maimemo 数据。
- 选择候选词并查看 2-3 个主题提案。
- 查看词义、词汇角色和关联解释。
- 选择主题并轻量调整 `Anchor words`。
- 生成 knowledge-first 课程。
- 直接阅读或可选预测核心问题。
- 完成四类练习。
- 分别查看知识理解和词汇迁移反馈。
- 展开查看知识来源。
- 查看最终总结。
- 重新打开历史课程。

### Security Tests

- 未登录访问拦截。
- 跨用户访问阻断。
- Lexical source 请求不包含用户身份、snapshot identity、学习记录或 secret。
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

### R2a: AI Content Quality Risk

风险：模型可能选择错误词义、虚构词汇关联、为了覆盖候选词生成牵强内容，或生成与知识核心无关的题目。

缓解：

- 生成前使用稳定 lexical source 或已校验的 structured AI fallback，并始终形成 `WordSemanticProfile`。
- 使用 `Anchor/Support/Deferred/Excluded` 角色限制核心词数量。
- 完整课程前执行 Topic Proposal 关系与自然度门禁。
- 生成后执行完整课程质量门禁和 knowledge-boundary 校验。
- 保存词义、关系链、题目 traceability、knowledge source 和生成 provenance。
- 使用固定回归样例持续评估知识准确性、自然度和课程质量。
- critique-and-repair 是否加入后续流程保持为 Open Question。

### R2b: Lexical Data Risk

风险：Lexical source 可能存在覆盖不足、词义粒度不一致、数据版本变化、许可限制或服务不可用问题。

缓解：

- 通过 `LexicalSource` abstraction 隔离具体 provider。
- 保存数据来源和版本，并对稳定 semantic profile 使用缓存。
- 使用固定 lexical fixtures 覆盖 Mock 与多义词、词性、搭配回归案例，不把 fixture 当作生产词库。
- AI 生成的 profile 必须通过 exact-word coverage、schema、sense 和 relation evidence 校验；无可靠 profile 时停止主题规划。

### R2c: Knowledge Accuracy And Coverage Risk

风险：Evergreen knowledge library 可能覆盖有限、来源过期、事实映射错误，或无法匹配用户当前词包。

缓解：

- MVP 只收录稳定、经过整理的知识主题和事实。
- 每个 fact 保存 source provenance 和版本。
- 每节课只使用一个核心知识点和最多 1-2 个辅助事实。
- 无 library topic 匹配时只允许受限的 language-focused 主题，不允许 AI 生成无来源外部事实。
- 对知识事实边界、来源映射和无匹配 fallback 建立固定测试。

### R3: Security Risk

风险：账号、session、HttpOnly cookie、Maimemo secret、平台 AI key 涉及安全敏感面。

缓解：

- 用户数据按 user scope 查询。
- Maimemo secret 加密入库。
- 平台 AI key 只在后端环境变量或 secret storage。
- 普通日志不得输出 secret。
- 安全测试进入 MVP 验收。

### R4: Scope Risk

风险：同时支持 CEFR A1-C2、lexical enrichment、知识主题匹配、两阶段生成和知识来源，会扩大实现与测试范围。

缓解：

- 每个等级先定义最小生成约束、校验规则和测试样例。
- 第一版只使用有限 evergreen factual knowledge library，并把无匹配 fallback 限制为语言知识；每节课只承载一个核心知识点。
- 第一版只支持 explanatory scenario、micro case 和 comparison 三种 content mode。
- 不在 MVP 中加入兴趣画像、实时检索、自由聊天、多角色对话、分支任务、多模型 UI、复杂报表和听说功能。

## Open Questions

- 第一阶段是否增加可选 critique-and-repair provider call 尚未确定。
- Lexical source 的具体 provider、许可、版本策略和缓存失效规则尚未确定。
- 第一批 evergreen knowledge library 的具体主题数量、来源选择和维护流程尚未确定。
- 主题关系链使用哪些确定性规则、LLM 判断和通过阈值尚未确定。
- `TopicProposal` 和 `KnowledgeBrief` 是否持久化为独立表，或只作为 generation provenance 保存，尚未确定。
- `WordSemanticProfile`、`KnowledgeTopic`、`TopicProposal`、`KnowledgeBrief` 和 `ContextLesson` 的最终 JSON/schema 需要在实现前定稿。
- Knowledge source 展示所需的 title、publisher、URL、version/date 和 fact mapping 字段尚未确定。
- 题目 traceability 和 generation metadata 的最终 JSON/schema 字段名称尚未确定。
- OpenAI MVP 使用的具体 model 尚未确定。
- Maimemo real adapter 是否能稳定得到 `masteredWordsSample` 仍需验证。
- 用户 AI token 加密入库的具体启用时机和 UI 不在 MVP 中确定。
- CEFR 到语法范围、句法复杂度、中文辅助比例的详细映射需要在实现设计中细化。

## References

- Maimemo OpenAPI: https://open.maimemo.com/#/
- maimemo/memo-api-cli: https://github.com/maimemo/memo-api-cli
- maimemo/memo-skills: https://github.com/maimemo/memo-skills/tree/main
