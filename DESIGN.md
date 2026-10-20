# 设计说明

## 流程

```text
主题和写作要求
      |
      v
规划 Agent -- 输出标题建议、核心观点、大纲和事实核查提示
      |
      v
写作 Agent -- 输出完整初稿
      |
      v
审校 Agent -- 输出 verdict、问题、修改指示和摘要
      |
      +-- approved ------> 完成并保存最终稿
      |
      +-- needs_revision -> 写作 Agent 按意见修改一次
                                 |
                                 v
                            审校 Agent 复核
                              |         |
                         approved   needs_revision
                              |         |
                            完成    停止并标记遗留意见
```

## 组件职责

- `BailianClient`：使用 OpenAI Python SDK 访问百炼 OpenAI 兼容 Chat Completions API。连接超时默认 10 秒，读取/请求超时默认 120 秒，可重试错误最多重试一次。错误转换为不包含 API Key 或原始请求头的安全提示。
- `PlannerAgent`、`WriterAgent`、`ReviewerAgent`：各自持有独立提示词，验证模型输出的数据结构，并只执行本 Agent 的职责。
- `ContentWorkflow`：按顺序调用 Agent，将上一阶段结果写入共享 `WorkflowState`，并控制最多一次返工。
- `StateStore`：每个步骤开始及完成后原子写入 JSON，确保中途失败时仍有可诊断记录。
- `data/runs/`：保存运行状态，目录内容由 Git 忽略。

## 状态和终态

状态包含运行 ID、用户输入、当前步骤、每步状态和输出、大纲、稿件、审校结果、返工次数、最终稿及错误信息。终态为：

- `completed`：审校通过（可能是首审，也可能是返工后复核）。
- `completed_with_unresolved_issues`：一次返工后仍未通过；保留修改稿和审校意见，不伪装成成功。
- `failed`：Agent 调用失败或输出不符合约定格式；记录失败步骤并停止。

Agent 间通过 Workflow 共享状态传递数据，不由 Agent 直接相互调用。模型结构化输出采用 JSON 提示并在应用侧验证；格式错误会显式失败，不会用空内容作为成功结果。

## 凭据

真实配置仅放在本机 `.env`。仓库只包含不带密钥的 `.env.example`。代码不输出 API Key；日志和状态文件保存经过清理的错误信息，不保存 API 请求头。

## MVP 边界

- 顺序执行三个 Agent，审校分支最多触发一轮返工。
- 暂不含 Web 界面、并行执行、数据库或多用户管理。
- 写作模型生成内容不等同于事实核查；对重要事实仍需人工核验。
