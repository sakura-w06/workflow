from pathlib import Path
from typing import Any

from content_workflow.agents.common import parse_json_object, required_string
from content_workflow.state import WorkflowInput


SYSTEM_PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "writer.txt").read_text(
    encoding="utf-8"
)


class WriterAgent:
    def __init__(self, client: Any):
        self.client = client

    def run(
        self,
        request: WorkflowInput,
        outline: dict[str, Any],
        revision_instructions: list[str] | None = None,
    ) -> dict[str, Any]:
        user_prompt = (
            f"创作要求：\n"
            f"- 主题：{request.topic}\n"
            f"- 目标读者：{request.audience}\n"
            f"- 内容类型：{request.content_type}\n"
            f"- 期望长度：{request.target_length}\n"
            f"- 语气：{request.tone}\n\n"
            f"规划 Agent 的大纲：\n{outline}\n\n"
            f"审校意见（首稿时为空）：\n{revision_instructions or []}"
        )
        result = parse_json_object(self.client.complete(SYSTEM_PROMPT, user_prompt), "写作 Agent")
        return {
            "title": required_string(result.get("title"), "title", "写作 Agent"),
            "content": required_string(result.get("content"), "content", "写作 Agent"),
            "change_summary": str(result.get("change_summary", "")).strip(),
        }
