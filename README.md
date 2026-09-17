# SA Multi-Agent Demo

这是一个面向云解决方案架构师SA的多 Agent 演示项目。

项目模拟从客户需求识别、产品能力检索、候选方案生成、方案验证，到会议纪要更新和重新计算的完整流程。其重点不是让大模型自由聊天，而是让多个职责明确的 Agent 围绕同一个结构化 State 协作，并通过版本号、依赖关系和 stale 状态控制下游结果是否需要重新计算。

## 一、项目实现了什么

当前 Demo 包含以下主要能力：

- 从客户描述中提取事实、需求、约束、偏好、未知项和假设。
- 根据客户需求从本地产品知识库中检索相关产品能力。
- 使用检索到的产品证据生成候选解决方案。
- 检查方案是否存在无证据结论、错误匹配或将未知信息当成已确认信息等问题。
- 由 Supervisor 根据验证结果决定下一步流程。
- 从会议纪要中提取新事实、决策、行动项和待确认问题。
- 根据新的会议信息增量更新 Customer State。
- 当上游信息发生变化时，将下游结果标记为 stale，并按正确顺序重新计算。
- 分析外部公开材料，提取潜在线索、机会、风险和待确认问题。
- 通过 Harness 和 Tools 目录实验更标准化的 Agent—Tool 调用方式。

## 二、7 个正式 Agent

本项目共有 7 个正式 Agent。

### 1. Requirement Identification Agent

负责把客户原始描述转换为结构化 Customer State，包括：

- facts
- requirements
- constraints
- preferences
- unknowns
- assumptions

重点：不把客户的兴趣直接当成正式需求，也不仅凭技术常识替客户创造需求。

### 2. Product Search Agent

根据 Customer State，从 `products.json` 中检索相关产品能力。

只负责“找产品证据”，不负责设计架构，也不能使用产品知识库之外的能力。

### 3. Solution Matching Agent

根据客户状态和 Product Search 结果生成候选解决方案。

候选方案会区分：

- 已匹配需求
- 部分匹配
- 未解决问题
- 必要假设
- 方案理由

只能使用 Product Search 已经返回的产品及能力。

### 4. Verification Agent

负责审核候选方案，而不是重新设计方案。

主要检查：

- unsupported claim
- evidence mismatch
- unknown treated as confirmed
- unsupported assumption
- missing requirement
- preference treated as mandatory

Verification 的结果会告诉 Supervisor 是否需要整改，以及问题应该由哪个阶段处理。

### 5. Supervisor Agent

根据 Verification 结果决定下一步执行哪个 Agent，例如：

- Requirement Identification Agent
- Product Search Agent
- Solution Matching Agent
- END

Supervisor 只负责路由，不负责重新分析客户需求或设计方案。

### 6. Meeting Record Agent

负责把非结构化会议纪要整理为：

- facts
- decisions
- action items
- open questions
- customer statements

不会把客户兴趣自动转换成方案决策。

### 7. Research Agent

负责分析外部公开材料并提取：

- findings
- opportunities
- risks
- questions

公开信息不等同于客户确认信息。因此 Research Agent 的结果不会被自动当成正式 Customer State。

## 三、两个辅助模式

以下两个函数不是新的正式 Agent，而是已有 Agent 的特殊工作模式。

### Requirement Update

位于 `agents/requirement.py`。
根据 Meeting Record 增量更新已有 Customer State，保留有效历史信息，并记录可能出现的冲突。

### Solution Correction

位于 `agents/solution.py`。
当 Verification 发现候选方案存在问题时，根据验证意见修改原方案。


## 四、目录结构

```text
SA_multi_agent_demo/
│
├── agents/                 # 7 个正式 Agent 及两个辅助模式
├── harness/                # Agent 执行与工具调用实验层
├── tools/                  # 可被 Harness 或 Agent 调用的工具
├── utils/                  # 通用辅助功能，例如终端输出
├── workflow/               # State、Trigger 和主流程编排
│
├── config.py               # 环境变量和模型配置
├── llm.py                  # GLM API 调用和 JSON 解析
├── main.py                 # 程序启动入口与兼容接口
├── product_loader.py       # 加载产品知识库
├── test_harness.py         # Harness 与 Tool 调用测试入口
├── .env.example            # 环境变量示例
├── .gitignore
└── README.md
```

## 五、各目录职责

### `agents/`

保存 7 个正式 Agent 的 Prompt 和调用函数。

```text
agents/
├── requirement.py
├── product_search.py
├── solution.py
├── verification.py
├── supervisor.py
├── meeting.py
└── research.py
```

这个目录负责“每个 Agent 应该做什么，以及应该遵守什么边界”。

### `workflow/`

负责控制 Agent 按什么顺序运行。

```text
workflow/
├── state.py
├── trigger.py
└── runner.py
```

- `state.py`：创建 State、记录版本号、标记下游结果失效。
- `trigger.py`：判断应该从哪个 Agent 重新开始，并执行 stale 重算循环。
- `runner.py`：串联整个端到端流程。


### `harness/`

用于实验或验证更标准化的执行方式，例如：

- 统一组织 Agent 运行上下文。
- 管理 Agent 可以使用的工具。
- 让 Agent 调用普通 Python 工具，而不是把所有逻辑写进 Prompt。
- 为后续增加日志、权限、重试和执行追踪提供扩展位置。

当前主业务流程仍以 `workflow/runner.py` 为核心；Harness 属于独立的工程化实验部分。

### `tools/`

存放可以被 Harness 或 Agent 调用的普通工具。

例如读取产品知识、查询数据或进行格式处理，更适合做成 Tool，而不是再创造一个 Agent。

### `utils/`

保存多个模块都可能使用的小型通用功能。

当前主要是：

```text
utils/output.py
```

负责打印 Requirement、Product Search、Solution、Verification 和 Workflow State 的终端摘要。

## 六、根目录文件

### `main.py`

负责：

- 导入 `workflow.runner.run_workflow`
- 保留部分旧函数名的兼容导出
- 在直接运行时启动完整工作流

### `config.py`

读取 `.env` 中的配置，包括：

- `GLM_API_KEY`
- API 地址
- 模型名称
- 请求超时时间
- Debug 开关

默认使用 Huawei ModelArts MaaS Chat Completions 接口。

### `llm.py`

负责：

- 向 GLM API 发送请求。
- 组装标准消息格式。
- 获取模型返回内容。
- 去掉可能存在的 Markdown JSON 代码块。
- 将文本解析为 Python 字典或列表。

是所有 Agent 共用的模型调用层。

### `product_loader.py`

负责读取根目录下的 `products.json`。

使用独立 loader 后，即使从其他工作目录启动程序，也可以根据项目路径正确找到产品知识库。

### `test_harness.py`

用于独立验证 Harness 和 Tools 的调用关系，是Harness实验层的测试程序。

## 七、Workflow State

系统使用一个共享 State 保存各阶段结果：

```text
customer_input
customer_state
meeting_record
research_findings
product_matches
candidate_solutions
verification
supervisor_decision
dependencies
versions
stale
```

### Versions

以下核心结果都有独立版本号：

```text
customer_state
product_matches
candidate_solutions
verification
```

例如：

```text
Customer State v2
Product Matches v2
Candidate Solutions v2
Verification v2
```

### Dependencies

系统同时记录每个结果基于哪些上游版本生成。

例如：

```text
Candidate Solutions v2
  based on Customer State v2
  based on Product Matches v2
```

这样可以判断一个结果虽然存在，但是否仍然基于最新数据。

### Stale

当上游数据变化时，下游结果不会被直接删除，而是标记为 stale。

例如 Customer State 从 v1 更新为 v2：

```text
Customer State v2
↓
Product Matches v1       STALE
↓
Candidate Solutions v1   STALE
↓
Verification v1          STALE
```

Trigger 会从最上游的 stale 节点开始重新计算：

```text
Product Search
→ Solution Matching
→ Verification
→ END
```

这避免了无意义地重新运行全部流程，也防止新旧版本的数据混用。

## 八、完整执行流程

```text
客户原始描述
    ↓
Requirement Identification Agent
    ↓
Customer State v1
    ↓
Product Search Agent
    ↓
Product Matches v1
    ↓
Solution Matching Agent
    ↓
Candidate Solutions v1
    ↓
Verification Agent
    ↓
Supervisor Agent
    ↓
Meeting Record Agent
    ↓
Requirement Update
    ↓
Customer State v2
    ↓
Stale Recalculation
    ├─ Product Search v2
    ├─ Solution Matching v2
    └─ Verification v2
    ↓
Research Agent
    ↓
最终 Workflow State
```

如果 Verification 要求整改，Supervisor 也可以将流程路由回 Solution Matching 的 correction mode，再次验证修改后的方案。

## 九、安装与运行

### 1. 创建虚拟环境

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. 安装依赖

```powershell
pip install -r requirements.txt
```

### 3. 配置环境变量

复制环境变量示例：

```powershell
Copy-Item .env.example .env
```

然后在 `.env` 中配置：

```env
GLM_API_KEY=your-api-key
```

不要将真实 `.env` 或 API Key 提交到 Git。

### 4. 运行完整 Demo

```powershell
python main.py
```

### 5. 测试 Harness

```powershell
python test_harness.py
```

## 十、代码修改建议

如果以后要修改不同类型的内容，可以按下面的位置寻找：

```text
修改某个 Agent 的职责或 Prompt
→ agents/

修改 Agent 执行顺序
→ workflow/runner.py

修改版本和 stale 传播规则
→ workflow/state.py
→ workflow/trigger.py

修改产品知识
→ products.json

修改 API、模型或 Debug 配置
→ config.py
→ .env

修改终端输出
→ utils/output.py

修改 Agent 调用工具的实验逻辑
→ harness/
→ tools/
```

## 十一、当前项目边界

这是一个本地 Demo，不是完整生产系统。

当前主要用于验证：

- 多 Agent 职责拆分。
- Prompt 边界设计。
- 结构化 State。
- 产品证据约束。
- Verification 与 Supervisor 路由。
- 上游变化后的版本化重算。
- Agent 与 Tool 的基本分层。

当前没有完整实现：

- 多用户与权限隔离。
- 数据库持久化。
- 任务队列和并发执行。
- 完整运行日志与 Token 成本统计。
- 自动化 Web Search。
- 生产级错误恢复。
- 完整的 Agent 自主 Tool Calling 循环。

因此更适合作为多 Agent 流程和工程结构的学习、演示与实验项目。
