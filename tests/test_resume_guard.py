"""hooks/resume_guard.py のテスト。"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "resume_guard", Path(__file__).resolve().parents[1] / "hooks" / "resume_guard.py"
)
assert _SPEC and _SPEC.loader
rg = importlib.util.module_from_spec(_SPEC)
sys.modules["resume_guard"] = rg
_SPEC.loader.exec_module(rg)

NOW = datetime(2026, 9, 23, 12, 0, tzinfo=UTC)
BIG = 150_000
SMALL = 20_000


def _ts(minutes_ago: int) -> str:
    return (NOW - timedelta(minutes=minutes_ago)).isoformat().replace("+00:00", "Z")


def _msg(role: str, block_type: str, text: str) -> dict:
    return {"type": "message", "role": role, "content": [{"type": block_type, "text": text}]}


def _codex_transcript(path: Path, ctx: int, minutes_ago: int) -> Path:
    lines = [
        {"timestamp": _ts(200), "type": "session_meta", "payload": {"cwd": "/tmp"}},
        {
            "timestamp": _ts(199),
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "# AGENTS.md instructions\n..."}],
            },
        },
        {
            "timestamp": _ts(198),
            "type": "response_item",
            "payload": _msg("user", "input_text", "機能Aを実装して"),
        },
        {
            "timestamp": _ts(minutes_ago),
            "type": "response_item",
            "payload": _msg("assistant", "output_text", "半分完了"),
        },
        {
            "timestamp": _ts(minutes_ago),
            "type": "event_msg",
            "payload": {"type": "token_count", "info": {"last_token_usage": {"input_tokens": ctx}}},
        },
    ]
    path.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in lines) + "\n", encoding="utf-8")
    return path


def _claude_transcript(path: Path, ctx: int, minutes_ago: int) -> Path:
    lines = [
        {"type": "user", "timestamp": _ts(199), "message": {"role": "user", "content": "バグを直して"}},
        {
            "type": "assistant",
            "timestamp": _ts(minutes_ago),
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "原因を特定"}],
                "usage": {"input_tokens": 2, "cache_read_input_tokens": ctx - 2, "cache_creation_input_tokens": 0},
            },
        },
        {"type": "assistant", "isSidechain": True, "timestamp": _ts(0), "message": {"usage": {"input_tokens": 5}}},
    ]
    path.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in lines) + "\n", encoding="utf-8")
    return path


# --- read_state ---


def test_read_state_codex(tmp_path: Path) -> None:
    state = rg.read_state(_codex_transcript(tmp_path / "t.jsonl", BIG, 60), 10_000)
    assert state.context_tokens == BIG
    assert state.user_prompts == ["機能Aを実装して"]
    assert state.last_agent_message == "半分完了"
    assert state.last_model_at == NOW - timedelta(minutes=60)


def test_read_state_claude_ignores_sidechain(tmp_path: Path) -> None:
    state = rg.read_state(_claude_transcript(tmp_path / "t.jsonl", BIG, 60), 10_000)
    assert state.context_tokens == BIG
    assert state.user_prompts == ["バグを直して"]
    assert state.last_agent_message == "原因を特定"


def test_read_state_skips_broken_lines(tmp_path: Path) -> None:
    path = _codex_transcript(tmp_path / "t.jsonl", BIG, 60)
    path.write_text("{not json\n[]\n" + path.read_text(encoding="utf-8"), encoding="utf-8")
    assert rg.read_state(path, 10_000).context_tokens == BIG


def test_read_state_tail_only(tmp_path: Path) -> None:
    path = _codex_transcript(tmp_path / "t.jsonl", BIG, 60)
    last_line = path.read_text(encoding="utf-8").splitlines()[-1]
    state = rg.read_state(path, len(last_line) + 2)
    assert state.context_tokens == BIG
    assert state.user_prompts == []


# --- should_intervene ---


@pytest.mark.parametrize(
    ("ctx", "idle", "prompt", "expected"),
    [
        (BIG, 120, "テスト追加して", True),  # 放置でキャッシュ切れ
        (BIG, 1, "続きをお願いします", True),  # 続き系
        (BIG, 1, "/goal 続きをお願いします", True),
        (BIG, 1, "Continue please", True),
        (BIG, 1, "テスト追加して", False),  # 作業中の通常入力
        (SMALL, 600, "続きをお願いします", False),  # 文脈が小さければ放置でも介入しない
    ],
)
def test_should_intervene(ctx: int, idle: int, prompt: str, expected: bool) -> None:
    state = rg.TranscriptState(context_tokens=ctx, last_model_at=NOW - timedelta(minutes=idle))
    assert rg.should_intervene(state, prompt, NOW, 80_000, 30)[0] is expected


def test_should_intervene_without_timestamp() -> None:
    state = rg.TranscriptState(context_tokens=BIG, last_model_at=None)
    assert rg.should_intervene(state, "普通の依頼", NOW, 80_000, 30)[0] is False


# --- main (end to end) ---


def _run(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], payload: dict, agent: str = "codex"):
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    assert rg.main(["--agent", agent]) == 0
    out = capsys.readouterr().out.strip()
    return json.loads(out) if out else None


@pytest.fixture
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    handoff_dir = tmp_path / "handoff"
    monkeypatch.setenv("AGENT_HANDOFF_DIR", str(handoff_dir))
    monkeypatch.delenv("RESUME_GUARD", raising=False)
    return handoff_dir


def test_main_blocks_then_allows_resend(
    env: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    transcript = _codex_transcript(tmp_path / "t.jsonl", BIG, 60 * 24 * 365)
    payload = {"session_id": "abc12345xyz", "transcript_path": str(transcript), "cwd": str(tmp_path), "prompt": "続き"}

    first = _run(monkeypatch, capsys, payload)
    assert first["decision"] == "block"
    assert "/new" in first["reason"]
    handoffs = list(env.glob("*.md"))
    assert len(handoffs) == 1
    body = handoffs[0].read_text(encoding="utf-8")
    assert "機能Aを実装して" in body
    assert "半分完了" in body

    # 同じ内容の再送はユーザーの明示的な続行として素通し
    assert _run(monkeypatch, capsys, payload) is None
    # マーカーは 1 回で消費される
    assert _run(monkeypatch, capsys, payload)["decision"] == "block"


def test_main_claude_suggests_clear(
    env: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    transcript = _claude_transcript(tmp_path / "t.jsonl", BIG, 1)
    payload = {"session_id": "s1", "transcript_path": str(transcript), "cwd": str(tmp_path), "prompt": "続けて"}
    assert "/clear" in _run(monkeypatch, capsys, payload, agent="claude")["reason"]


def test_main_disabled_by_env(
    env: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("RESUME_GUARD", "off")
    transcript = _codex_transcript(tmp_path / "t.jsonl", BIG, 600)
    assert _run(monkeypatch, capsys, {"session_id": "s", "transcript_path": str(transcript), "prompt": "続き"}) is None


def test_main_missing_transcript_passes(
    env: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _run(monkeypatch, capsys, {"session_id": "s", "transcript_path": "/nonexistent", "prompt": "続き"}) is None


def test_main_invalid_json_passes(
    env: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("not json"))
    assert rg.main(["--agent", "codex"]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "入力 JSON" in captured.err


def test_main_small_context_passes(
    env: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    transcript = _codex_transcript(tmp_path / "t.jsonl", SMALL, 600)
    assert _run(monkeypatch, capsys, {"session_id": "s", "transcript_path": str(transcript), "prompt": "続き"}) is None
    assert not env.exists()


def test_add_prompt_merges_partial_duplicate() -> None:
    state = rg.TranscriptState()
    state.add_prompt("続きをお願いします")
    state.add_prompt("続きをお願いします。あとテストも")
    state.add_prompt("別の指示")
    assert state.user_prompts == ["続きをお願いします。あとテストも", "別の指示"]


def test_handoff_includes_blocked_prompt(
    env: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    transcript = _codex_transcript(tmp_path / "t.jsonl", BIG, 600)
    payload = {"session_id": "s", "transcript_path": str(transcript), "prompt": "新しくログイン画面を作って"}
    assert _run(monkeypatch, capsys, payload)["decision"] == "block"
    body = next(env.glob("*.md")).read_text(encoding="utf-8")
    assert "新しくログイン画面を作って" in body


def test_bypass_requires_same_prompt(
    env: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    transcript = _codex_transcript(tmp_path / "t.jsonl", BIG, 600)
    base = {"session_id": "s", "transcript_path": str(transcript)}
    assert _run(monkeypatch, capsys, {**base, "prompt": "続き"})["decision"] == "block"
    # 別の入力では素通しせず、改めてブロックする
    assert _run(monkeypatch, capsys, {**base, "prompt": "別の依頼"})["decision"] == "block"
    # 直前にブロックした入力と同じなら素通し
    assert _run(monkeypatch, capsys, {**base, "prompt": "別の依頼"}) is None


def test_session_id_cannot_escape_handoff_dir(
    env: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    transcript = _codex_transcript(tmp_path / "t.jsonl", BIG, 600)
    payload = {"session_id": "../../evil/x", "transcript_path": str(transcript), "prompt": "続き"}
    assert _run(monkeypatch, capsys, payload)["decision"] == "block"
    written = [p.resolve() for p in tmp_path.rglob("*") if p.is_file() and p.suffix in {".md", ".marker"}]
    assert written
    assert all(env.resolve() in p.parents for p in written)
    assert not (tmp_path.parent / "evil").exists()


def test_handoff_is_private(
    env: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    env.mkdir(mode=0o755)
    env.chmod(0o755)
    transcript = _codex_transcript(tmp_path / "t.jsonl", BIG, 600)
    assert _run(monkeypatch, capsys, {"session_id": "s", "transcript_path": str(transcript), "prompt": "続き"})
    assert env.stat().st_mode & 0o777 == rg.PRIVATE_DIR_MODE
    assert next(env.glob("*.md")).stat().st_mode & 0o777 == rg.PRIVATE_FILE_MODE


def test_handoffs_in_same_second_do_not_overwrite(tmp_path: Path) -> None:
    state = rg.TranscriptState(context_tokens=BIG)
    out = tmp_path / "handoff"
    first = rg.write_handoff(state, {"session_id": "s", "prompt": "画面を作る"}, "codex", out, NOW)
    second = rg.write_handoff(state, {"session_id": "s", "prompt": "テストを書く"}, "codex", out, NOW)
    assert first != second
    assert "画面を作る" in first.read_text(encoding="utf-8")
    assert "テストを書く" in second.read_text(encoding="utf-8")
