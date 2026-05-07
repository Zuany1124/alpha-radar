# AlphaRadar Backend API 文档

本文档描述 `backend` 当前公开的 HTTP API。接口实现基于 FastAPI，业务路由统一挂载在 `/api/v1` 下。

## 基础信息

- 服务名：AlphaRadar Backend
- API 版本：`0.1.0`
- 默认地址：`http://localhost:8000`
- 业务接口前缀：`/api/v1`
- 数据格式：请求体和响应体均为 JSON
- 时间格式：ISO 8601 字符串，例如 `2026-05-05T00:00:00Z`

## 通用约定

### 分页参数

列表接口统一支持：

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `limit` | integer | `50` | 返回数量 |
| `offset` | integer | `0` | 偏移量 |

列表响应统一为：

```json
{
  "items": []
}
```

### 常见错误响应

FastAPI 默认错误格式：

```json
{
  "detail": "错误原因"
}
```

常见状态码：

| 状态码 | 说明 |
| --- | --- |
| `200` | 请求成功 |
| `201` | 创建成功 |
| `204` | 删除成功，无响应体 |
| `404` | 资源不存在 |
| `409` | 资源冲突或状态不允许 |
| `422` | 请求参数或请求体校验失败 |

## 健康检查

### GET `/health`

检查服务进程是否可用。

响应示例：

```json
{
  "status": "ok",
  "service": "alpharadar-backend"
}
```

### GET `/ready`

检查数据库和队列是否可用。

响应示例：

```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "queue": "ok"
  }
}
```

## Wallet API

Wallet 表示已确认纳入监控或研究范围的钱包。

### Wallet 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | Wallet ID |
| `address` | string | 钱包地址 |
| `label` | string/null | 标签 |
| `notes` | string/null | 备注 |
| `source` | string/null | 来源 |
| `confidence` | number/null | 置信度，范围 `0` 到 `1` |
| `status` | string | 状态 |
| `created_at` | string | 创建时间 |
| `updated_at` | string | 更新时间 |

### GET `/api/v1/wallets`

查询 Wallet 列表。

查询参数：

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `limit` | integer | `50` | 返回数量 |
| `offset` | integer | `0` | 偏移量 |

响应：`WalletList`

```json
{
  "items": [
    {
      "id": "wallet_1",
      "address": "9xQeWvG816bUx9EPfWfBa7DPTbQsvqKkdZ2wLQf9Y5J",
      "label": "Seed wallet",
      "notes": "Known smart wallet",
      "source": "manual",
      "confidence": 0.8,
      "status": "active",
      "created_at": "2026-05-05T00:00:00Z",
      "updated_at": "2026-05-05T00:00:00Z"
    }
  ]
}
```

### POST `/api/v1/wallets`

创建 Wallet。地址已存在时返回 `409`。

请求体：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `address` | string | 是 | 钱包地址，长度 `1` 到 `128` |
| `label` | string/null | 否 | 标签 |
| `notes` | string/null | 否 | 备注 |
| `source` | string/null | 否 | 来源 |
| `confidence` | number/null | 否 | 置信度，范围 `0` 到 `1` |

请求示例：

```json
{
  "address": "9xQeWvG816bUx9EPfWfBa7DPTbQsvqKkdZ2wLQf9Y5J",
  "label": "Seed wallet",
  "notes": "Known smart wallet",
  "source": "manual",
  "confidence": 0.8
}
```

响应：`201 Created`，返回 `Wallet`。

### GET `/api/v1/wallets/{wallet_id}`

查询 Wallet 详情。不存在时返回 `404`。

路径参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `wallet_id` | string | Wallet ID |

响应：`Wallet`

### PATCH `/api/v1/wallets/{wallet_id}`

更新 Wallet。不存在时返回 `404`。

请求体：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `label` | string/null | 否 | 标签 |
| `notes` | string/null | 否 | 备注 |
| `source` | string/null | 否 | 来源 |
| `confidence` | number/null | 否 | 置信度，范围 `0` 到 `1` |
| `status` | string/null | 否 | 状态 |

请求示例：

```json
{
  "label": "Updated seed"
}
```

响应：`Wallet`

### DELETE `/api/v1/wallets/{wallet_id}`

删除 Wallet。不存在时返回 `404`。

响应：`204 No Content`

## Candidate Wallet API

Candidate Wallet 表示系统推荐但尚未人工确认的钱包。

### CandidateWallet 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | Candidate Wallet ID |
| `address` | string | 钱包地址 |
| `recommendation_reason` | string | 推荐原因 |
| `related_wallet_ids` | string[] | 关联 Wallet ID 列表 |
| `evidence_ids` | string[] | 关联 Evidence ID 列表 |
| `status` | string | 状态，例如 `pending`、`approved`、`rejected` |
| `reviewed_at` | string/null | 审核时间 |
| `created_at` | string | 创建时间 |
| `updated_at` | string | 更新时间 |

### GET `/api/v1/candidate-wallets`

查询 Candidate Wallet 列表。

查询参数：

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `limit` | integer | `50` | 返回数量 |
| `offset` | integer | `0` | 偏移量 |

响应：`CandidateWalletList`

### GET `/api/v1/candidate-wallets/{candidate_wallet_id}`

查询 Candidate Wallet 详情。不存在时返回 `404`。

路径参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `candidate_wallet_id` | string | Candidate Wallet ID |

响应：`CandidateWallet`

### POST `/api/v1/candidate-wallets/{candidate_wallet_id}/approve`

批准 Candidate Wallet，并创建对应 Wallet。候选钱包不是 `pending` 状态时返回 `409`。

响应示例：

```json
{
  "status": "approved",
  "wallet": {
    "id": "wallet_1",
    "address": "Cand111111111111111111111111111111111111111",
    "label": null,
    "notes": "Repeated co-movement with a seed wallet",
    "source": "candidate_approval",
    "confidence": null,
    "status": "active",
    "created_at": "2026-05-05T00:00:00Z",
    "updated_at": "2026-05-05T00:00:00Z"
  }
}
```

### POST `/api/v1/candidate-wallets/{candidate_wallet_id}/reject`

拒绝 Candidate Wallet。候选钱包不是 `pending` 状态时返回 `409`。

响应：`CandidateWallet`

## Scan API

Scan 表示一次扫描任务。手动创建 Scan 后，后端会写入队列，由 worker 异步消费。

### Scan 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | Scan ID |
| `trigger` | string | 触发方式，目前创建接口仅支持 `manual` |
| `scope` | object | 扫描范围 |
| `status` | string | 状态，例如 `queued`、`succeeded`、`failed` |
| `started_at` | string/null | 开始时间 |
| `finished_at` | string/null | 结束时间 |
| `error_message` | string/null | 失败原因 |
| `created_signal_event_count` | integer | 本次扫描创建的 SignalEvent 数量 |
| `created_lead_count` | integer | 本次扫描创建的 Lead 数量 |
| `created_at` | string | 创建时间 |
| `updated_at` | string | 更新时间 |

### GET `/api/v1/scans`

查询 Scan 列表。

查询参数：

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `limit` | integer | `50` | 返回数量 |
| `offset` | integer | `0` | 偏移量 |

响应：`ScanList`

### POST `/api/v1/scans`

创建手动 Scan 并写入队列。

请求体：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `trigger` | string | 否 | `manual` | 触发方式，只允许 `manual` |
| `scope` | object | 否 | `{}` | 扫描范围，例如钱包 ID 列表 |

请求示例：

```json
{
  "trigger": "manual",
  "scope": {
    "wallet_ids": ["wallet-1"]
  }
}
```

响应：`201 Created`，返回 `Scan`。

### GET `/api/v1/scans/{scan_id}`

查询 Scan 详情。不存在时返回 `404`。

响应：`Scan`

## Lead API

Lead 表示由信号、证据和 Agent 分析沉淀出的研究线索。

### Lead 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | Lead ID |
| `title` | string | 标题 |
| `asset_id` | string/null | 关联资产 ID |
| `primary_wallet_id` | string/null | 主要 Wallet ID |
| `signal_summary` | string | 信号摘要 |
| `why_this_matters` | string/null | 重要性说明 |
| `risk_notes` | string/null | 风险说明 |
| `confidence` | number/null | 置信度 |
| `freshness_timestamp` | string/null | 新鲜度时间 |
| `agent_verdict` | string/null | Agent 判断 |
| `related_signal_event_ids` | string[] | 关联 SignalEvent ID 列表 |
| `related_evidence_ids` | string[] | 关联 Evidence ID 列表 |
| `related_agent_run_ids` | string[] | 关联 AgentRun ID 列表 |
| `created_at` | string | 创建时间 |
| `updated_at` | string | 更新时间 |

### GET `/api/v1/leads`

查询 Lead 列表。

查询参数：

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `limit` | integer | `50` | 返回数量 |
| `offset` | integer | `0` | 偏移量 |
| `asset_id` | string | 无 | 按资产过滤 |
| `primary_wallet_id` | string | 无 | 按主要钱包过滤 |
| `agent_verdict` | string | 无 | 按 Agent 判断过滤 |
| `min_confidence` | number | 无 | 最小置信度，范围 `0` 到 `1` |

响应：`LeadList`

### GET `/api/v1/leads/{lead_id}`

查询 Lead 详情，并展开关联 Evidence 和 AgentRun。不存在时返回 `404`。

响应字段在 `Lead` 基础上额外包含：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `evidence_items` | Evidence[] | 展开的证据列表，不包含 embedding |
| `agent_runs` | AgentRun[] | 展开的 AgentRun 审计记录 |

## Evidence API

Evidence 表示新闻、市场上下文或其他可供检索和分析的证据。API 读取响应不会暴露 embedding。

### Evidence 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | Evidence ID |
| `evidence_type` | string | 证据类型 |
| `title` | string | 标题 |
| `source_url` | string/null | 来源 URL |
| `published_at` | string/null | 发布时间 |
| `fetched_at` | string/null | 抓取时间 |
| `summary` | string/null | 摘要 |
| `evidence_metadata` | object | 元数据 |
| `created_at` | string | 创建时间 |
| `updated_at` | string | 更新时间 |

### GET `/api/v1/evidence`

查询 Evidence 列表。

查询参数：

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `limit` | integer | `50` | 返回数量 |
| `offset` | integer | `0` | 偏移量 |
| `evidence_type` | string | 无 | 按证据类型过滤 |

响应：`EvidenceList`

### GET `/api/v1/evidence/{evidence_id}`

查询 Evidence 详情。不存在时返回 `404`。

响应：`Evidence`

## AgentRun API

AgentRun 表示 LangGraph 或 Agent 工作流的轻量审计记录。

### AgentRun 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | AgentRun ID |
| `workflow_name` | string | 工作流名称 |
| `agent_name` | string/null | Agent 名称 |
| `model` | string/null | 使用的模型 |
| `input_payload` | object | 输入载荷 |
| `output_payload` | object | 输出载荷 |
| `status` | string | 状态 |
| `started_at` | string/null | 开始时间 |
| `finished_at` | string/null | 结束时间 |
| `error_message` | string/null | 错误信息 |
| `token_usage` | object | token 使用情况 |
| `langsmith_project` | string/null | LangSmith 项目 |
| `langsmith_trace_id` | string/null | LangSmith Trace ID |
| `langsmith_run_url` | string/null | LangSmith Run URL |
| `trace_tags` | string[] | Trace 标签 |
| `trace_metadata` | object | Trace 元数据 |
| `created_at` | string | 创建时间 |
| `updated_at` | string | 更新时间 |

### GET `/api/v1/agent-runs`

查询 AgentRun 列表。

查询参数：

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `limit` | integer | `50` | 返回数量 |
| `offset` | integer | `0` | 偏移量 |
| `workflow_name` | string | 无 | 按工作流名称过滤 |
| `agent_name` | string | 无 | 按 Agent 名称过滤 |
| `status` | string | 无 | 按运行状态过滤 |

响应：`AgentRunList`

### GET `/api/v1/agent-runs/{agent_run_id}`

查询 AgentRun 详情。不存在时返回 `404`。

响应：`AgentRun`

## 调试入口

本项目使用 FastAPI，服务启动后通常也可通过以下地址查看自动生成的交互式文档：

- Swagger UI：`http://localhost:8000/docs`
- OpenAPI JSON：`http://localhost:8000/openapi.json`
