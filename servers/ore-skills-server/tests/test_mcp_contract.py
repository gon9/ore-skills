from __future__ import annotations

import asyncio
import importlib

import pytest
from mcp.server.fastmcp import FastMCP
from ore_skills_server import main as run_server
from ore_skills_server.main import mcp

server_module = importlib.import_module("ore_skills_server.main")


def test_server_exposes_expected_tools() -> None:
    tools = asyncio.run(mcp.list_tools())

    assert isinstance(mcp, FastMCP)
    assert {tool.name for tool in tools} == {"check_spec", "get_transcript"}
    assert all(tool.inputSchema.get("required") for tool in tools)


def test_check_spec_returns_success_message(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(server_module, "check_spec_file", lambda _content: [])

    content, structured = asyncio.run(mcp.call_tool("check_spec", {"content": "# valid"}))

    assert content[0].text == "問題は見つかりませんでした。"
    assert structured == {"result": "問題は見つかりませんでした。"}


def test_check_spec_formats_findings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        server_module,
        "check_spec_file",
        lambda _content: ["概要がありません", "要件がありません"],
    )

    content, structured = asyncio.run(mcp.call_tool("check_spec", {"content": "invalid"}))

    expected = "以下の問題が見つかりました:\n- 概要がありません\n- 要件がありません"
    assert content[0].text == expected
    assert structured == {"result": expected}


def test_get_transcript_delegates_to_media(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(server_module, "get_youtube_transcript", lambda video_id: f"transcript:{video_id}")

    content, structured = asyncio.run(mcp.call_tool("get_transcript", {"video_id": "abc123"}))

    assert content[0].text == "transcript:abc123"
    assert structured == {"result": "transcript:abc123"}


def test_public_entrypoint_is_exported() -> None:
    assert callable(run_server)
