"""マルチプロバイダー対応 LLM クライアント。

環境変数 LLM_PROVIDER で利用するプロバイダーを切り替える:
  - "openai"    : OpenAI API を使用
  - "anthropic" : Anthropic API (Claude) を使用
  - "auto"      : ANTHROPIC_API_KEY があれば Anthropic、なければ OpenAI(デフォルト)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    pass

try:
    from openai import OpenAI as _OpenAI
except ImportError:
    _OpenAI = None  # type: ignore[assignment,misc]

try:
    import anthropic as _anthropic
except ImportError:
    _anthropic = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

Provider = Literal["openai", "anthropic"]

# プロバイダーごとのデフォルトモデル
DEFAULT_MODELS: dict[Provider, str] = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-sonnet-4-20250514",
}


@dataclass
class LLMResponse:
    """LLM レスポンスの共通データクラス。"""

    content: str
    model: str
    provider: Provider
    usage: dict[str, int] = field(default_factory=dict)


def detect_provider() -> Provider:
    """環境変数から利用可能なプロバイダーを自動検出する。"""
    provider_env = os.getenv("LLM_PROVIDER", "auto").lower()

    if provider_env == "openai":
        return "openai"
    if provider_env == "anthropic":
        return "anthropic"

    # auto: キーの有無で判定(Anthropic 優先)
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"

    raise RuntimeError("LLM プロバイダーが見つかりません。OPENAI_API_KEY または ANTHROPIC_API_KEY を設定してください。")


def chat_completion(
    messages: list[dict[str, str]],
    *,
    model: str | None = None,
    provider: Provider | None = None,
    temperature: float = 0.3,
    max_tokens: int = 1500,
) -> LLMResponse:
    """プロバイダー非依存のチャット補完を実行する。

    Args:
        messages: OpenAI 形式の messages リスト
                  [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        model: 使用するモデル名。None の場合はプロバイダーのデフォルトを使用
        provider: 明示的にプロバイダーを指定。None の場合は auto-detect
        temperature: 生成の温度パラメータ
        max_tokens: 最大トークン数

    Returns:
        LLMResponse: 共通レスポンスオブジェクト
    """
    resolved_provider = provider or detect_provider()
    resolved_model = model or DEFAULT_MODELS[resolved_provider]

    logger.info(f"LLM呼び出し: provider={resolved_provider}, model={resolved_model}")

    if resolved_provider == "openai":
        return _call_openai(messages, resolved_model, temperature, max_tokens)
    return _call_anthropic(messages, resolved_model, temperature, max_tokens)


def _call_openai(
    messages: list[dict[str, str]],
    model: str,
    temperature: float,
    max_tokens: int,
) -> LLMResponse:
    """OpenAI API を呼び出す。"""
    if _OpenAI is None:
        raise RuntimeError(
            "openai パッケージがインストールされていません。`uv add openai` でインストールしてください。"
        )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("環境変数 'OPENAI_API_KEY' が設定されていません。")

    client = _OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    usage = {}
    if response.usage:
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }

    return LLMResponse(
        content=response.choices[0].message.content,
        model=model,
        provider="openai",
        usage=usage,
    )


def _call_anthropic(
    messages: list[dict[str, str]],
    model: str,
    temperature: float,
    max_tokens: int,
) -> LLMResponse:
    """Anthropic API (Claude) を呼び出す。"""
    if _anthropic is None:
        raise RuntimeError(
            "anthropic パッケージがインストールされていません。`uv add anthropic` でインストールしてください。"
        )

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("環境変数 'ANTHROPIC_API_KEY' が設定されていません。")

    client = _anthropic.Anthropic(api_key=api_key)

    # OpenAI 形式の messages を Anthropic 形式に変換
    system_prompt = ""
    anthropic_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system_prompt = msg["content"]
        else:
            anthropic_messages.append({"role": msg["role"], "content": msg["content"]})

    kwargs: dict = {
        "model": model,
        "messages": anthropic_messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if system_prompt:
        kwargs["system"] = system_prompt

    response = client.messages.create(**kwargs)

    usage = {}
    if response.usage:
        usage = {
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        }

    return LLMResponse(
        content=response.content[0].text,
        model=model,
        provider="anthropic",
        usage=usage,
    )
