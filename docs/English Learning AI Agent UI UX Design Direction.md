# Lexis UI/UX Design Direction

生成日期：2026-07-02
来源文档：

- [English Learning AI Agent PRD.md](English Learning AI Agent PRD.md)
- [English Learning AI Agent IA Handoff.md](English Learning AI Agent IA Handoff.md)
- `grill-me` 设计方向确认会话

## 1. Design Positioning

Lexis 的第一版 UI/UX 方向是：

> 安静、专注、稍微有 AI 感的学习工作台。

Lexis 不是游戏化打卡产品，不是自由聊天式 AI Tutor，也不是传统电子书 App。它的核心体验是：同步 Maimemo 词汇数据，生成一节结构化语境阅读课程，完成逐题练习，获得即时反馈，并在历史中复盘。

整体视觉应偏向现代 AI 工具和轻仪表盘感；课程正文区域保留一点阅读纸面感。产品应呈现 Apple Notes、Linear、Notion Calendar 一类克制、精密、安静的高级感。

## 2. Experience Principles

### 2.1 Calm Workspace

用户打开 Lexis 后，应快速知道：

- Maimemo 是否已连接或已同步。
- 今日词包是否 ready。
- 当前是否可以生成一节课程。

界面不应把用户推向 streak、积分、排行榜或每日压力机制。高级感来自清楚的状态、稳定的层级和准确的留白，而不是装饰性视觉。

### 2.2 Tool First, Reading Second

Lexis 的主框架是工具型学习工作台。阅读正文是核心学习内容，但纸面感只应进入正文阅读区域，不能扩散到整个 App。

主 UI 应保持现代工具感：状态明确、动作直接、信息密度适中。正文区域可以更温和、更像讲义，支持沉浸阅读。

### 2.3 AI As Infrastructure

AI 是幕后生成与反馈引擎，不是人格化角色。

AI 的存在感应体现在：

- 课程生成状态。
- schema/rule validation 状态。
- 即时反馈和最终总结。
- 失败后的 retry 入口。

不使用 AI 头像、聊天气泡、拟人名称或陪伴式文案。不要让用户误以为 Lexis 是自由聊天 Tutor。

## 3. Visual Direction

### 3.1 Palette

主色方向：

- 墨黑：主要文字、关键标题、强操作。
- 雾白：页面背景、阅读区域背景。
- 石墨灰：次级文字、边界、分割线、辅助信息。
- 低饱和青绿色：AI、成功、校验通过、掌握提升等关键正向状态。

辅助状态色：

- 柔和红：错误、校验失败、同步失败。
- 琥珀色：警告、未完成、需要重试。
- 中性灰：loading、pending、disabled。

避免：

- 大面积紫蓝 AI 渐变。
- 高饱和糖果色。
- 霓虹科幻感。
- 单一色相铺满整个界面。

### 3.2 Typography

整体排版应清晰、克制、可长时间阅读。

- 工具 UI 使用清晰的 sans-serif 字体。
- 阅读正文可使用更舒适的正文排版，但不必使用强烈的书籍字体风格。
- 正文区域行距应明显宽于工具区。
- 标题不应过大；Lexis 是学习工具，不是营销落地页。
- 控件文字必须短，避免按钮或标签内换行拥挤。

### 3.3 Shape, Borders, Shadows

界面形状应偏精密、轻量。

- 卡片圆角不宜过大，建议 6-8px。
- 分割线和边框优先于厚重阴影。
- 阴影只用于浮层、底部 sheet、popover 或需要表达层级的区域。
- 不使用大面积玻璃拟态、模糊背景或装饰性光斑。

## 4. Navigation

### 4.1 Mobile

手机端主导航采用底部 Tab，最多 3 个：

- Workspace
- History
- Settings

Lesson Player 进入后应临时沉浸，隐藏或弱化底部 Tab，只保留返回、进度和必要动作。

不设置独立 Dashboard Tab。MVP 不做复杂报表，Dashboard 会稀释核心学习路径。

### 4.2 Pad

Pad 端采用真正的双栏学习工作台，而不是放大版手机。

建议结构：

- 左侧 Rail 或 Sidebar：Workspace / History / Settings。
- Workspace：词包与同步状态、生成控制与最近课程状态并置。
- Lesson Player：左侧阅读正文与辅助内容，右侧练习、反馈、进度。
- History Detail：左侧历史列表，右侧课程复盘详情。

Pad 端应减少模态弹窗，多使用 side panel、inspector 和 inline state。

## 5. Screen Direction

### 5.1 Workspace

Workspace 首屏定位为“今日词包状态 + 生成控制台”。

首屏优先回答：

- Maimemo 是否连接。
- 最近一次同步是否成功。
- 今日新词、复习或模糊词、已掌握词样本是否 ready。
- 用户是否可以生成课程。

Workspace 不应成为复杂首页、欢迎页或学习数据报表页。

### 5.2 Word Package Adjustment

词包调整采用轻量可控边界。

应支持：

- 查看 `New Words`、`Fuzzy/Review Words`、`Mastered Sample` 三组。
- 从本次课程移除少量词。
- 标记 1-3 个重点词。

不做：

- 拖拽排序。
- 标签体系。
- 高级筛选。
- 批量词库编辑。
- 长期词库管理。

`Mastered Sample` 默认作为语境材料，不鼓励用户过度操作。

### 5.3 Lesson Player

手机端 Lesson Player 采用分段式节奏：

1. Reading
2. Aid
3. Exercises
4. Summary

手机上不应让阅读正文和题目长期同屏竞争。练习阶段一屏聚焦一道题，提交后立即展示反馈。

Pad 端可使用双栏：

- 左侧：阅读正文、词汇辅助、语法或长难句分析。
- 右侧：题目、答案输入、即时反馈、进度。

Lesson Player 不使用聊天气泡，不设计自由输入 tutor thread。

### 5.4 Reading Area

正文区域使用轻纸面感。

可以使用：

- 更温和的背景。
- 更宽松的行距。
- 精致的目标词高亮。
- margin notes 或 inline annotations 风格的词汇/句法说明。

避免：

- 整站仿书本。
- 纸张纹理泛滥。
- 翻页动画。
- 高亮过多导致正文变乱。

### 5.5 Feedback

反馈采用短、准、结构化的学习教练式表达。

推荐结构：

1. 判断：正确 / 部分正确 / 需要重看。
2. 原因：一句话说明关键点。
3. 建议：一个具体改进点或下次注意点。

反馈应像高质量批注，不像聊天陪伴，也不是冷冰冰的判题器。

### 5.6 History

History 定位为轻量复盘空间。

列表应展示：

- 课程主题或简短标题。
- CEFR level。
- 日期。
- 完成状态。
- 最终总结入口或摘要状态。

详情页应能复盘：

- 课程正文。
- 用户作答。
- 逐题反馈。
- 最终总结。

不做复杂统计、趋势图、周报、月报或积分系统。

### 5.7 Settings

Settings 主要承载：

- Account/profile basics。
- Maimemo connection。
- Secret saved/error state。
- Session/logout。

Maimemo secret 不显示明文，不返回前端。设置页只展示 saved、not configured、sync failed 等状态。

## 6. Motion And Microinteractions

动效方向为可感知但很轻的精致动效。

适合：

- sync / generate / validate 的细进度状态。
- 状态切换的短淡入。
- feedback 出现时轻微上移或淡入。
- 成功、掌握提升时使用克制的青绿色变化。

避免：

- 大面积流光。
- 粒子效果。
- 3D loading。
- 夸张弹跳。
- 长时间动画阻塞学习。

动效应服务状态理解，不服务装饰。

## 7. Empty, Loading, Error States

状态设计要保持清楚、克制、可恢复。

### Empty

空态要直接说明下一步动作。

示例方向：

- 未连接 Maimemo：引导到 Settings / Connection。
- 无同步数据：提供 Sync action。
- 无历史课程：提示先生成并完成一节课程。

### Loading

Loading 应区分不同任务：

- syncing
- generating
- validating
- feedback pending
- saving summary

不要用一个泛化 spinner 覆盖所有状态。

### Error

错误态必须保留恢复路径。

常见动作：

- Retry sync
- Retry generation
- Regenerate lesson
- Retry feedback
- Return to Workspace

错误文案应说明“发生了什么”和“现在可以做什么”，避免技术细节泄漏和过度解释。

## 8. Explicit Non-Directions

Lexis 第一版不走以下方向：

- Duolingo 式游戏化。
- Streak / 打卡压力机制。
- 积分、排行榜、徽章系统。
- 自由聊天式 AI Tutor。
- 拟人化 AI 老师。
- 大面积紫蓝 AI SaaS 渐变。
- 复杂学习报表。
- 高级词库管理后台。
- 仿书本 App。
- 社交、班级、好友或管理员后台。

这些边界应在后续 Figma、前端实现和组件设计中持续遵守。

## 9. Design Success Criteria

第一版 UI/UX 设计完成后，应满足：

- 手机端能顺畅完成 Workspace -> Generate Lesson -> Lesson Player -> Summary -> History 的核心路径。
- Pad 端能体现双栏学习工作台价值，而不是拉宽手机布局。
- 用户一眼能理解 sync、generation、validation、feedback 的当前状态。
- 阅读正文可长时间阅读，不被控件和反馈干扰。
- AI 有存在感，但不人格化。
- 反馈有教学价值，但不冗长。
- 色彩克制，高级感来自层级、留白、状态与细节，而不是装饰。
