# 仓库开发规则

本文件适用于整个仓库。AI 开发代理在修改本仓库代码时，除非子目录存在更具体的规则文件，否则默认遵守以下规范。

## Python 中文注释规范

### 注释原则

精简为主，仅在关键位置添加中文注释。

### 必须注释

- 复杂业务流程的步骤标注。
- 公开 API（导出函数/类）的 docstring。
- 非显而易见的业务规则。
- 临时方案或技术债务（`# TODO:`、`# FIXME:`）。

### 禁止注释

- 禁止给显而易见的代码添加注释，例如 `i += 1  # i 加 1`。
- 禁止重复描述代码本身。
- 禁止每行都加注释。
- 禁止提交注释掉的旧代码；无用代码应直接删除。

### 业务流程注释格式

复杂业务使用步骤编号标注关键节点：

```python
async def execute_trading_cycle(self, agent: Agent) -> None:
    """执行交易周期"""

    # 1. 加载并验证 Agent 归属
    agent = await self._load_and_validate_agent()
    if agent is None:
        return

    # 2. 初始化交易所连接
    await self._ensure_exchange(agent)

    # 3. 执行 LangGraph 决策流程
    decision = await self._run_langgraph_decision(agent)

    # 4. 执行订单
    await self._execute_order(agent, decision)
```

### 函数/类 Docstring 格式

导出的函数和类使用简洁的中文 docstring：

```python
class ExchangeFactory:
    """Exchange 抽象工厂，根据类型创建对应的交易所实例"""

    @staticmethod
    def create(exchange_type: ExchangeType, **kwargs) -> BaseExchange:
        """创建 Exchange 实例

        Args:
            exchange_type: 交易所类型（HYPERLIQUID/SIMULATION）
            **kwargs: 传递给具体实现的参数

        Returns:
            BaseExchange 实例

        Raises:
            ValueError: 未知的交易所类型
        """
        pass
```

### 行内注释格式

行内注释仅用于解释非显而易见的逻辑：

```python
# 好的示例
max_trade_usd = Decimal("1000")
tolerance = max_trade_usd * Decimal("0.01")  # 允许 1% 误差，避免浮点精度问题

# 坏的示例（禁止）
i = 0  # 初始化 i 为 0
```

### TODO/FIXME 格式

标记技术债务或待办事项：

```python
# TODO: 迁移到 gRPC 后删除此方法
async def legacy_deduct_credits(self):
    pass

# FIXME: 并发场景下可能有竞态条件，需要加分布式锁
async def update_balance(self):
    pass
```

### 禁止的注释模式

```python
# 禁止：注释掉的代码（直接删除）
# old_value = calculate_old_way()

# 禁止：显而易见的注释
def get_user(user_id: int):
    """获取用户"""
    return db.get(user_id)

# 禁止：每行都加注释
def process():
    a = 1  # 设置 a 为 1
    b = 2  # 设置 b 为 2
    return a + b  # 返回 a + b
```
