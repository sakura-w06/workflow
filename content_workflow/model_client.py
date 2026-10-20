from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI
import httpx

from content_workflow.config import Settings


class ModelCallError(RuntimeError):
    """A sanitized error safe to show to users and store in run history."""


class BailianClient:
    def __init__(self, settings: Settings):
        timeout = httpx.Timeout(
            timeout=settings.timeout,
            connect=settings.connect_timeout,
        )
        self._client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
            timeout=timeout,
            max_retries=settings.max_retries,
        )
        self._model = settings.model

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
            )
        except APITimeoutError as exc:
            raise ModelCallError("百炼 API 请求超时；请检查网络或适当增加 LLM_TIMEOUT。") from exc
        except APIConnectionError as exc:
            raise ModelCallError("无法连接百炼 API；请检查网络和 LLM_BASE_URL。") from exc
        except APIStatusError as exc:
            if exc.status_code == 401:
                message = "百炼 API 认证失败；请检查 LLM_API_KEY。"
            elif exc.status_code == 404:
                message = "百炼 API 未找到指定模型或接口；请检查 LLM_MODEL 和 LLM_BASE_URL。"
            elif exc.status_code == 429:
                message = "百炼 API 请求频率受限；请稍后重试。"
            else:
                message = f"百炼 API 返回 HTTP {exc.status_code} 错误。"
            raise ModelCallError(message) from exc

        if not response.choices or response.choices[0].message.content is None:
            raise ModelCallError("百炼 API 返回了空内容。")
        return response.choices[0].message.content
