import os
from unittest.mock import MagicMock, patch

import pytest
from common.llm_client import (
    LLMResponse,
    _call_anthropic,
    _call_openai,
    chat_completion,
    detect_provider,
)


class TestDetectProvider:
    """detect_provider の正常系・異常系テスト。"""

    @patch.dict(os.environ, {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "key"}, clear=True)
    def test_explicit_openai(self):
        assert detect_provider() == "openai"

    @patch.dict(os.environ, {"LLM_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "key"}, clear=True)
    def test_explicit_anthropic(self):
        assert detect_provider() == "anthropic"

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "key"}, clear=True)
    def test_auto_anthropic(self):
        assert detect_provider() == "anthropic"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "key"}, clear=True)
    def test_auto_openai(self):
        assert detect_provider() == "openai"

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "a", "OPENAI_API_KEY": "o"}, clear=True)
    def test_auto_prefers_anthropic(self):
        """auto モードでは Anthropic が優先される。"""
        assert detect_provider() == "anthropic"

    @patch.dict(os.environ, {}, clear=True)
    def test_no_key_raises(self):
        with pytest.raises(RuntimeError, match="LLM プロバイダーが見つかりません"):
            detect_provider()


class TestChatCompletion:
    """chat_completion のルーティングテスト。"""

    @patch("common.llm_client._call_openai")
    @patch.dict(os.environ, {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "key"})
    def test_routes_to_openai(self, mock_call):
        mock_call.return_value = LLMResponse(content="hello", model="gpt-4o-mini", provider="openai")
        result = chat_completion(messages=[{"role": "user", "content": "hi"}])
        assert result.provider == "openai"
        mock_call.assert_called_once()

    @patch("common.llm_client._call_anthropic")
    @patch.dict(os.environ, {"LLM_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "key"})
    def test_routes_to_anthropic(self, mock_call):
        mock_call.return_value = LLMResponse(content="hello", model="claude-sonnet-4-20250514", provider="anthropic")
        result = chat_completion(messages=[{"role": "user", "content": "hi"}])
        assert result.provider == "anthropic"
        mock_call.assert_called_once()

    @patch("common.llm_client._call_anthropic")
    @patch.dict(os.environ, {"LLM_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "key"})
    def test_explicit_provider_kwarg(self, mock_call):
        mock_call.return_value = LLMResponse(content="hello", model="claude-sonnet-4-20250514", provider="anthropic")
        result = chat_completion(
            messages=[{"role": "user", "content": "hi"}],
            provider="anthropic",
        )
        assert result.provider == "anthropic"


class TestCallOpenAI:
    """_call_openai の単体テスト。"""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "dummy_key"})
    @patch("common.llm_client._OpenAI")
    def test_success(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "テスト回答"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30
        mock_client.chat.completions.create.return_value = mock_response

        result = _call_openai([{"role": "user", "content": "hello"}], "gpt-4o-mini", 0.3, 100)
        assert result.content == "テスト回答"
        assert result.provider == "openai"
        expected_total = 10 + 20
        assert result.usage["total_tokens"] == expected_total

    @patch.dict(os.environ, {}, clear=True)
    def test_no_api_key(self):
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
            _call_openai([{"role": "user", "content": "hi"}], "gpt-4o-mini", 0.3, 100)


class TestCallAnthropic:
    """_call_anthropic の単体テスト。"""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "dummy_key"})
    @patch("common.llm_client._anthropic")
    def test_success(self, mock_anthropic_mod):
        mock_client = MagicMock()
        mock_anthropic_mod.Anthropic.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="テスト回答")]
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 20
        mock_client.messages.create.return_value = mock_response

        result = _call_anthropic(
            [
                {"role": "system", "content": "あなたはアシスタントです"},
                {"role": "user", "content": "hello"},
            ],
            "claude-sonnet-4-20250514",
            0.3,
            100,
        )
        assert result.content == "テスト回答"
        assert result.provider == "anthropic"
        expected_total = 10 + 20
        assert result.usage["total_tokens"] == expected_total

        # system prompt が kwargs に含まれていることを確認
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["system"] == "あなたはアシスタントです"
        assert len(call_kwargs["messages"]) == 1

    @patch.dict(os.environ, {}, clear=True)
    def test_no_api_key(self):
        with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
            _call_anthropic([{"role": "user", "content": "hi"}], "claude-sonnet-4-20250514", 0.3, 100)
