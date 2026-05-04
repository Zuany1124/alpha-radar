# Solana Alpha Evidence Radar 需求分析

## 1. 项目背景

Solana 链上资金流动速度快，部分高质量钱包的转账、建仓、换仓、资金归集等行为可能提前反映市场关注度变化。但单纯观察链上动作容易产生噪声：钱包身份不明确、代币流动性不足、新闻滞后、项目背景缺失、资金来源复杂，都会导致误判。

本项目拟建设一个个人研究型仪表盘，用于持续观察 Solana “smart money” 钱包活动，将链上信号与市场数据、新闻资料、项目材料和风险审查连接起来，形成可追溯的证据链，帮助用户判断某个信号是否值得进一步研究。

系统不负责交易，不生成下单指令，不接入交易私钥，也不提供自动执行能力。

## 2. 项目目标

### 2.1 核心目标

- 发现值得关注的 Solana 钱包异动。
- 将钱包行为、资产信息、市场上下文、新闻/项目资料整合成结构化线索。
- 为每条线索提供清晰的证据来源、风险提示、置信度和新鲜度。
- 支持用户维护种子 smart-wallet 列表，并审批系统推荐的候选钱包。
- 通过本地优先的 Docker Compose 架构，便于个人部署、迭代和调试。

### 2.2 非目标

- 不执行交易。
- 不生成买入、卖出、止盈、止损等交易指令。
- 不保存或接触交易私钥。
- MVP 不覆盖社交媒体分析。
- MVP 不做多链支持，仅聚焦 Solana。
- MVP 不以云端生产部署为首要目标。

## 3. 目标用户与使用场景

### 3.1 目标用户

主要用户是个人加密研究者或交易研究员，具备一定链上分析能力，希望通过工具化方式降低重复监控成本，并保留每个研究结论背后的证据链。

### 3.2 典型使用场景

- 用户导入一组已知 smart-wallet 地址，系统定期扫描其链上活动。
- 系统发现某个钱包对某个资产出现异常资金流入、余额变化或重复行为模式。
- 系统补充该资产的价格、成交量、流动性、相关新闻和项目资料。
- 多个分析 Agent 对信号进行检测、解释、检索、质疑和综合。
- 用户在仪表盘查看 ranked alpha leads，并进入详情页检查证据链。
- 用户审批或拒绝系统推荐的候选钱包，逐步扩展 watchlist。
- 用户手动触发一次扫描，用于验证最新链上变化。

## 4. 范围边界

### 4.1 MVP 范围

- Solana 链上钱包活动监控。
- 用户维护 seed wallets。
- 系统推荐 candidate wallets，且必须经用户审批后进入正式 watchlist。
- 30 分钟默认批处理扫描。
- 手动扫描触发。
- 钱包转账、资金来源、代币余额变化、相关实体和重复共动模式分析。
- 基于 Helius Wallet API 的链上数据获取。
- 新闻和项目/代币资料的 RAG 语料库。
- 基于 LangGraph 的多 Agent 分析流程。
- React 仪表盘展示线索列表、详情、证据和候选钱包审批。
- FastAPI 提供资源化 API。
- Postgres + pgvector 存储业务数据、证据和向量。
- Redis/队列支撑异步任务。
- OpenAI API 用于结构化分析和 embeddings。

### 4.2 延后范围

- 社交媒体信号，例如 X、Telegram、Discord、Reddit。
- 自动交易、半自动交易或交易所/DEX 下单。
- 多链扩展，例如 Ethereum、Base、BSC。
- 复杂实体图谱、可视化资金网络图。
- 团队协作、权限系统和多用户工作流。
- 云端部署、监控告警和生产级运维。

## 5. 功能需求

### 5.1 钱包与 Watchlist 管理

系统应支持用户维护 Solana 钱包地址列表。

主要需求：

- 添加、编辑、删除 seed wallet。
- 为钱包记录标签、备注、来源和可信度。
- 查询钱包详情，包括最近活动、相关资产、历史信号和入选原因。
- 展示系统推荐的 candidate wallet。
- 用户可以批准或拒绝 candidate wallet。
- 未经批准的 candidate wallet 不应进入正式扫描 watchlist。

### 5.2 链上扫描

系统应定期扫描 watchlist 中的钱包活动。

主要需求：

- 默认每 30 分钟执行一次批量扫描。
- 支持从 UI 手动触发扫描。
- 采集钱包转账、代币余额变化、资金来源和相关实体。
- 识别重复 co-movement 模式，例如多个钱包在相近时间窗口内对同一资产出现相似动作。
- 将原始链上事件归一化为系统内部的 `SignalEvent`。
- 记录每次扫描的开始时间、结束时间、状态、错误信息和影响范围。

### 5.3 信号评分

系统应对链上活动进行异常程度和研究价值评分。

主要需求：

- 为每个 `SignalEvent` 计算 anomaly score。
- 评分应考虑钱包历史行为、资产规模、资金变化幅度、重复行为、时间窗口和噪声特征。
- 明显噪声或低质量活动应被过滤，或生成低置信度结果。
- 评分逻辑应可测试、可回放，并支持固定 fixture 回归测试。

### 5.4 市场上下文

系统应为链上信号补充市场背景。

主要需求：

- 获取相关资产的价格、成交量、流动性和近期变化。
- 标记低流动性、高滑点或异常成交量风险。
- 将市场上下文与 signal event 关联保存。
- 当市场数据缺失或过期时，应在 lead 中明确标记。

### 5.5 RAG 证据检索

系统应建立新闻和项目资料语料库，用于解释资产背景和近期事件。

主要需求：

- 支持从可配置 RSS、API 或网页来源导入新闻和项目/token 材料。
- 为文档生成 embeddings，并存入 pgvector。
- 对每个 signal 检索相关背景材料。
- 每条证据应保留标题、来源链接、发布时间、抓取时间、摘要和引用 ID。
- MVP 不接入社交媒体语料。

### 5.6 多 Agent 分析工作流

系统应使用 LangGraph 编排多角色 Agent，对每条候选信号生成结构化 lead。

Agent 角色：

- On-chain Signal Agent：识别异常钱包行为。
- Market Context Agent：补充价格、成交量和流动性上下文。
- RAG Research Agent：检索新闻和项目背景。
- Risk/Skeptic Agent：指出证据薄弱、低流动性陷阱、过期新闻和噪声信号。
- Lead Synthesizer：生成最终结构化 lead。

主要需求：

- Agent 输出必须使用 JSON Schema 或 Structured Outputs 约束。
- 每次 Agent 执行应记录 `AgentRun`，包括输入、输出、状态、耗时、模型和错误。
- 最终 lead 必须可追溯到 signal events、evidence items 和 agent runs。
- Agent 结论应区分事实、推断和风险提示。

### 5.7 Lead 展示

React 仪表盘应展示 ranked alpha leads。

列表页应展示：

- 标题。
- 钱包。
- 资产。
- movement type。
- anomaly score。
- agent verdict。
- confidence。
- freshness timestamp。
- “why this matters” 摘要。

详情页应展示：

- signal summary。
- 相关钱包和资产。
- evidence list。
- risk notes。
- confidence score。
- source links/IDs。
- 关联的 agent run 历史。
- 原始或归一化链上事件摘要。

### 5.8 API

FastAPI 应提供资源化接口。

核心资源：

- watchlists。
- wallets。
- candidate wallets。
- scans。
- leads。
- evidence。
- agent runs。

主要需求：

- 支持 dashboard 查询。
- 支持 lead 详情查询。
- 支持钱包和 watchlist 管理。
- 支持 candidate wallet 审批。
- 支持手动 scan trigger。
- API 响应结构应稳定，便于前端迭代。

## 6. 数据对象需求

系统至少应包含以下核心实体：

- `Wallet`：正式监控的钱包。
- `CandidateWallet`：系统推荐但待用户审批的钱包。
- `Asset`：Solana token 或相关资产。
- `SignalEvent`：归一化后的链上信号事件。
- `EvidenceItem`：新闻、项目资料、市场数据或链上证据。
- `Lead`：最终研究线索。
- `AgentRun`：一次 Agent 工作流或单个 Agent 节点执行记录。

`Lead` 必须包含：

- title。
- asset/wallet references。
- signal summary。
- evidence list。
- risk notes。
- confidence score。
- freshness timestamp。
- source links/IDs。

## 7. 非功能需求

### 7.1 可追溯性

每条 lead 都应能追溯到原始链上事件、市场上下文、RAG 证据和 Agent 输出。系统不应只保存最终自然语言结论。

### 7.2 可审计性

Agent 输出应结构化保存。关键字段应具备 schema 校验，便于测试、回放和问题定位。

### 7.3 可配置性

扫描频率、数据源、seed wallet、RAG 来源和模型配置应可配置。MVP 默认扫描频率为 30 分钟。

### 7.4 本地优先

系统目标运行环境为 Docker Compose，本地包含 frontend、API、worker、Postgres/pgvector 和 Redis。

### 7.5 安全边界

系统不得要求交易私钥。不得包含自动下单权限。所有输出应定位为研究线索，而非交易建议。

### 7.6 可测试性

信号评分、RAG 检索、结构化 Agent 输出、worker 流程、API 和 UI 关键路径都应具备测试覆盖。

## 8. 技术约束

默认技术栈：

- Frontend：React。
- API：Python FastAPI。
- Worker：独立 Python workers。
- Workflow：LangGraph。
- Database：Postgres + pgvector。
- Queue/Cache：Redis。
- LLM：OpenAI API。
- Embeddings：默认 `text-embedding-3-small`，后续可升级 `text-embedding-3-large`。
- Solana Data Provider：Helius Wallet API。
- Runtime：本地 Docker Compose。

实现前应重新获取相关框架、SDK、API 和 CLI 的当前官方文档，尤其是 Helius、LangGraph、FastAPI、React、pgvector、OpenAI Structured Outputs 和 embeddings。

## 9. 关键业务流程

### 9.1 定时扫描流程

1. Worker 按默认 30 分钟周期启动扫描。
2. 系统读取已批准 watchlist 钱包。
3. 通过 Helius 获取钱包活动、转账和余额变化。
4. 系统归一化链上数据并生成 `SignalEvent`。
5. 信号评分模块计算 anomaly score。
6. 达到候选阈值的事件进入 LangGraph 分析流程。
7. Agent 补充市场、RAG 和风险上下文。
8. Lead Synthesizer 生成结构化 `Lead`。
9. API 将最新 lead 提供给前端展示。

### 9.2 手动扫描流程

1. 用户在 UI 触发手动扫描。
2. API 创建 scan job 并返回任务状态。
3. Worker 执行指定范围扫描。
4. 前端轮询或刷新 scan 状态和新 lead。

### 9.3 Candidate Wallet 审批流程

1. 系统根据资金关联、重复共动或来源关系推荐 candidate wallet。
2. 前端展示推荐原因、关联钱包和证据。
3. 用户批准后，candidate wallet 转为正式 `Wallet`。
4. 用户拒绝后，系统保留拒绝记录，避免重复推荐同一地址。

## 10. 风险与待确认问题

### 10.1 产品风险

- “smart money” 定义可能主观，初始 seed wallet 质量会显著影响结果质量。
- 链上异动与真实 alpha 之间不一定存在稳定因果关系。
- 低流动性资产容易制造高 anomaly score 但研究价值低。
- 新闻和项目资料可能滞后，导致解释偏差。

### 10.2 技术风险

- Helius API 限额、字段覆盖和历史数据可用性会影响扫描完整性。
- 钱包实体关联和 co-movement 检测可能复杂度较高，需要从简单规则开始。
- LangGraph 多 Agent 成本和延迟需要控制。
- pgvector 检索质量依赖文档清洗、切分和 metadata 设计。

### 10.3 待确认问题

- 初始 seed wallet 数量和来源。
- MVP 首批新闻/项目资料数据源。
- 市场数据来源，例如 DEX 聚合器、价格 API 或自建索引。
- anomaly score 的初始阈值和排序权重。
- 前端是否需要实时刷新，还是定时刷新即可。
- 是否需要登录鉴权；本地单用户 MVP 可暂不引入。

## 11. 验收标准

MVP 可按以下标准验收：

- 用户可以添加 seed wallet，并在 dashboard 中看到其扫描状态。
- Worker 能按 30 分钟默认周期执行扫描，也能响应手动触发。
- 至少一种钱包异动 fixture 能生成 `SignalEvent` 和 anomaly score。
- 至少一条候选信号能完成 LangGraph 分析并生成结构化 `Lead`。
- Lead 详情页能展示 signal summary、evidence list、risk notes、confidence 和 source links/IDs。
- Candidate wallet 可以被批准或拒绝。
- 噪声钱包活动 fixture 会被过滤，或生成低置信度 lead。
- RAG 文档可被导入、向量化、检索，并关联到 lead。
- 关键 API 具备测试覆盖。
- UI smoke test 覆盖 lead list、lead detail、evidence display 和 candidate wallet approval flow。

## 12. 建议实施优先级

### P0：系统骨架与数据闭环

- Docker Compose。
- Postgres/pgvector。
- Redis。
- FastAPI 基础资源接口。
- Worker job 框架。
- React 基础 dashboard。
- 核心数据模型。

### P1：链上信号 MVP

- Seed wallet 管理。
- Helius 数据接入。
- 钱包活动归一化。
- 基础 anomaly score。
- `SignalEvent` 存储与回放测试。

### P2：Lead 生成

- LangGraph 工作流。
- OpenAI Structured Outputs。
- RAG ingestion 和 retrieval。
- Market context 接入。
- Risk/Skeptic Agent。
- Lead Synthesizer。

### P3：研究体验完善

- Lead 排序和筛选。
- Lead 详情证据链。
- Candidate wallet 推荐和审批。
- Agent run 历史。
- 噪声过滤回归测试。

## 13. 成功指标

- 用户可以在一个页面快速判断哪些 Solana 钱包异动值得进一步研究。
- 每条 lead 都能说明“为什么重要”和“为什么可能不可靠”。
- 用户能追溯每个结论背后的链上事件、资料来源和 Agent 输出。
- 系统能持续运行本地扫描，并稳定产生可审查的结构化记录。
- 噪声信号不会被包装成高置信度结论。
