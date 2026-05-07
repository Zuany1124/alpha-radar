# AlphaRadar

AlphaRadar 是一个本地优先的 Solana 链上研究仪表盘，用于监控智能钱包活动，把高噪声的链上行为整理成可追溯的研究线索。

项目定位是研究辅助系统，而不是交易系统：它不执行交易、不保存私钥、不生成自动下单指令。核心目标是采集链上信号、沉淀证据、评估风险，并通过结构化 API 和前端界面支持后续分析。

## 项目简介

AlphaRadar 围绕“钱包监控 -> 链上信号 -> 证据检索 -> 风险复核 -> 研究线索”构建。

当前仓库包含：

- FastAPI 后端资源 API，提供钱包、候选钱包、扫描任务、线索、证据和 Agent 运行记录接口。
- Redis 队列和 Python Worker，用于把长耗时扫描任务移出请求生命周期。
- Solana 活动采集适配层，支持 Helius 数据源和本地 fixture 数据源。
- LangGraph 线索分析工作流，将链上信号、市场上下文、RAG 证据和风险复核串成可审计流程。
- Postgres 数据模型和 Alembic 迁移，保存钱包、资产、信号事件、证据、线索、扫描和 Agent 运行记录。
- Next.js Web3 前端脚手架，包含钱包连接、主题、国际化和 Web3 provider 基础能力。

## 技术栈

### 后端

- Python 3.12
- FastAPI：HTTP API、OpenAPI 文档、健康检查和就绪检查
- SQLAlchemy 2.x：ORM 和仓储层
- Alembic：数据库迁移
- Postgres：核心业务数据存储
- Redis：异步任务队列
- LangGraph：多步骤 Agent 工作流编排
- OpenAI SDK：后续 LLM 分析和 embedding 接入
- Elasticsearch：证据检索索引的可选后端
- Helius：Solana 链上活动数据源
- pytest：后端测试
- uv：Python 依赖和命令运行

### 前端

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS 4
- shadcn/ui 风格组件基础
- wagmi、viem、RainbowKit：Web3 钱包和链交互
- Privy：可选登录和嵌入式钱包能力
- TanStack Query：异步状态管理
- Zustand：轻量客户端状态
- next-intl：国际化
- pnpm：前端包管理

## 项目架构

```text
.
├── docs/
│   ├── DESIGN.md
│   └── solana-alpha-evidence-radar-requirements.md
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── wallets.py
│   │   │       ├── candidate_wallets.py
│   │   │       ├── scans.py
│   │   │       ├── leads.py
│   │   │       ├── evidence.py
│   │   │       └── agent_runs.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   └── session.py
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── workers/
│   │       ├── integrations/
│   │       ├── jobs/
│   │       ├── workflows/
│   │       ├── queue.py
│   │       └── runner.py
│   ├── alembic/
│   ├── tests/
│   └── pyproject.toml
└── frontend/
    ├── app/
    ├── components/
    ├── hooks/
    ├── lib/
    ├── providers/
    ├── stores/
    └── package.json
```

### 后端分层

- `api/`：FastAPI 路由层，只处理请求参数、响应模型和依赖注入。
- `schemas/`：Pydantic 输入输出模型。
- `services/`：业务服务层，承载钱包管理、扫描创建、证据检索、线索查询等用例。
- `repositories/`：数据访问层，封装 SQLAlchemy 查询和持久化细节。
- `models/`：数据库实体模型。
- `workers/queue.py`：Redis 队列抽象，提供生产和消费 scan job 的能力。
- `workers/jobs/scan_job.py`：扫描任务执行入口，负责采集、归一化、评分、候选钱包推荐和工作流触发。
- `workers/workflows/lead_analysis/`：LangGraph 线索分析工作流。

### 前端分层

- `app/`：Next.js App Router 页面。
- `components/ui/`：通用 UI 基础组件。
- `components/wallet/`：钱包连接、账号信息和网络状态组件。
- `lib/config/`：链、wagmi、Privy 和功能配置。
- `providers/`：React Query、wagmi、RainbowKit、Privy 和主题 Provider。
- `hooks/`：合约写入、余额读取和挂载状态等复用逻辑。
- `messages/`：中英文国际化文案。

## 运行方式

### 1. 准备基础服务

后端默认依赖本地 Postgres 和 Redis：

```bash
Postgres: localhost:5432
Redis: localhost:6379
Database: alpharadar
User: alpharadar
Password: alpharadar
```

当前仓库没有提供 `docker-compose.yml`，需要你自行启动 Postgres 和 Redis，或调整 `backend/.env` 中的连接配置。

### 2. 启动后端 API

```bash
cd backend
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

后端默认地址：

- API: `http://127.0.0.1:8000`
- OpenAPI: `http://127.0.0.1:8000/docs`
- 健康检查: `GET /health`
- 就绪检查: `GET /ready`

### 3. 启动后端 Worker

扫描任务通过 API 创建后会进入 Redis 队列，Worker 负责消费并执行：

```bash
cd backend
uv run python -m app.workers.runner
```

### 4. 启动前端

```bash
cd frontend
cp .env.example .env.local
pnpm install
pnpm dev
```

前端默认地址：

```text
http://127.0.0.1:3000
```

### 5. 运行测试

后端测试：

```bash
cd backend
uv run pytest
```

前端检查：

```bash
cd frontend
pnpm type-check
pnpm build
```

## 核心 API

后端 API 统一挂载在 `/api/v1`：

- `GET /api/v1/wallets`：查询钱包列表
- `POST /api/v1/wallets`：创建监控钱包
- `PATCH /api/v1/wallets/{wallet_id}`：更新钱包
- `DELETE /api/v1/wallets/{wallet_id}`：删除钱包
- `GET /api/v1/candidate-wallets`：查询候选钱包
- `POST /api/v1/scans`：创建手动扫描任务并写入队列
- `GET /api/v1/scans`：查询扫描列表
- `GET /api/v1/leads`：查询研究线索
- `GET /api/v1/evidence`：查询证据记录
- `GET /api/v1/agent-runs`：查询 Agent 工作流运行记录

## 工作流编排

AlphaRadar 的长任务被拆成两层：队列任务编排和 LangGraph 分析编排。

### 队列任务编排

```text
POST /api/v1/scans
  |
  v
ScanService.create_scan
  |
  v
RedisQueueClient.enqueue("scan", {"scan_id": ...})
  |
  v
ScanWorkerRunner.run_forever
  |
  v
run_scan_job(scan_id)
```

`run_scan_job` 的主要步骤：

1. 加载扫描记录和目标钱包。
2. 根据配置选择 Helius 数据源或 fixture 数据源。
3. 拉取钱包历史和转账记录。
4. 归一化 Solana 活动为内部 `SignalEvent`。
5. 对信号事件进行异常评分。
6. 持久化信号事件，并根据阈值推荐候选钱包。
7. 导入 fixture 证据数据，构建证据检索服务。
8. 触发 LangGraph `lead_analysis` 工作流。
9. 回写扫描状态、创建线索和 Agent 运行记录。

### LangGraph 线索分析编排

当前工作流定义在 `backend/app/workers/workflows/lead_analysis/graph.py`：

```text
START
  |
  v
load_signal_context
  |
  v
onchain_signal_agent
  |
  v
market_context_agent
  |
  v
rag_research_agent
  |
  v
risk_skeptic_agent
  |
  v
lead_synthesizer
  |
  v
persist_agent_run
  |
  v
END
```

各节点职责：

- `load_signal_context`：从数据库加载扫描产生的信号事件、资产和钱包上下文。
- `onchain_signal_agent`：提炼主要链上异常信号，输出资产、钱包、事件类型和异常分数。
- `market_context_agent`：预留市场上下文分析节点，当前为占位输出。
- `rag_research_agent`：基于资产和事件类型检索证据，输出关联 evidence id。
- `risk_skeptic_agent`：结合证据完整性和异常分数做风险复核。
- `lead_synthesizer`：生成结构化研究线索，包括标题、信号摘要、风险提示、置信度和结论。
- `persist_agent_run`：保存 Agent 运行记录和最终 Lead，保证线索可以追溯到输入信号与证据。

## 关键配置

后端配置来自 `backend/.env`：

```env
DATABASE_URL=postgresql+psycopg://alpharadar:alpharadar@localhost:5432/alpharadar
REDIS_URL=redis://localhost:6379/0
HELIUS_API_KEY=
OPENAI_API_KEY=
SIGNAL_PROVIDER=auto
SIGNAL_ANOMALY_THRESHOLD=0.65
DEFAULT_EMBEDDING_MODEL=text-embedding-3-small
DEFAULT_ANALYSIS_MODEL=gpt-4.1-mini
ELASTICSEARCH_URL=
LANGSMITH_TRACING=false
LANGSMITH_PROJECT=alpharadar-local
```

常用数据源模式：

- `SIGNAL_PROVIDER=fixture`：使用本地测试数据，适合开发和测试。
- `SIGNAL_PROVIDER=helius`：强制使用 Helius，需要配置 `HELIUS_API_KEY`。
- `SIGNAL_PROVIDER=auto`：有 `HELIUS_API_KEY` 时使用 Helius，否则回退到 fixture。

前端配置来自 `frontend/.env.local`：

```env
NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID=your_walletconnect_project_id
NEXT_PUBLIC_PRIVY_APP_ID=your_privy_app_id
NEXT_PUBLIC_ALCHEMY_ID=your_alchemy_api_key
```

## 文档

- `docs/solana-alpha-evidence-radar-requirements.md`：产品需求和 MVP 范围。
- `docs/DESIGN.md`：界面设计方向和视觉系统。
- `backend/doc/architecture.md`：后端架构说明。
- `backend/README.md`：后端快捷命令。
