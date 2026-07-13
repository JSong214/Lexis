# Lexis 项目约定

## 需求来源

- 产品范围、业务流程、数据模型和 API 约束以 `docs/English Learning AI Agent PRD.md` 为准；实现前先阅读相关章节。
- 如果代码与 PRD 冲突，先指出冲突，不要静默扩大 MVP 范围。

## 技术与架构

- 前端使用 React + TypeScript；后端使用 Python + FastAPI；数据层使用 PostgreSQL、SQLAlchemy 2.0 和 Alembic。
- 按可运行的垂直切片开发，保持前后端真实 API 路径连通；外部服务不可用时保留 `MockMaimemoSyncProvider` 和 `MockLLMProvider`。
- Maimemo 通过 `MaimemoSyncProvider` 接入，只读、不写回学习状态；AI 通过 `LLMProvider` 接入，输出必须经过 schema 和规则校验。
- `ContextLesson` 只保存课程内容；用户作答、反馈和总结保存到独立的数据结构中。

## 安全与外部 API

- Maimemo token 和 AI key 只能保存在后端环境或安全存储中；不得写入前端、普通日志或源码。Maimemo token 入库必须加密。
- 调用 Maimemo API 前，按官方文档验证 endpoint、字段和响应结构；请求使用 `Authorization: Bearer <token>`。
- 参考：[Maimemo Open API](https://open.maimemo.com/#/)、[memo-skills](https://github.com/maimemo/memo-skills/tree/main)。

## 验证

- Backend：`cd backend; uv run pytest; uv run ruff check .`
- Frontend：`cd frontend; npm run lint; npm run build`
- 只修改与当前任务直接相关的文件；接口或行为变化时同步更新对应文档和测试。
