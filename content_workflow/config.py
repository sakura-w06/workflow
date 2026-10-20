from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str
    base_url: str
    connect_timeout: float
    timeout: float
    max_retries: int


def load_settings() -> Settings:
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    api_key = os.getenv("LLM_API_KEY", "").strip()
    model = os.getenv("LLM_MODEL", "").strip()
    if not api_key:
        raise ValueError("未配置 LLM_API_KEY。请复制 .env.example 为 .env 并填写百炼 API Key。")
    if not model:
        raise ValueError("未配置 LLM_MODEL。请在 .env 中填写百炼支持的模型名称。")

    try:
        connect_timeout = float(os.getenv("LLM_CONNECT_TIMEOUT", "10"))
        timeout = float(os.getenv("LLM_TIMEOUT", "120"))
        max_retries = int(os.getenv("LLM_MAX_RETRIES", "1"))
    except ValueError as exc:
        raise ValueError("LLM_CONNECT_TIMEOUT、LLM_TIMEOUT 和 LLM_MAX_RETRIES 必须是有效数字。") from exc

    if connect_timeout <= 0 or timeout <= 0:
        raise ValueError("连接和响应超时必须大于 0 秒。")
    if max_retries < 0 or max_retries > 1:
        raise ValueError("LLM_MAX_RETRIES 只能设置为 0 或 1。")

    return Settings(
        api_key=api_key,
        model=model,
        base_url=os.getenv(
            "LLM_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        ).strip(),
        connect_timeout=connect_timeout,
        timeout=timeout,
        max_retries=max_retries,
    )
