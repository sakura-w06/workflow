import json
import re
from typing import Any


def parse_json_object(raw: str, agent_name: str) -> dict[str, Any]:
    text = raw.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1)
    try:
        result = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{agent_name} 输出不是有效 JSON：{exc.msg}（第 {exc.lineno} 行）。") from exc
    if not isinstance(result, dict):
        raise ValueError(f"{agent_name} 输出必须是 JSON 对象。")
    return result


def required_string(value: Any, field_name: str, agent_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{agent_name} 输出缺少有效的 {field_name} 字段。")
    return value.strip()
