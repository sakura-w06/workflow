from pathlib import Path
from typing import Any

from content_workflow.agents.common import parse_json_object, required_string
from content_workflow.state import WorkflowInput


SYSTEM_PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "planner.txt").read_text(
    encoding="utf-8"
)


class PlannerAgent:
    def __init__(self, client: Any):
        self.client = client

    def run(self, request: WorkflowInput) -> dict[str, Any]:
        user_prompt = (
            f"主题：{request.topic}\n"
            f"目标读者：{request.audience}\n"
            f"内容类型：{request.content_type}\n"
            f"期望长度：{request.target_length}\n"
            f"语气：{request.tone}"
        )
        result = parse_json_object(self.client.complete(SYSTEM_PROMPT, user_prompt), "规划 Agent")
        result["title"] = required_string(result.get("title"), "title", "规划 Agent")
        result["core_message"] = required_string(
            result.get("core_message"), "core_message", "规划 Agent"
        )
        sections = result.get("sections")
        if not isinstance(sections, list) or not sections:
            raise ValueError("规划 Agent 输出缺少非空的 sections 列表。")
        for index, section in enumerate(sections, start=1):
            if not isinstance(section, dict):
                raise ValueError(f"规划 Agent 的第 {index} 个章节必须是 JSON 对象。")
            section["heading"] = required_string(
                section.get("heading"), f"sections[{index}].heading", "规划 Agent"
            )
            section["key_points"] = required_string(
                section.get("key_points"), f"sections[{index}].key_points", "规划 Agent"
            )
        return result
