from pathlib import Path
from typing import Any

from content_workflow.agents.common import parse_json_object, required_string
from content_workflow.state import WorkflowInput


SYSTEM_PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "reviewer.txt").read_text(
    encoding="utf-8"
)


class ReviewerAgent:
    def __init__(self, client: Any):
        self.client = client

    def run(
        self,
        request: WorkflowInput,
        outline: dict[str, Any],
        draft: dict[str, Any],
    ) -> dict[str, Any]:
        user_prompt = (
            f"主题和写作要求：\n"
            f"- 主题：{request.topic}\n"
            f"- 目标读者：{request.audience}\n"
            f"- 内容类型：{request.content_type}\n"
            f"- 期望长度：{request.target_length}\n"
            f"- 语气：{request.tone}\n\n"
            f"规划 Agent 的大纲：\n{outline}\n\n"
            f"待审校稿件：\n标题：{draft['title']}\n正文：\n{draft['content']}"
        )
        result = parse_json_object(self.client.complete(SYSTEM_PROMPT, user_prompt), "审校 Agent")
        verdict = required_string(result.get("verdict"), "verdict", "审校 Agent").lower()
        if verdict not in {"approved", "needs_revision"}:
            raise ValueError("审校 Agent 的 verdict 必须为 approved 或 needs_revision。")
        issues = result.get("issues")
        instructions = result.get("revision_instructions")
        if not isinstance(issues, list) or not all(isinstance(item, str) for item in issues):
            raise ValueError("审校 Agent 的 issues 必须是字符串列表。")
        if not isinstance(instructions, list) or not all(
            isinstance(item, str) for item in instructions
        ):
            raise ValueError("审校 Agent 的 revision_instructions 必须是字符串列表。")
        return {
            "verdict": verdict,
            "issues": issues,
            "revision_instructions": instructions,
            "summary": required_string(result.get("summary"), "summary", "审校 Agent"),
        }
