#!/usr/bin/env python3
"""長いスレッドの「続き」再開を止め、ハンドオフ経由の新スレッドへ誘導する UserPromptSubmit フック。

Codex CLI と Claude Code の両方で使う。標準ライブラリだけで動く。

背景:
    巨大な文脈を持つスレッドを再開すると、1 リクエストごとに文脈全体を送り直すため
    rate limit を数分で使い切る。時間が空くとキャッシュも切れて最初の 1 回がさらに重い。

動作:
    1. transcript の末尾から「直近の文脈サイズ」と「最後にモデルが応答した時刻」を読む
    2. 文脈が閾値以上 かつ (放置時間が閾値以上 または 入力が「続き」系) なら介入する
    3. 介入時は transcript から機械的にハンドオフ Markdown を書き出し、プロンプトをブロックする
       (モデルを 1 回も呼ばないので、ブロック自体は rate limit を消費しない)
    4. 同じセッションで直後にもう一度送信された場合は素通しする(ユーザーの明示的な続行)

環境変数(すべて任意):
    RESUME_GUARD=off                 フックを無効化
    RESUME_GUARD_CTX_TOKENS          介入する文脈サイズの閾値(既定 80000)
    RESUME_GUARD_IDLE_MINUTES        キャッシュ切れとみなす放置時間(既定 30)
    RESUME_GUARD_BYPASS_MINUTES      ブロック後に再送で素通しする猶予(既定 10)
    RESUME_GUARD_TAIL_BYTES          transcript 末尾から読むバイト数(既定 4000000)
    AGENT_HANDOFF_DIR                ハンドオフの保存先(既定 ~/.local/state/agent-handoff)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_CTX_TOKENS = 80_000
DEFAULT_IDLE_MINUTES = 30
DEFAULT_BYPASS_MINUTES = 10
DEFAULT_TAIL_BYTES = 4_000_000
RECENT_PROMPTS = 5
SNIPPET_CHARS = 1500
PRIVATE_DIR_MODE = 0o700
PRIVATE_FILE_MODE = 0o600
MAX_NAME_ATTEMPTS = 100

CONTINUE_PATTERN = re.compile(
    r"^\s*(/goal\b.*|続き|つづき|続けて|続行|再開|continue|resume|go on|keep going)",
    re.IGNORECASE,
)
# モデル向けに自動注入されるメッセージ(ユーザー入力ではない)
INJECTED_PREFIXES = ("<", "# AGENTS.md", "Caveat:")


@dataclass
class TranscriptState:
    """transcript 末尾から抽出した状態。"""

    context_tokens: int = 0
    last_model_at: datetime | None = None
    user_prompts: list[str] = field(default_factory=list)
    last_agent_message: str = ""
    last_plan: str = ""

    def add_prompt(self, text: str) -> None:
        """ユーザー指示を追加する。途中保存された同じ指示(前方一致)は置き換える。"""
        if self.user_prompts and text.startswith(self.user_prompts[-1]):
            self.user_prompts[-1] = text
        else:
            self.user_prompts.append(text)


def _env_int(name: str, default: int) -> int:
    """整数の環境変数を読む。不正値は既定値に戻す。"""
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


def _parse_ts(value: str | None) -> datetime | None:
    """ISO8601 文字列を aware datetime に変換する。"""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _read_tail_lines(path: Path, tail_bytes: int) -> list[str]:
    """ファイル末尾 tail_bytes だけを行単位で読む(先頭の途切れ行は捨てる)。"""
    size = path.stat().st_size
    with path.open("rb") as f:
        if size > tail_bytes:
            f.seek(size - tail_bytes)
            f.readline()
        data = f.read()
    return data.decode("utf-8", errors="replace").splitlines()


def _is_real_prompt(text: str) -> bool:
    """自動注入ではない、ユーザーが実際に打った入力かを判定する。"""
    stripped = text.strip()
    return bool(stripped) and not stripped.startswith(INJECTED_PREFIXES)


def _text_blocks(content: object, block_types: tuple[str, ...]) -> str:
    """message.content(文字列 or ブロック配列)からテキストを連結する。"""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") in block_types]
    return "\n".join(p for p in parts if p)


def _apply_codex(entry: dict, state: TranscriptState) -> None:
    """Codex rollout の 1 行を状態に反映する。"""
    payload = entry.get("payload") or {}
    kind = payload.get("type")
    if kind == "token_count" and payload.get("info"):
        state.context_tokens = payload["info"]["last_token_usage"]["input_tokens"]
        state.last_model_at = _parse_ts(entry.get("timestamp")) or state.last_model_at
    elif kind == "message":
        if payload.get("role") == "user":
            text = _text_blocks(payload.get("content"), ("input_text",))
            if _is_real_prompt(text):
                state.add_prompt(text)
        elif payload.get("role") == "assistant":
            text = _text_blocks(payload.get("content"), ("output_text",))
            if text.strip():
                state.last_agent_message = text
    elif kind == "function_call" and payload.get("name") == "update_plan":
        state.last_plan = payload.get("arguments", "")


def _apply_claude(entry: dict, state: TranscriptState) -> None:
    """Claude Code transcript の 1 行を状態に反映する。"""
    if entry.get("isSidechain"):
        return
    message = entry.get("message") or {}
    if entry.get("type") == "assistant":
        usage = message.get("usage") or {}
        total = sum(usage.get(k, 0) for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
        if total:
            state.context_tokens = total
            state.last_model_at = _parse_ts(entry.get("timestamp")) or state.last_model_at
        text = _text_blocks(message.get("content"), ("text",))
        if text.strip():
            state.last_agent_message = text
    elif entry.get("type") == "user" and not entry.get("isMeta"):
        text = _text_blocks(message.get("content"), ("text",))
        if _is_real_prompt(text):
            state.add_prompt(text)


def read_state(path: Path, tail_bytes: int) -> TranscriptState:
    """transcript(Codex / Claude どちらの形式でも)から状態を抽出する。"""
    state = TranscriptState()
    for line in _read_tail_lines(path, tail_bytes):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        if "payload" in entry:
            _apply_codex(entry, state)
        else:
            _apply_claude(entry, state)
    return state


def should_intervene(
    state: TranscriptState, prompt: str, now: datetime, ctx_threshold: int, idle_minutes: int
) -> tuple[bool, str]:
    """介入すべきかと、その理由を返す。"""
    if state.context_tokens < ctx_threshold:
        return False, ""
    idle_min = (now - state.last_model_at).total_seconds() / 60 if state.last_model_at else 0
    if idle_min >= idle_minutes:
        return True, f"最後の応答から {idle_min:.0f} 分経過しておりキャッシュが切れている可能性が高い"
    if CONTINUE_PATTERN.match(prompt):
        return True, "「続き」系の再開指示で、巨大な文脈をそのまま引き継ごうとしている"
    return False, ""


def _git_summary(cwd: str) -> str:
    """cwd の git ブランチと変更ファイルを返す。git でなければ空文字。"""
    try:
        branch = subprocess.run(
            ["git", "-C", cwd, "branch", "--show-current"], capture_output=True, text=True, timeout=5, check=True
        ).stdout.strip()
        status = subprocess.run(
            ["git", "-C", cwd, "status", "--short"], capture_output=True, text=True, timeout=5, check=True
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""
    return f"- branch: `{branch}`\n\n```\n{status or '(clean)'}\n```"


def _clip(text: str) -> str:
    """長文を末尾優先で切り詰める。"""
    return text if len(text) <= SNIPPET_CHARS else "…" + text[-SNIPPET_CHARS:]


def _safe_id(session: str) -> str:
    """session_id をファイル名に使える文字だけに正規化する(パス逸脱の防止)。"""
    return re.sub(r"[^A-Za-z0-9_-]", "_", session)[:64] or "unknown"


def _prompt_digest(prompt: str) -> str:
    """再送判定用に入力のハッシュを取る(内容そのものはマーカーに残さない)。"""
    return hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()


def write_handoff(state: TranscriptState, hook_input: dict, agent: str, out_dir: Path, now: datetime) -> Path:
    """モデルを呼ばずに transcript から機械的にハンドオフ Markdown を書く。"""
    out_dir.mkdir(mode=PRIVATE_DIR_MODE, parents=True, exist_ok=True)
    out_dir.chmod(PRIVATE_DIR_MODE)  # 会話内容を含むため本人以外に読ませない(既存ディレクトリも締める)
    session = _safe_id(str(hook_input.get("session_id", "unknown")))
    local = now.astimezone()
    cwd = str(hook_input.get("cwd", ""))
    prompts = "\n".join(f"{i}. {_clip(p)}" for i, p in enumerate(state.user_prompts[-RECENT_PROMPTS:], 1))
    sections = [
        f"# Handoff ({agent}) {local:%Y-%m-%d %H:%M}",
        "",
        f"- cwd: `{cwd}`",
        f"- 元 transcript: `{hook_input.get('transcript_path', '')}`",
        f"- 直近の文脈サイズ: 約 {state.context_tokens:,} tokens",
        "",
        "## ブロックした依頼(まだ実行されていない)",
        "",
        _clip(str(hook_input.get("prompt", ""))) or "(なし)",
        "",
        "## 直近のユーザー指示",
        "",
        prompts or "(なし)",
        "",
        "## 直前のエージェント発言",
        "",
        _clip(state.last_agent_message) or "(なし)",
    ]
    if state.last_plan:
        sections += ["", "## 最新のプラン", "", "```json", _clip(state.last_plan), "```"]
    git = _git_summary(cwd) if cwd else ""
    if git:
        sections += ["", "## Git 状態", "", git]
    sections += [
        "",
        "## 新スレッドでの進め方",
        "",
        "- まずこのファイルと `git status` / `git log -5` で現状を把握する",
        "- 詳細が要るときだけ元 transcript を安いサブエージェントに grep させる(全文を読まない)",
    ]
    return _create_unique(out_dir, f"{local:%Y%m%d-%H%M%S}-{agent}-{session[:8]}", "\n".join(sections) + "\n")


def _create_unique(out_dir: Path, stem: str, body: str) -> Path:
    """既存ファイルを上書きせず、衝突したら連番を付けて新規作成する(本人のみ読み書き可)。"""
    for n in range(1, MAX_NAME_ATTEMPTS + 1):
        path = out_dir / (f"{stem}.md" if n == 1 else f"{stem}-{n}.md")
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, PRIVATE_FILE_MODE)
        except FileExistsError:
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(body)
        return path
    raise FileExistsError(f"ハンドオフのファイル名が {MAX_NAME_ATTEMPTS} 回衝突しました: {stem}")


def _bypass_marker(out_dir: Path, session: str) -> Path:
    """セッションごとの「一度ブロックした」マーカーのパス。"""
    return out_dir / ".bypass" / f"{_safe_id(session)}.marker"


def consume_bypass(out_dir: Path, session: str, prompt: str, bypass_minutes: int, now_ts: float) -> bool:
    """直前にブロックしたのと同じ入力の再送なら素通し扱いにする。マーカーは判定後に必ず消す。"""
    marker = _bypass_marker(out_dir, session)
    if not marker.exists():
        return False
    fresh = now_ts - marker.stat().st_mtime <= bypass_minutes * 60
    same = marker.read_text(encoding="utf-8").strip() == _prompt_digest(prompt)
    marker.unlink(missing_ok=True)
    return fresh and same


def block_message(reason: str, state: TranscriptState, handoff: Path, agent: str) -> str:
    """ユーザーに見せるブロック理由。"""
    new_cmd = "/new" if agent == "codex" else "/clear"
    return (
        f"[resume-guard] このスレッドは直近 約{state.context_tokens:,} tokens の文脈を毎回送り直しています。"
        f"{reason}ため、このまま再開すると数回で rate limit に達します。\n"
        f"ハンドオフを書き出しました: {handoff}\n"
        f"推奨: {new_cmd} してから「{handoff} を読んで続きをお願いします」と送ってください。\n"
        "(/compact してから再送するか、同じ内容をもう一度送ればこのまま続行できます)"
    )


def decide(hook_input: dict, agent: str) -> dict | None:
    """フック入力を評価し、ブロックするなら出力 JSON を、素通しなら None を返す。"""
    transcript = hook_input.get("transcript_path")
    if not transcript or not Path(transcript).is_file():
        return None

    out_dir = Path(os.environ.get("AGENT_HANDOFF_DIR", Path.home() / ".local/state/agent-handoff"))
    session = str(hook_input.get("session_id", "unknown"))
    prompt = str(hook_input.get("prompt", ""))
    now = datetime.now(UTC)
    bypass_minutes = _env_int("RESUME_GUARD_BYPASS_MINUTES", DEFAULT_BYPASS_MINUTES)
    if consume_bypass(out_dir, session, prompt, bypass_minutes, time.time()):
        return None

    state = read_state(Path(transcript), _env_int("RESUME_GUARD_TAIL_BYTES", DEFAULT_TAIL_BYTES))
    intervene, reason = should_intervene(
        state,
        prompt,
        now,
        _env_int("RESUME_GUARD_CTX_TOKENS", DEFAULT_CTX_TOKENS),
        _env_int("RESUME_GUARD_IDLE_MINUTES", DEFAULT_IDLE_MINUTES),
    )
    if not intervene:
        return None

    handoff = write_handoff(state, hook_input, agent, out_dir, now)
    marker = _bypass_marker(out_dir, session)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(_prompt_digest(prompt), encoding="utf-8")
    return {"decision": "block", "reason": block_message(reason, state, handoff, agent)}


def main(argv: list[str] | None = None) -> int:
    """フックのエントリポイント。stdin の JSON を読み、必要ならブロック JSON を stdout に出す。

    フック自身の不具合でユーザーの入力を止めないよう、失敗は stderr に出して素通しする。
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=["codex", "claude"], required=True)
    args = parser.parse_args(argv)

    if os.environ.get("RESUME_GUARD", "").lower() == "off":
        return 0
    try:
        hook_input = json.load(sys.stdin)
        result = decide(hook_input, args.agent)
    except json.JSONDecodeError as e:
        print(f"[resume-guard] 入力 JSON を読めませんでした: {e}", file=sys.stderr)
        return 0
    except OSError as e:
        print(f"[resume-guard] ファイル操作に失敗しました: {e}", file=sys.stderr)
        return 0
    if result:
        print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
