# AlphaRadar 后端代码完成计划

## Summary
先完成后端代码主链，不处理前端。目标是把当前骨架补成一条可运行闭环：`Wallet -> Scan -> Queue -> Worker -> SignalEvent -> RAG -> LangGraph -> Lead + AgentRun`。  
`AgentRun` 采用轻量审计方案，不复制 LangSmith 的全部 tracing 数据。

## Key Changes

### 1. 先收敛领域模型和 API 边界
- 固定 MVP 的核心实体：`Wallet`、`CandidateWallet`、`Scan`、`Asset`、`SignalEvent`、`EvidenceItem`、`Lead`、`AgentRun`
- 将 `AgentRun` 收缩为轻量审计模型，只保留业务关联和 LangSmith trace 链接
- 补齐真实可用的 schema：
  - `LeadRead`
  - `EvidenceRead`
  - `AgentRunRead`
- 补齐真实 API：
  - `GET /api/v1/leads`
  - `GET /api/v1/leads/{id}`
  - `GET /api/v1/evidence`
  - `GET /api/v1/evidence/{id}`
  - `GET /api/v1/agent-runs`
  - `GET /api/v1/agent-runs/{id}`

### 2. 打通 scan 和 worker 执行闭环
- 把 Redis queue payload 改成 JSON 序列化，禁止 `str(payload)`
- 增加 worker runner，持续消费 `alpharadar:jobs:scan`
- 固定 `Scan.status` 状态流转：
  - `queued`
  - `running`
  - `succeeded`
  - `failed`
- `POST /api/v1/scans` 只做建单和入队，不做实际扫描
- worker 负责回写 `started_at`、`finished_at`、`error_message`、计数结果

### 3. 先做 deterministic signal pipeline
- 先不上复杂 LLM 判断，先把链上信号生成做实
- 增加 Helius integration 抽象层，至少提供：
  - wallet history / transfers
  - wallet balances
  - asset metadata
- 增加 fixture provider，保证无 API key 也能跑测试
- 将 provider 结果标准化成 `SignalEvent`
- 实现第一版 anomaly scoring：
  - 大额异动
  - 新 token 增仓
  - 多 monitored wallets 共振
  - 可识别 counterparty / funding relation
- 只让高于阈值的 signal 进入后续 LangGraph 分析

### 4. 再做 RAG evidence pipeline
- 新增 evidence ingestion 服务，先支持新闻和项目资料
- Evidence 入库字段固定：
  - `evidence_type`
  - `title`
  - `source_url`
  - `published_at`
  - `fetched_at`
  - `summary`
  - `metadata`
  - `embedding`
- embedding 默认 OpenAI `text-embedding-3-small`
- 先实现可用检索：
  - keyword filter
  - 时间新鲜度
  - 向量相似度
- pgvector 作为 Postgres 主路径；SQLite 测试环境允许保留兼容 fallback

### 5. 最后替换 LangGraph placeholder 节点
- 保留当前线性 `StateGraph` 编排，不引入 supervisor
- 节点职责固定：
  - `load_signal_context`
  - `onchain_signal_agent`
  - `market_context_agent`
  - `rag_research_agent`
  - `risk_skeptic_agent`
  - `lead_synthesizer`
  - `persist_agent_run`
- 所有节点只通过 typed state 传递结构化结果
- LLM 输出必须走 Pydantic schema 校验
- `persist_agent_run` 同时完成：
  - 写入轻量 `AgentRun`
  - 写入 `Lead`
  - 关联 `SignalEvent` / `EvidenceItem`

### 6. LangSmith 与本地审计边界
- LangSmith 负责 runtime tracing 和调试
- 本地 `AgentRun` 只保留业务查询所需最小字段
- API 返回的 `AgentRunRead` 以业务可读为主，不暴露全部 provider 内部细节
- 若 LangSmith 未开启，后端仍必须能用 fixture 模式完成 scan 和 lead 生成

## Implementation Order
1. 收缩 `AgentRun` 模型和 schema，补齐 `Lead` / `Evidence` / `AgentRun` 的 repository、service、API。
2. 重构 queue 为 JSON job，增加 worker runner 和 scan 状态流转。
3. 增加 fixture-based worker path，确保不依赖外部 key 也能跑完整闭环。
4. 实现 Helius integration 和 `SignalEvent` normalization。
5. 实现 anomaly scoring，并把低质量事件挡在 LangGraph 之前。
6. 实现 evidence ingestion、embedding、retrieval。
7. 增加 pgvector migration，并保留 SQLite 测试 fallback。
8. 替换 LangGraph placeholder 节点，落库 `Lead` 和轻量 `AgentRun`。
9. 跑完整后端测试，修复回归。

## Test Plan
- 单元测试：
  - wallet CRUD 与重复地址冲突
  - candidate wallet approve/reject 冲突
  - queue JSON 序列化与消费
  - scan 状态流转
  - anomaly scoring fixtures
  - evidence ingestion 与 retrieval
  - LangGraph output schema 校验
- 集成测试：
  - `POST /api/v1/scans` 创建 scan 并成功入队
  - worker 消费 job 后生成 `SignalEvent`
  - 高分 signal 进入 LangGraph
  - workflow 生成 `Lead` 和轻量 `AgentRun`
  - `GET /leads`、`GET /evidence`、`GET /agent-runs` 能读到真实持久化结果
- 验收标准：
  - 没有 Helius/OpenAI/LangSmith key 也能通过 fixture 路径跑通后端测试
  - 有真实 key 时可切换到真实 provider，不改 service 和 workflow 主逻辑

## Assumptions
- 当前阶段完全不做前端。
- `AgentRun` 保留为轻量本地审计，不做 LangSmith 全量镜像。
- MVP 只支持 Solana。
- Helius 是默认链上 provider。
- OpenAI 是默认 embedding 和分析 provider。
- Multi-agent 继续采用线性 LangGraph workflow，不做自由协作式 agent system。
