# Lexis 词汇语境学习 MVP IA Handoff

生成日期：2026-07-02  
来源文档：[English Learning AI Agent PRD.md](English Learning AI Agent PRD.md)  
转化方式：`prd-to-ia` skill  
输出边界：本文件是 UI 设计前的信息架构 handoff，不包含视觉设计、组件库选择、样式、API 设计或数据库实现细节。

## 1. 来源与范围摘要

### 产品目标

Lexis 的核心目标是把用户在 Maimemo 中的当日词汇学习数据，转化为一节可完成、可反馈、可追踪的 CEFR 匹配语境阅读课程。`source-backed: D1, Problem, Goals`

### 主要用户

| 角色 | 摘要 | 标签 | 来源/依据 |
| --- | --- | --- | --- |
| CEFR A1-C2 英语学习者 | 登录 Lexis，同步自己的 Maimemo 词汇数据，生成并完成语境阅读课程，查看历史反馈。 | source-backed | Users And Actors, Goals, User Journey |

### 外部系统

| 系统 | IA 相关性 | 标签 | 来源/依据 |
| --- | --- | --- | --- |
| Maimemo OpenAPI | 提供今日新词、复习或模糊词、已掌握词样本、墨墨词汇记录总数；Lexis 只读，不写回。 | source-backed | FR10-FR15, Data Boundary |
| OpenAI / `LLMProvider` | 生成结构化 `ContextLesson`、逐题反馈、最终总结。 | source-backed | FR22-FR26, AI Behavior Contract |

### 核心范围

| 范围 | 包含能力 | 标签 | 来源/依据 |
| --- | --- | --- | --- |
| Account/Auth | 邮箱密码注册登录、后端 session、HttpOnly cookie、未登录拦截、用户数据隔离。 | source-backed | FR1-FR5 |
| Connection/Secrets | Maimemo secret 配置与加密存储，平台 OpenAI key 仅服务端保存。 | source-backed | FR6-FR9 |
| Maimemo Sync | 同步并保存标准化 snapshot，形成词汇画像。 | source-backed | FR10-FR19 |
| Lesson Generation | 用户手动触发生成；生成前可轻量调整词包；生成结构化课程。 | source-backed | FR20-FR26, FR45, FR47 |
| CEFR Constraints | A1-C2 全等级生成约束、校验规则和测试样例。 | source-backed | FR27-FR33 |
| Lesson Experience | 阅读文章、词汇辅助、目标词解释、语法分析、四类练习。 | source-backed | FR34-FR44 |
| Feedback/Attempt | 每题即时反馈、保存作答、最终总结、更新语境掌握状态。 | source-backed | FR48-FR52 |
| History | 查看历史课程、作答、逐题反馈和最终总结。 | source-backed | FR53-FR55 |
| Validation/Fallback | schema 校验、规则校验、失败状态、重试入口。 | source-backed | FR56-FR60, Fallbacks |

### 明确非目标 / 排除项

| 排除范围 | IA 决策 | 标签 | 来源/依据 |
| --- | --- | --- | --- |
| 自由聊天式 AI Tutor | 不建聊天入口、thread UI 或自由输入 tutor flow。 | excluded | Non-Goals, D5 |
| 写回 Maimemo | 不设计 Maimemo 写入、学习状态回写或远端更新确认。 | excluded | FR15, Data Boundary |
| 长期复习调度 | 不建 Lexis 自有复习计划/排程导航。 | excluded | FR18, Non-Goals |
| Streak/打卡压力机制 | 不建 streak、每日强制完成或连续打卡 UI。 | excluded | FR46, Non-Goals |
| 多模型 UI / BYOK UI | MVP 不设计模型切换入口或用户自带 AI key 配置流程。 | excluded | D15, FR8, Non-Goals |
| 组织/班级/好友/排行榜/管理员后台 | 不建社交、组织或 admin 信息架构。 | excluded | Non-Goals |
| 听力/口语/发音/ASR/音频生成 | 不建音频相关练习与媒体状态。 | excluded | Non-Goals |
| 复杂学习报表 | 不建周报、月报、积分、复杂趋势 dashboard。 | excluded | Non-Goals |
| 高级词库管理 | 不建复杂筛选、词库 CRUD 或长期词库管理台。 | excluded | Non-Goals |

## 2. 就绪度评估

| 缺口类型 | 发现 | 影响 | IA 处理 |
| --- | --- | --- | --- |
| 阻塞 | 无。PRD 已明确 primary user、core job、scope、核心对象、权限边界和 AI flow。 | 可以继续完整 IA 转化。 | 继续建模 |
| 非阻塞 | OpenAI MVP model 尚未确定。 | 不影响 IA 结构，但影响生成状态文案和 observability 字段。 | 标记为 unresolved |
| 非阻塞 | `ContextLesson` 最终 JSON schema 未定稿。 | 不影响屏幕结构，但影响课程内容 contract 的字段精度。 | 标记为 unresolved |
| 非阻塞 | Maimemo real adapter 是否稳定提供 `masteredWordsSample` 未验证。 | 影响同步完成标准、失败/降级状态。 | 标记为 unresolved |
| 非阻塞 | CEFR 到语法范围、句法复杂度、中文辅助比例映射未定稿。 | 影响规则校验详情和课程展示粒度。 | 标记为 unresolved |
| 设计时问题 | 具体 route 命名、导航样式、表单字段排布未定。 | UI 设计阶段解决。 | 仅给出概念 route |

## 3. 标准化功能清单

| 功能 ID | 来源 | 标准化功能 | 优先级 | 标签 |
| --- | --- | --- | --- | --- |
| AUTH-001 | FR1-FR5 | 未登录/学习者 -> 注册或登录 -> session -> 创建登录态 -> 只允许访问自己的学习功能。 | critical | source-backed |
| SEC-001 | FR6-FR9 | 系统 -> 保护 secret/token -> Maimemo secret / AI key / user AI token boundary -> 加密、服务端保存、不返回前端、不进普通日志。 | critical | source-backed |
| SYNC-001 | FR10-FR15 | 学习者 -> 同步 Maimemo -> sync snapshot -> 获取并标准化当日词汇数据 -> 供词汇画像和课程生成使用。 | critical | source-backed |
| VOCAB-001 | FR16-FR19 | 系统 -> 构建词汇画像 -> 最新 sync snapshot -> 区分新词、复习或模糊词、已掌握词样本和墨墨词汇记录总数。 | critical | source-backed |
| GEN-001 | FR20-FR26, FR45, FR47 | 学习者 -> 手动生成课程 -> `LessonGenerationContext` -> 调用 `LLMProvider` -> 生成结构化 `ContextLesson`。 | critical | source-backed |
| CEFR-001 | FR27-FR33 | 系统 -> 约束课程难度 -> CEFR A1-C2 规则 -> 控制长度、额外陌生词和辅助信息。 | critical | source-backed |
| CONTENT-001 | FR34-FR44 | 学习者 -> 学习课程内容 -> `ContextLesson` -> 阅读、词汇、语法、四类练习 -> 完成语境学习。 | critical | source-backed |
| FEEDBACK-001 | FR48-FR52 | 学习者 -> 提交练习答案 -> `LessonAttempt` / `ExerciseFeedback` -> 获得即时反馈、最终总结并更新掌握状态。 | critical | source-backed |
| HISTORY-001 | FR53-FR55 | 学习者 -> 查看历史 -> lesson/attempt/feedback -> 复盘课程内容、作答、反馈、总结。 | important | source-backed |
| VALID-001 | FR56-FR60 | 系统 -> 校验 AI 输出 -> schema/rule validation result -> 阻止无效课程进入有效历史并允许重新生成。 | critical | source-backed |
| OBS-001 | Observability, Cost And Latency | 系统 -> 记录运行事件 -> sync/generation/validation/feedback logs -> 支撑后续诊断、成本和质量优化。 | supporting | source-backed |
| FALLBACK-001 | Fallbacks | 学习者/系统 -> 处理失败或缺失支持 -> not connected/sync failed/OpenAI failed/validation failed/incomplete attempt -> 保留历史并提供重试或未完成状态。 | important | source-backed |

## 4. 角色与权限模型

### 角色模型

| 角色 | 目标 | 范围 | 权限 | 标签 | 来源/依据 |
| --- | --- | --- | --- | --- | --- |
| 访客 | 注册或登录。 | 仅 Auth screens | 可访问注册、登录；不可访问同步、课程生成、历史、反馈。 | source-backed | FR1-FR5 |
| 学习者 | 同步个人词汇、生成课程、完成练习、查看历史。 | 仅自己的账号数据 | 可配置自己的 `MaimemoConnection`、同步自己的 snapshot、生成自己的 lesson、提交自己的 attempt、查看自己的 history。 | source-backed | Users And Actors, FR4-FR5 |
| 后端系统 | 执行 session、secret protection、sync normalization、validation、persistence。 | 服务端流程 | 可处理用户请求范围内的数据；不得跨用户共享；不得泄露 secret。 | source-backed | FR2-FR9, Data Boundary |
| Maimemo OpenAPI | 提供授权用户的词汇学习数据。 | 外部只读数据源 | 仅作为只读数据来源；Lexis 不写回。 | source-backed | FR10-FR15 |
| `LLMProvider` / OpenAI | 生成课程与反馈。 | AI 生成与反馈 | 只接收生成课程/反馈所需上下文；不得接收 secret/token。 | source-backed | AI Behavior Contract, Privacy |
| 开发/测试操作者 | 用 mock provider 跑通端到端开发和测试。 | 开发/测试环境 | 可使用 mock Maimemo 和 mock LLM；不形成 production learner navigation。 | source-backed | Goals, User Stories, Testing Strategy |

### 权限矩阵

| 角色 | 对象/区域 | 可查看 | 可操作 | 限制 | 来源/标签 |
| --- | --- | --- | --- | --- | --- |
| 访客 | Auth | 是 | 注册、登录 | 不能访问 app protected routes。 | FR1-FR5 / source-backed |
| 访客 | 课程工作台/历史/反馈 | 否 | 否 | 必须被要求登录。 | AC1 / source-backed |
| 学习者 | 自己的 `MaimemoConnection` | 是 | 配置、更新 secret、触发 sync | secret 明文不返回前端。 | FR6-FR9 / source-backed |
| 学习者 | 自己的 `MaimemoSyncSnapshot` | 是 | 通过 sync 触发创建 | 只读 Maimemo，不写回。 | FR10-FR15 / source-backed |
| 学习者 | 自己的 `VocabularyProfile` | 是 | 用于生成课程、轻量调整词包 | 课程默认只用最新同步当日词。 | FR16-FR19, FR47 / source-backed |
| 学习者 | 自己的 `ContextLesson` | 是 | 生成、失败后重新生成、学习 | invalid lesson 不进入有效历史。 | FR20-FR26, FR56-FR60 / source-backed |
| 学习者 | 自己的 `LessonAttempt` | 是 | 提交答案、完成 attempt | 可保存 draft/incomplete。 | FR48-FR52, Fallbacks / source-backed |
| 学习者 | 自己的 `ExerciseFeedback` | 是 | 通过提交答案触发反馈 | feedback 属于该用户 attempt。 | FR48-FR50 / source-backed |
| 学习者 | 自己的 `ContextMasteryState` | 是 | 课程完成后由系统间接更新 | 不写回 Maimemo。 | FR52, D8 / source-backed |
| 后端系统 | secrets/logs | 有限服务端可见 | 加密、存储、日志脱敏 | 不返回前端、不写普通日志。 | FR6-FR9, Observability / source-backed |
| 开发/测试操作者 | mock data/providers | 开发/测试环境可见 | 运行 mock sync/generation | 除非后续明确，否则不定义为学习者可见的 MVP 设置项。 | Goals, User Stories / inferred |

## 5. 领域对象与内容模型

| 对象 | 描述 | 所属/操作者 | IA 关键字段 | 相关对象 | 生命周期状态 | 标签 |
| --- | --- | --- | --- | --- | --- | --- |
| `User` | Lexis 账号主体。 | 学习者 | email, auth status, CEFR level, exam/learning goal | `Session`, 用户拥有的全部数据 | unregistered、registered、authenticated、logged out | source-backed |
| `Session` | 后端 session 和 HttpOnly cookie 登录态。 | 后端系统 | session status, expiry | `User` | active、expired、revoked | source-backed |
| `MaimemoConnection` | 用户授权/配置 Maimemo 连接的记录。 | 学习者 | connection status, secret saved indicator, last sync status | `User`, `MaimemoSyncSnapshot` | not configured、configured、sync ready、sync failed | source-backed |
| `MaimemoSyncSnapshot` | 一次同步结果快照。 | 后端系统 | `newWords`, `fuzzyWords/reviewWords`, `masteredWordsSample`, `trackedWordCount`, timestamp, status | `MaimemoConnection`, `VocabularyProfile`, `ContextLesson` | syncing、succeeded、failed | source-backed |
| `VocabularyProfile` | 基于最新 snapshot 的课程生成词汇画像。 | 后端系统 | new words, fuzzy/review words, mastered sample, tracked word count | `MaimemoSyncSnapshot`, `LessonGenerationContext` | unavailable、ready、stale/unresolved | source-backed |
| `WordPackageAdjustment` | 生成前用户对词包的轻量调整。 | 学习者 | selected/removed/emphasized words, adjustment notes | `VocabularyProfile`, `LessonGenerationContext` | unedited、edited、invalid/unresolved | source-backed |
| `LessonGenerationContext` | AI 课程生成输入 contract。 | 后端系统 | `examGoal`, `cefrLevel`, `newWords`, `fuzzyWords`, `masteredWordsSample`, `trackedWordCount`, `userWordAdjustments`, `generationConstraints` | `VocabularyProfile`, `ContextLesson` | ready、missing inputs、submitted | source-backed |
| `ContextLesson` | AI 生成课程内容；不存用户作答和反馈。 | `LLMProvider` / 后端系统 | reading, unfamiliar word aid, target word explanation, grammar analysis, four exercise types, validation result | `LessonAttempt`, `MaimemoSyncSnapshot` | generating、validation pending、valid、invalid、generation failed | source-backed |
| `Exercise` | `ContextLesson` 内的题目内容。 | `LLMProvider` / 后端系统 | type, prompt, target words, expected answer/rubric | `ContextLesson`, `ExerciseFeedback` | unanswered、answered、feedback available | inferred |
| `LessonAttempt` | 用户对某节课的一次学习过程。 | 学习者 | answers, progress, final summary, completion state | `ContextLesson`, `ExerciseFeedback` | not started、in progress、incomplete/draft、completed | source-backed |
| `ExerciseFeedback` | 单题作答和即时反馈记录。 | 后端系统 / `LLMProvider` | submitted answer, correctness/feedback, explanation, status | `LessonAttempt`, `Exercise` | pending、available、failed | source-backed |
| `ContextMasteryState` | Lexis 内部语境掌握状态。 | 后端系统 | target word/context mastery indicators, updated at | `User`, `LessonAttempt` | not initialized、updated | source-backed |
| `ValidationResult` | AI 输出 schema/rule 校验结果。 | 后端系统 | schema status, rule failures, reasons, valid flag | `ContextLesson` | pending、passed、failed | source-backed |
| `LLMCallLog` | LLM 调用与成本/延迟观测记录。 | 后端系统 | model name, token usage, latency, error type, status | `ContextLesson`, `ExerciseFeedback` | recorded success、recorded failure | source-backed |
| `SyncLog` | Maimemo sync 观测记录。 | 后端系统 | status, error type, duration | `MaimemoSyncSnapshot` | recorded success、recorded failure | source-backed |

## 6. 对象生命周期与状态模型

### `MaimemoConnection`

| 状态 | 进入条件 | 可用动作 | 下一状态 | 可见角色 | 标签 |
| --- | --- | --- | --- | --- | --- |
| not configured | 学习者还没有保存 Maimemo secret。 | 配置连接；开发/演示场景可走 mock/dev path。 | configured | 学习者 | source-backed |
| configured | secret 已加密保存。 | sync Maimemo、更新连接。 | syncing、sync failed、sync ready | 学习者 | source-backed |
| sync ready | 最近一次 sync 成功。 | 查看 snapshot、生成 vocabulary profile、再次 sync。 | syncing | 学习者 | source-backed |
| sync failed | sync 尝试失败。 | 重试 sync、查看错误状态、保留既有 history。 | syncing、sync ready | 学习者 | source-backed |

### `ContextLesson`

| 状态 | 进入条件 | 可用动作 | 下一状态 | 可见角色 | 标签 |
| --- | --- | --- | --- | --- | --- |
| not generated | 最新词包还没有请求生成课程。 | 调整 word package、generate lesson。 | generating | 学习者 | source-backed |
| generating | 用户手动触发课程生成。 | 等待；是否可取消仍 unresolved。 | validation pending、generation failed | 学习者 | source-backed |
| validation pending | `LLMProvider` 已返回输出。 | 系统执行 schema/rule validation。 | valid、invalid | 学习者/系统 | source-backed |
| valid | schema 与规则校验通过。 | 开始学习、查看课程内容。 | attempted、historical | 学习者 | source-backed |
| invalid | schema 或规则校验失败。 | 查看失败原因、重新生成。 | generating | 学习者 | source-backed |
| generation failed | LLM/provider 调用失败。 | 重试生成。 | generating | 学习者 | source-backed |
| historical | lesson 已保存，并可在 history 中查看。 | 重新打开、复盘 attempt/feedback。 | historical | 学习者 | source-backed |

### `LessonAttempt`

| 状态 | 进入条件 | 可用动作 | 下一状态 | 可见角色 | 标签 |
| --- | --- | --- | --- | --- | --- |
| not started | 打开 valid lesson，但尚未提交答案。 | 开始练习。 | in progress | 学习者 | source-backed |
| in progress | 至少提交一道题，或正在练习中。 | 提交下一题；离开并保存 incomplete。 | incomplete/draft、completed | 学习者 | source-backed |
| incomplete/draft | 用户未完成课程即离开。 | 恢复 attempt、查看已答题 feedback。 | in progress、completed | 学习者 | source-backed |
| completed | 所有必需练习已提交，final summary 已保存。 | 查看 summary、更新 mastery state、进入 history。 | historical | 学习者 | source-backed |

### `ExerciseFeedback`

| 状态 | 进入条件 | 可用动作 | 下一状态 | 可见角色 | 标签 |
| --- | --- | --- | --- | --- | --- |
| pending | 用户提交一道题答案。 | 等待 feedback。 | available、failed | 学习者 | source-backed |
| available | feedback 已生成并保存。 | 继续课程、查看解释。 | available | 学习者 | source-backed |
| failed | feedback 生成或保存失败。 | 重试 feedback，或保留答案 pending。 | pending、available | 学习者 | source-backed |

## 7. 功能放置矩阵

| 来源 ID | 功能 | 导航区域 | 屏幕/route | 对象/动作 | 所属流程 | 状态 | 理由 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FR1-FR5 | 注册/登录/session/用户数据隔离/受保护访问。 | Auth | `/register`, `/login`, protected route gate | `User`, `Session` / register, login, guard | Auth + Permission Gate | placed | 所有私有学习流程之前都必须完成登录态确认。 |
| FR6-FR9 | secret 保护，且不返回前端、不进入普通日志。 | Settings/Connection + 系统边界 | `/app/settings/connection`, server-side only states | `MaimemoConnection`, secret boundary / configure | 配置 Maimemo | placed | 用户需要 connection UI；secret 只展示 saved/error state，不展示明文。 |
| FR10-FR15 | Maimemo provider abstraction、mock/real 边界、标准化输出、只读。 | Course Workspace + Connection | `/app/workspace`, `/app/settings/connection` | `MaimemoSyncSnapshot` / sync | 同步 Maimemo | placed | sync 是词汇画像和课程生成的前置条件。 |
| FR16-FR19 | 基于最新 snapshot 的 vocabulary profile；不做 Lexis 自有复习调度。 | Course Workspace | `/app/workspace` | `VocabularyProfile` / view, use latest | 准备课程 | placed | profile 是课程工作台的核心输入。 |
| FR20-FR26 | `LessonGenerationContext`、`LLMProvider`、结构化 `ContextLesson`。 | Course Workspace | `/app/workspace` -> `/app/lessons/:lessonId` | `ContextLesson` / generate | 生成课程 | placed | 生成从 workspace 发起，并落到 lesson player。 |
| FR27-FR33 | CEFR A1-C2 约束、文章长度、额外陌生词上限、中文辅助。 | Course Workspace + Validation | `/app/workspace`, `/app/lessons/:lessonId` | `GenerationConstraints`, `ValidationResult` / validate | 生成课程 | placed | 这些约束影响输入就绪、输出校验和失败状态。 |
| FR34-FR44 | 课程内容：reading、word aid、target words、grammar、four exercise types、词汇优先级。 | Lesson Player | `/app/lessons/:lessonId` | `ContextLesson`, `Exercise` / view, answer | 完成课程 | placed | 这是核心学习界面。 |
| FR45-FR47 | 手动生成、不强制每日完成、生成前轻量调整词包。 | Course Workspace | `/app/workspace` | `WordPackageAdjustment` / edit, submit generation | 准备课程 | placed | 避免 auto-generation 和每日压力 UI。 |
| FR48-FR52 | 逐题 feedback、attempt/feedback 持久化、final summary、mastery update。 | Lesson Player | `/app/lessons/:lessonId` | `LessonAttempt`, `ExerciseFeedback`, `ContextMasteryState` / submit, complete | 完成课程 | placed | 这是主要学习反馈闭环。 |
| FR53-FR55 | 历史课程、作答、feedback、final summary。 | History | `/app/history`, `/app/history/:lessonId` | `ContextLesson`, `LessonAttempt`, `ExerciseFeedback` / view | 复盘历史 | placed | PRD 明确要求复盘历史课程。 |
| FR56-FR60 | schema/rule validation、invalid lesson state、retry。 | Course Workspace + Generation Status | `/app/workspace`, `/app/lessons/:lessonId` state | `ValidationResult` / fail, retry | 生成课程 | placed | invalid output 不能进入有效 history。 |
| Fallbacks | not connected、sync failed、OpenAI failed、validation failed、incomplete attempt。 | Workspace, Lesson Player, History | 多个 state contracts | Connection, Lesson, Attempt / retry, resume | 失败恢复 | placed | PRD 要求覆盖这些状态。 |
| Observability | sync/LLM/validation/feedback 运行记录。 | 无学习者导航 | 仅服务端日志 | `SyncLog`, `LLMCallLog` / record | 所有系统流程 | placed as system-only | PRD 要求记录，但不要求 admin UI。 |
| Non-Goals | chat tutor、writeback、streak、多模型 UI、社交/admin/audio/reporting。 | 无 | 无 | N/A | N/A | excluded | 明确不属于 MVP。 |

## 8. 导航与 Route 模型

### 导航区域

| 区域 | 目的 | 主要角色 | 主要对象 | 入口 | 包含内容 | 来源/依据 |
| --- | --- | --- | --- | --- | --- | --- |
| Auth | 让访客成为 authenticated learner。 | 访客 | `User`, `Session` | app entry、protected-route redirect | Register, Login | FR1-FR5 |
| Course Workspace | 同步词汇、查看词汇画像、调整词包、手动生成课程。 | 学习者 | `MaimemoSyncSnapshot`, `VocabularyProfile`, `WordPackageAdjustment`, `ContextLesson` | 登录后、主导航、history regenerate path | sync status、vocabulary profile、word adjustment、generation status | FR10-FR26, FR45-FR47 |
| Lesson Player | 完成一节结构化语境阅读课程并获得反馈。 | 学习者 | `ContextLesson`, `LessonAttempt`, `ExerciseFeedback` | generated lesson、history resume | reading content、word aid、grammar analysis、exercises、final summary | FR34-FR52 |
| History | 查看历史课程、作答、feedback 和 summary。 | 学习者 | `ContextLesson`, `LessonAttempt`, `ExerciseFeedback` | 主导航、completion exit | history list、history detail | FR53-FR55 |
| Connection Settings | 配置 Maimemo connection，显示 secret 保存状态和同步错误。 | 学习者 | `MaimemoConnection` | workspace empty/not connected state、settings nav | Maimemo connection form/status | FR6-FR15 |

### Route 到屏幕映射

| Route | 屏幕 | 访问角色 | 主要对象 | 入口来源 | 退出路径 | 标签 |
| --- | --- | --- | --- | --- | --- | --- |
| `/register` | 注册页 | 访客 | `User` | 直接访问、登录页链接 | `/app/workspace`, `/login` | source-backed |
| `/login` | 登录页 | 访客 | `Session` | 直接访问、protected-route redirect | `/app/workspace`, `/register` | source-backed |
| `/app/workspace` | 课程工作台 | 学习者 | `VocabularyProfile`, `ContextLesson` | 登录后、主导航 | `/app/settings/connection`, `/app/lessons/:lessonId`, `/app/history` | source-backed |
| `/app/settings/connection` | Maimemo 连接设置页 | 学习者 | `MaimemoConnection` | workspace not connected state、settings nav | `/app/workspace` | inferred |
| `/app/lessons/:lessonId` | 课程学习页 | lesson 所有者 | `ContextLesson`, `LessonAttempt` | generation success、history resume | `/app/history/:lessonId`, `/app/workspace` | source-backed |
| `/app/history` | 历史课程列表 | 学习者 | `ContextLesson` collection | 主导航、completion exit | `/app/history/:lessonId`, `/app/workspace` | source-backed |
| `/app/history/:lessonId` | 历史课程详情 | lesson 所有者 | `ContextLesson` + `LessonAttempt` + `ExerciseFeedback` | 历史列表 | `/app/history`, `/app/lessons/:lessonId` when resumable | source-backed |

## 9. 屏幕清单与屏幕契约

### AUTH-01 注册页

| 字段 | 契约 |
| --- | --- |
| 目的 | 创建 Lexis 账号并进入私有学习空间。 |
| 主要角色 | 访客 |
| 主要对象 | `User` |
| 来源功能 | FR1-FR5 |
| 入口 | 直接访问、登录页链接、无账号时的 protected-route redirect。 |
| 退出路径 | 注册成功后进入课程工作台；也可去登录页。 |
| 主要动作 | 使用 email/password 注册。 |
| 次要动作 | 前往登录页。 |
| 内容优先级 | email/password 输入、validation errors、auth status。 |
| 状态 | success、loading、error；permission/empty 不适用。 |
| 权限规则 | 仅访客需要使用；已登录学习者应被重定向到 workspace。 |
| 依赖 | 后端 auth/session。 |
| 未解决 | 密码策略属于实现/安全设计，PRD 未指定。 |
| 标签 | source-backed |

### AUTH-02 登录页

| 字段 | 契约 |
| --- | --- |
| 目的 | 通过 email/password 建立后端 session 和 HttpOnly cookie。 |
| 主要角色 | 访客 |
| 主要对象 | `Session` |
| 来源功能 | FR1-FR5, AC1 |
| 入口 | 直接访问、注册页链接、protected-route redirect。 |
| 退出路径 | 登录成功后进入课程工作台；也可去注册页。 |
| 主要动作 | 登录。 |
| 次要动作 | 前往注册页。 |
| 内容优先级 | 凭证输入、auth error、redirect context。 |
| 状态 | success、loading、error、permission redirect。 |
| 权限规则 | 已认证学习者不应停留在此页。 |
| 依赖 | 后端 session 和 HttpOnly cookie。 |
| 未解决 | PRD 未指定 password reset；除非后续新增，否则不进入 MVP IA。 |
| 标签 | source-backed |

### APP-01 课程工作台

| 字段 | 契约 |
| --- | --- |
| 目的 | 作为课程生成工作台：确认连接、同步词汇、查看词汇画像、调整词包并手动生成课程。 |
| 主要角色 | 学习者 |
| 主要对象 | `VocabularyProfile`, `MaimemoSyncSnapshot`, `ContextLesson` |
| 来源功能 | FR10-FR33, FR45-FR47, FR56-FR60 |
| 入口 | 登录后、主导航、历史中的 retry/regenerate path。 |
| 退出路径 | Maimemo 连接设置页；生成有效课程后进入课程学习页；历史页。 |
| 主要动作 | sync Maimemo、调整词包、generate lesson、失败后 retry generation。 |
| 次要动作 | 查看最新 snapshot status、查看 validation failure reason、前往 connection settings。 |
| 内容优先级 | connection status、latest sync summary、新词/模糊词/已掌握词组、CEFR level、exam/learning goal、generation readiness、validation result。 |
| 状态 | empty/not connected、loading/syncing、ready、generating、validation failed、generation failed、permission denied。 |
| 权限规则 | 学习者只能访问自己的 snapshot/profile/lesson generation。 |
| 依赖 | authenticated session、`MaimemoConnection`、latest sync snapshot、generation constraints。 |
| 未解决 | CEFR/exam goal 的具体采集位置尚未确定：workspace inline vs account/profile settings。IA 假设 workspace 可以暴露缺失的 generation inputs。 |
| 标签 | source-backed + inferred placement |

### APP-02 Maimemo 连接设置页

| 字段 | 契约 |
| --- | --- |
| 目的 | 配置并维护 Maimemo connection，展示 secret saved status 和 sync readiness。 |
| 主要角色 | 学习者 |
| 主要对象 | `MaimemoConnection` |
| 来源功能 | FR6-FR15, R1, R3 |
| 入口 | workspace not connected state、settings nav。 |
| 退出路径 | 课程工作台。 |
| 主要动作 | 保存/更新 Maimemo secret；配置完成后触发 sync。 |
| 次要动作 | 查看 last sync error/status。 |
| 内容优先级 | connection state、saved indicator、sync availability、不会暴露 secret 的安全提示。 |
| 状态 | not configured、saving、configured、sync failed、permission denied。 |
| 权限规则 | 只有 owner learner 可以查看/更新自己的 connection；保存后不再展示 plaintext secret。 |
| 依赖 | encryption boundary、backend storage、Maimemo provider abstraction。 |
| 未解决 | revoke/delete/rotate secret 是否需要 MVP UI 尚不明确；先作为 future-support boundary。 |
| 标签 | source-backed |

### APP-03 课程学习页

| 字段 | 契约 |
| --- | --- |
| 目的 | 展示有效 `ContextLesson`，让学习者完成阅读、四类练习并获得逐题反馈。 |
| 主要角色 | 学习者 |
| 主要对象 | `ContextLesson`, `LessonAttempt` |
| 来源功能 | FR34-FR52 |
| 入口 | generation success、resumable history detail。 |
| 退出路径 | 完成总结页、历史详情页、课程工作台。 |
| 主要动作 | 阅读课程、提交每道 exercise answer、继续下一题、完成课程。 |
| 次要动作 | 查看 vocabulary aid、target word explanation、grammar/long sentence analysis；离开并稍后 resume。 |
| 内容优先级 | reading article、target/fuzzy word treatment、带中文辅助的 unfamiliar word aid、grammar analysis、exercise prompts、feedback state。 |
| 状态 | lesson ready、feedback pending、feedback available、feedback failed、incomplete/draft、completed、permission denied。 |
| 权限规则 | 学习者只能访问自己的 valid lesson 和自己的 attempt。 |
| 依赖 | valid `ContextLesson`、exercise set、feedback provider、attempt/feedback persistence。 |
| 未解决 | PRD 未指定具体 scoring/rubric 展示方式。 |
| 标签 | source-backed |

### APP-04 完成总结页

| 字段 | 契约 |
| --- | --- |
| 目的 | 课程完成后展示最终总结，并确认 Lexis 语境掌握状态已更新。 |
| 主要角色 | 学习者 |
| 主要对象 | `LessonAttempt`, `ContextMasteryState` |
| 来源功能 | FR51-FR52 |
| 入口 | Lesson Player completion。 |
| 退出路径 | 历史详情页、课程工作台。 |
| 主要动作 | 查看 final summary、进入 history、生成另一节课程。 |
| 次要动作 | 回看 exercise feedback。 |
| 内容优先级 | final summary、可用时展示 strengths/weaknesses、mastery update status、saved history link。 |
| 状态 | saving summary、summary ready、summary failed/unresolved、permission denied。 |
| 权限规则 | 仅 owner 可见。 |
| 依赖 | 所有必需练习已提交，final summary 已保存。 |
| 未解决 | final summary 存在 `LessonAttempt` 还是关联 feedback 记录中，仍是实现选择。 |
| 标签 | source-backed |

### APP-05 历史课程列表

| 字段 | 契约 |
| --- | --- |
| 目的 | 让学习者查看自己的历史课程集合。 |
| 主要角色 | 学习者 |
| 主要对象 | `ContextLesson` collection |
| 来源功能 | FR53-FR55 |
| 入口 | 主导航、完成总结页。 |
| 退出路径 | 历史详情页、课程工作台。 |
| 主要动作 | 打开某节历史课程。 |
| 次要动作 | filter/sort 不进入 MVP，除非后续明确要求。 |
| 内容优先级 | lesson date、CEFR level、source snapshot summary、completion/validity status、final summary presence。 |
| 状态 | history empty、loading、list ready、error、permission denied。 |
| 权限规则 | 仅 owner 可见；invalid generated lesson 不应作为 valid course history 展示。 |
| 依赖 | 已保存的 `ContextLesson` 和 attempts。 |
| 未解决 | 列表具体元数据属于 design-time。 |
| 标签 | source-backed |

### APP-06 历史课程详情

| 字段 | 契约 |
| --- | --- |
| 目的 | 复盘单节历史课程，包括课程内容、用户作答、逐题反馈和最终总结。 |
| 主要角色 | 学习者 |
| 主要对象 | `ContextLesson`, `LessonAttempt`, `ExerciseFeedback` |
| 来源功能 | FR53-FR55, AC13 |
| 入口 | 历史列表、完成总结页。 |
| 退出路径 | 历史列表、课程工作台；attempt 可恢复时进入课程学习页。 |
| 主要动作 | 复盘 lesson 和 feedback。 |
| 次要动作 | 适用时 resume incomplete attempt。 |
| 内容优先级 | generated lesson content、submitted answers、feedback、final summary、source sync snapshot reference。 |
| 状态 | detail ready、incomplete attempt、missing/deleted object unresolved、loading、error、permission denied。 |
| 权限规则 | 仅 owner 可见；用户 A 不能访问用户 B 的 history。 |
| 依赖 | 已持久化的 lesson/attempt/feedback。 |
| 未解决 | PRD 未指定是否可基于同一 snapshot 重新生成历史课程；MVP IA 暂不包含。 |
| 标签 | source-backed |

## 10. 关键流程规格

### Flow 1：Auth + 受保护访问

| 字段 | 规格 |
| --- | --- |
| 参与者 | 访客、学习者、后端系统 |
| 目标 | 只让 authenticated learner 访问自己的 workspace/history/lesson data。 |
| 前置条件 | 用户可能未登录，或 session 已过期。 |
| 触发 | 用户打开 app 或 protected route。 |
| 主路径 | 1. 用户打开 protected route。2. 后端/session layer 检查 session。3. 如果没有 valid session，重定向到 Login。4. 用户登录或注册。5. 后端设置 HttpOnly cookie。6. 用户进入 Course Workspace。 |
| 分支 | 凭证无效 -> 展示 auth error。已有 valid session -> 直接进入 Workspace。 |
| 失败/空/权限状态 | session 过期时重定向到 Login；用户数据访问必须 scoped to current user。 |
| 完成状态 | authenticated learner 看到自己的 workspace。 |
| 来源/依据 | FR1-FR5, AC1-AC2 |

### Flow 2：配置 Maimemo + 同步词汇

| 字段 | 规格 |
| --- | --- |
| 参与者 | 学习者、后端系统、Maimemo OpenAPI |
| 目标 | 保存 Maimemo connection，并生成最新 sync snapshot / vocabulary profile。 |
| 前置条件 | 学习者已登录。 |
| 触发 | 学习者进入未连接状态的 Workspace，或主动选择 sync。 |
| 主路径 | 1. 学习者打开 Connection Settings。2. 学习者提交 Maimemo secret。3. 后端加密并保存 secret。4. 学习者触发 sync。5. `MaimemoSyncProvider` 读取 Maimemo data。6. 后端标准化为 `newWords`, `fuzzyWords`, `masteredWordsSample`, `trackedWordCount`。7. 系统保存 snapshot 并构建 vocabulary profile。8. Workspace 展示最新 profile。 |
| 分支 | dev/test 中的 mock provider 可以生成等价标准化数据。real adapter 缺少 `masteredWordsSample` -> adapter incomplete/unresolved。 |
| 失败/空/权限状态 | 未连接 -> connection empty state。sync failed -> 保留历史并展示 retry。未授权访问 -> permission state。secret 不得暴露。 |
| 完成状态 | `VocabularyProfile` 可以用于生成课程。 |
| 来源/依据 | FR6-FR19, AC3-AC4, R1 |

### Flow 3：生成并校验 `ContextLesson`

| 字段 | 规格 |
| --- | --- |
| 参与者 | 学习者、后端系统、`LLMProvider`/OpenAI |
| 目标 | 手动生成一节通过 schema/rule validation 的 `ContextLesson`。 |
| 前置条件 | 学习者已登录；`VocabularyProfile` ready；CEFR level 和 exam/learning goal 可用；word package ready。 |
| 触发 | 学习者点击 Generate Lesson。 |
| 主路径 | 1. Workspace 展示最新 word groups。2. 学习者轻量调整 word package。3. 学习者手动触发 generation。4. 后端构建 `LessonGenerationContext`。5. `LLMProvider` 返回 structured output。6. 后端执行 schema validation。7. 后端执行 rule validation：length、CEFR range、target coverage、unfamiliar word count、four exercise types、grammar analysis、final summary fields。8. valid `ContextLesson` 被保存并在 Lesson Player 中打开。 |
| 分支 | validation fails -> 展示 failure reason 并允许 regenerate。OpenAI call fails -> generation failed state 并允许 retry。`MockLLMProvider` 可跑通 dev/test path。 |
| 失败/空/权限状态 | 缺少 sync/profile -> Workspace readiness prompt。invalid lesson -> 不标记为 valid，也不进入有效 history。 |
| 完成状态 | valid lesson 打开并可学习。 |
| 来源/依据 | FR20-FR33, FR45-FR47, FR56-FR60, AC5-AC10 |

### Flow 4：完成课程并获得即时反馈

| 字段 | 规格 |
| --- | --- |
| 参与者 | 学习者、后端系统、`LLMProvider`/OpenAI |
| 目标 | 完成四类练习，保存作答、逐题反馈、最终总结，并更新语境掌握状态。 |
| 前置条件 | valid `ContextLesson` 已存在；学习者拥有该 lesson。 |
| 触发 | 学习者打开 Lesson Player 并提交一道 exercise answer。 |
| 主路径 | 1. 学习者阅读 article 和 supporting content。2. 学习者回答一道 exercise。3. 后端把 answer 保存到 `LessonAttempt`。4. 系统生成/保存 `ExerciseFeedback`。5. UI 展示 immediate feedback。6. 学习者完成所有 required exercise types。7. 系统生成/保存 final summary。8. 系统更新 `ContextMasteryState`。9. 展示 Completion Summary。 |
| 分支 | 学习者未完成即离开 -> 保存 incomplete/draft state。feedback generation fails -> 展示 retry/pending feedback state。 |
| 失败/空/权限状态 | 未授权 lesson access 被阻断。attempt save failure 应展示错误，并尽可能不丢失已保存答案。 |
| 完成状态 | completed attempt 和 final summary 可在 history 中查看。 |
| 来源/依据 | FR34-FR52, AC11-AC12 |

### Flow 5：复盘历史课程

| 字段 | 规格 |
| --- | --- |
| 参与者 | 学习者、后端系统 |
| 目标 | 复盘历史课程、作答、逐题反馈和最终总结。 |
| 前置条件 | 学习者已登录；可能已有至少一条 saved lesson/attempt。 |
| 触发 | 学习者打开 History。 |
| 主路径 | 1. History List 加载当前用户拥有的 lessons。2. 学习者选择一节 lesson。3. History Detail 加载 generated content、attempt answers、feedback 和 final summary。4. 学习者复盘。 |
| 分支 | 无 history -> empty state。incomplete attempt -> 适用时提供 resume path。 |
| 失败/空/权限状态 | 用户 A 不能读取用户 B 的 records。invalid generated lessons 不出现在 valid lesson history。 |
| 完成状态 | 学习者完成一次历史学习记录复盘。 |
| 来源/依据 | FR53-FR55, AC13 |

## 11. 状态覆盖矩阵

| 屏幕/流程 | 成功态 | 空态 | 加载态 | 错误态 | 权限态 | Fallback |
| --- | --- | --- | --- | --- | --- | --- |
| 注册/登录 | session 创建成功并进入 workspace。 | N/A | auth submitting。 | invalid credentials / registration error。 | 已认证用户被重定向离开。 | protected route 重定向到 login。 |
| 课程工作台 | `VocabularyProfile` ready，可生成课程。 | 无 Maimemo connection 或无 sync snapshot。 | syncing、generating、validating。 | sync/generation/validation failure。 | 未登录 -> login；跨用户访问被阻断。 | dev/demo 可走 mock data path；可 retry generation/sync。 |
| Maimemo 连接设置 | secret saved，connection configured。 | 无 connection configured。 | saving secret、syncing。 | save/sync failed。 | owner-only。 | 保留既有 history；允许 retry sync。 |
| 课程学习页 | valid lesson active；每题提交后展示 feedback。 | valid lesson 场景下不适用；无 valid lesson 时回到 workspace。 | feedback pending。 | feedback failed / save failed。 | owner-only lesson access。 | 保存 incomplete attempt；支持时 retry feedback。 |
| 完成总结页 | final summary saved；mastery state updated。 | N/A | saving summary/update。 | summary 或 mastery update failed。 | owner-only。 | 如果 summary 保存失败，history 是否展示 completed content + unresolved summary 需要产品确认。 |
| 历史课程列表 | 展示 historical lessons。 | 无 saved history。 | loading history。 | query/load failure。 | owner-only。 | invalid lessons 不进入 valid list。 |
| 历史课程详情 | 展示 lesson、answers、feedback、summary。 | 已生成但未开始的 lesson 可能缺少 attempt。 | loading detail。 | record missing/load failure。 | owner-only。 | incomplete attempt 可 resume。 |

## 12. 假设、开放问题与风险

### 假设

| ID | 假设 | 依据 | 置信度 | 如果错误的影响 | 待确认问题 | 标签 |
| --- | --- | --- | --- | --- | --- | --- |
| A-IA-001 | CEFR level 和 exam/learning goal 可以在 Workspace 内采集/编辑，或由一个最小 account/profile 区域提供。 | `LessonGenerationContext` 需要 `examGoal` 和 `cefrLevel`；AI Inputs 也包含二者。 | 高 | route/screen placement 可能移动到 profile settings，但核心 IA 不变。 | CEFR/goal 应放在 onboarding、workspace 还是 settings？ | inferred |
| A-IA-002 | “复习或模糊词”在 real adapter 字段验证前，可以先作为一个学习者可见分组呈现。 | FR13 允许 `reviewWords` 或 `fuzzyWords`；PRD 多次使用“复习或模糊词”。 | 高 | UI label 以后可能拆成 review words 与 fuzzy words 两组。 | MVP 是否需要视觉上区分 review words 和 fuzzy words？ | inferred |
| A-IA-003 | History detail 可以复用 lesson content structure，以只读/复盘模式展示。 | History 必须展示 generated content、answers、feedback、final summary。 | 中 | 后续可能需要单独的 history detail screen contract。 | 历史复盘是否要保持原 lesson-player 顺序？ | inferred |
| A-IA-004 | Mock provider support 不作为 production IA 中的主要学习者导航区域。 | mock providers 用于真实集成前的 dev/test；PRD 没有指定用户可见 mock mode。 | 中 | 如果需要 demo mode，Workspace 需要明确的 “use mock data” action。 | MVP demo 用户是否需要看到 “use mock data” 入口？ | inferred |

### 开放问题

| ID | 问题 | 影响 | 当前 IA 处理 | 标签 |
| --- | --- | --- | --- | --- |
| OQ-001 | OpenAI MVP 使用的具体 model 是什么？ | observability labels、cost/latency expectations。 | model name 作为 logged metadata，不作为用户导航。 | unresolved |
| OQ-002 | `ContextLesson` 最终 JSON schema 是什么？ | Lesson Player content contract 和 validation failure details。 | 在 schema 定稿前使用 PRD 级内容分类。 | unresolved |
| OQ-003 | Maimemo real adapter 能否稳定得到 `masteredWordsSample`？ | sync completion 和 fallback state。 | 如果缺失，则 real adapter 标记为 incomplete。 | unresolved |
| OQ-004 | 用户 AI token 加密入库何时启用？ | 未来 BYOK route/settings。 | MVP 排除 BYOK UI；只保留 data boundary。 | unresolved |
| OQ-005 | CEFR 到语法范围、句法复杂度、中文辅助比例如何映射？ | generation constraints 和 rule validation details。 | 作为实现/内容设计细化项，不作为 IA blocker。 | unresolved |
| OQ-006 | Incomplete attempt 的恢复规则是什么？ | Lesson Player 与 History Detail 的 resume behavior。 | 先建模 `incomplete/draft` 状态和 resume entry。 | unresolved |
| OQ-007 | secret revoke/delete/rotation 是否进入 MVP UI？ | Connection Settings actions。 | 先只显式建模 save/update；revoke/delete 作为 unresolved future-support action。 | unresolved |

### 风险

| 风险 | IA 影响 | IA 缓解 | 标签 |
| --- | --- | --- | --- |
| real Maimemo adapter 不确定 | sync readiness 与数据完整性可能失败。 | 显式建模 sync failed/incomplete states；把 `masteredWordsSample` 作为完成标准。 | source-backed |
| AI output quality | 如果 invalid lessons 被当作正常内容展示，会误导学习者。 | validation states 阻止 invalid lessons 进入 valid history，并提供 retry path。 | source-backed |
| auth/secrets 安全敏感 | UI 可能意外暴露私有数据或跨用户对象。 | 所有私有屏幕 owner-only；secret 只展示 saved indicator，不展示 plaintext；权限态覆盖所有私有区域。 | source-backed |
| CEFR A1-C2 范围较宽 | 相比窄 MVP，需要更多 validation/test variants。 | CEFR constraints 作为 generation readiness 和 validation artifact 的一等对象。 | source-backed |

## 13. Traceability Matrix

| 来源 ID | PRD 事实/要求 | IA Artifact | 决策 | 标签 | 开放项 |
| --- | --- | --- | --- | --- | --- |
| D1 | sync Maimemo -> generate context reading lesson -> answer/feedback/history/mastery loop。 | Navigation、critical flows、object model | Course Workspace -> Lesson Player -> History 是核心闭环。 | source-backed | 无 |
| D2-D3 | Maimemo sync 架构和 real adapter 必需输出。 | sync flow、`MaimemoSyncSnapshot`、`VocabularyProfile` | 标准化 word groups 是生成课程前置条件。 | source-backed | real adapter verification |
| D4, FR45-FR46 | 手动生成课程；不强制每日完成。 | Workspace contract | 不建 auto-generated daily pressure 或 streak surface。 | source-backed | 无 |
| D5 | 固定结构阅读课；不做自由聊天 tutor。 | Exclusions、Lesson Player | 不建 chat IA 或 conversation thread。 | excluded | 无 |
| D6, FR38-FR41 | 必须包含四类练习。 | Lesson Player、validation | 四类练习是 content priority 和 validation requirement。 | source-backed | exact schema |
| D7, FR56-FR60 | AI 输出结构化并校验。 | `ValidationResult` lifecycle、generation flow | invalid lesson 被阻断，并可 retry。 | source-backed | exact schema/rules |
| D8, FR15, FR18 | 不写回 Maimemo，不做 Lexis 复习调度。 | Exclusions、permission model | Maimemo read-only；mastery state 是 Lexis-local。 | source-backed | 无 |
| D9, FR1-FR5 | 账号系统和数据隔离。 | Auth screens、permission matrix | 所有 app data 都 owner-scoped 且 protected。 | source-backed | password policy not specified |
| D13, FR6-FR9 | 服务端 AI key 与加密用户 secret。 | Connection Settings、security states | UI 只展示 saved/error status，不展示 plaintext secret。 | source-backed | secret revoke/delete timing |
| D14-D15 | OpenAI-backed provider + abstraction；MVP 不做多模型 UI。 | `LLMProvider` object、exclusions | provider 是系统能力，不是 model picker UI。 | source-backed/excluded | model selection unresolved |
| D16-D17 | `ContextLesson` 存生成课程；`LessonAttempt`/`ExerciseFeedback` 存作答/feedback/summary。 | Domain object model | generated content 与 user attempt data 分离。 | source-backed | final summary storage location |
| D18, FR27-FR33 | CEFR A1-C2 支持和约束。 | Generation context、validation、Workspace readiness | CEFR 是 required input/constraint 和 validation dimension。 | source-backed | detailed CEFR mapping |
| FR10-FR19 | sync provider、normalized snapshot、vocabulary profile。 | Workspace、sync flow、object lifecycle | latest snapshot 驱动默认课程生成。 | source-backed | real adapter fields |
| FR20-FR26 | `LessonGenerationContext` 和 `LLMProvider`。 | generation flow、`ContextLesson` lifecycle | 用户手动 generation，通过 provider 创建 structured lesson。 | source-backed | exact schema |
| FR34-FR44 | 课程内容要求和词汇优先级。 | Lesson Player contract | reading、word aid、target explanations、grammar、four exercises 都是必需内容。 | source-backed | display structure is design-time |
| FR48-FR52 | 即时 feedback、保存 attempt/feedback/summary、更新 mastery。 | Lesson Player、Completion Summary | 每次答题都会创建 saved feedback；完成后更新 mastery。 | source-backed | feedback retry semantics |
| FR53-FR55 | 历史查看要求。 | History List、History Detail | history 必须包含 generated content、answers、feedback、final summary。 | source-backed | historical regeneration excluded |
| Fallbacks | not connected、sync failed、OpenAI failed、validation failed、incomplete attempt。 | State coverage matrix | 每个 critical flow 覆盖 empty/loading/error/fallback states。 | source-backed | incomplete attempt resume rules |
| Observability | 记录 sync/LLM/validation/generation/feedback status；不记录 secrets。 | system-only logs、no admin UI | 记录 operational data，但 MVP 不暴露 admin surface。 | source-backed | 是否需要未来 ops dashboard |
| Non-Goals | chat、writeback、streak、social/admin/audio/reporting/BYOK/multi-model UI。 | Exclusions | 不为这些范围创建 route 或 screen。 | excluded | future roadmap only |

## Quality Gate 结果

| 检查项 | 结果 |
| --- | --- |
| PRD 主要功能都已 placed 或 excluded | 通过 |
| 每个 proposed screen 都有 goal、object、entry/exit、actions、states、permissions、dependencies | 通过 |
| AI-specific input、output states、validation、fallback、history、observability 已建模 | 通过 |
| inferred items 都带有依据 | 通过 |
| unresolved items 与 confirmed requirements 分离 | 通过 |
| 已避免 visual design、layout、component、implementation architecture 建议 | 通过 |






