# 内容创作 Workflow

一个使用阿里云百炼 OpenAI 兼容 API 的命令行 MVP。工作流由规划 Agent、写作 Agent、审校 Agent 按顺序协作；若首次审校要求修改，写作 Agent 修改一次后由审校 Agent 复核，不会无限循环。

## 环境要求

- Python 3.11 或更高版本
- 阿里云百炼 API Key，以及账号可调用的模型名称

## 配置

首次配置时，仅在项目根目录还没有 `.env` 文件的情况下运行：

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

如果 `.env` 已存在，请不要再次复制模板，以免覆盖已有配置。编辑 `.env`，至少填写：

```dotenv
LLM_API_KEY=你的百炼API密钥
LLM_MODEL=你的百炼模型名称
```

默认使用百炼北京地域的 OpenAI 兼容地址：
`https://dashscope.aliyuncs.com/compatible-mode/v1`。如使用其他地域或兼容服务地址，可设置 `LLM_BASE_URL`。请按百炼控制台提供的模型名称和服务地域配置。

默认连接超时为 10 秒、响应超时为 120 秒；对可重试的临时 API 错误最多重试一次。可通过 `LLM_CONNECT_TIMEOUT`、`LLM_TIMEOUT`、`LLM_MAX_RETRIES` 调整。

## 安装和运行

在 VS Code 中打开项目文件夹，然后按 `Ctrl + \`` 打开集成终端。确认终端当前目录是项目根目录；以下命令适用于 PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m content_workflow "如何开始低碳生活" --audience "普通读者" --content-type "科普文章" --length "约 800 字" --tone "清晰易懂"
```

如果终端提示“无法将 `python` 识别为命令”，说明 Python 没有加入当前终端的 `PATH`。在 VS Code 按 `Ctrl + Shift + P`，选择 **Python: Select Interpreter**，确认已安装并选中 Python，然后可在命令中使用所选解释器的完整路径。也可以按本机实际安装位置设置路径，例如：

```powershell
$python = 'C:\Path\To\Python\python.exe'
Test-Path $python
& $python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m content_workflow "如何开始低碳生活"
```

将示例中的 `C:\Path\To\Python\python.exe` 替换为实际路径；`Test-Path` 返回 `True` 才表示路径有效。若当前项目已有 `.venv`，无需重复创建虚拟环境。

也可以省略可选参数：

```powershell
.\.venv\Scripts\python.exe -m content_workflow "如何开始低碳生活"
```

终端展示最终稿和运行记录位置。每次运行的输入、Agent 输出、状态、审校意见及错误（如有）保存在 `data/runs/<运行ID>.json`。
