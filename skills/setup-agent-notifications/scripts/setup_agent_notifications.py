#!/usr/bin/env python3
"""Claude Code と Codex CLI の macOS 通知を安全に構成・診断する。"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any

CLAUDE_NOTIFICATION_LABEL = "入力/許可待ち"


def _backup(path: Path) -> Path | None:
    """既存ファイルをタイムスタンプ付きで退避する。"""
    if not path.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup = path.with_name(f"{path.name}.bak.{stamp}")
    shutil.copy2(path, backup)
    return backup


def _hook_entry(command: str) -> dict[str, Any]:
    """Claude Code のコマンドフックを返す。"""
    return {"hooks": [{"type": "command", "command": command}]}


def merge_claude_hooks(settings: dict[str, Any], notify_path: Path) -> dict[str, Any]:
    """既存設定を保持したまま Claude Code 通知フックを追加する。"""
    hooks = settings.setdefault("hooks", {})
    commands = {
        "Notification": f'{notify_path} "Claude Code" "{CLAUDE_NOTIFICATION_LABEL}" "操作を待っています"',
        "Stop": f'{notify_path} "Claude Code" "完了" "応答が完了しました"',
    }
    for event, command in commands.items():
        entries = hooks.setdefault(event, [])
        found = any(
            hook.get("command") == command
            for entry in entries
            if isinstance(entry, dict)
            for hook in entry.get("hooks", [])
            if isinstance(hook, dict)
        )
        if not found:
            entries.append(_hook_entry(command))
    return settings


def _replace_root_key(text: str, key: str, value_line: str) -> str:
    """TOML のルートキーだけを置換し、なければ最初のテーブル前へ追加する。"""
    lines = text.splitlines()
    table_index = next((index for index, line in enumerate(lines) if line.lstrip().startswith("[")), len(lines))
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*=")
    for index in range(table_index):
        if pattern.match(lines[index]):
            lines[index] = value_line
            return "\n".join(lines).rstrip() + "\n"
    lines.insert(table_index, value_line)
    return "\n".join(lines).rstrip() + "\n"


def _upsert_tui(text: str) -> str:
    """既存の [tui] を保持しつつ推奨通知キーを設定する。"""
    desired = {
        "notifications": "notifications = true",
        "notification_condition": 'notification_condition = "unfocused"',
        "notification_method": 'notification_method = "auto"',
    }
    lines = text.splitlines()
    start = next((index for index, line in enumerate(lines) if line.strip() == "[tui]"), None)
    if start is None:
        suffix = ["", "[tui]", *desired.values()]
        return "\n".join([*lines, *suffix]).strip() + "\n"
    end = next(
        (index for index in range(start + 1, len(lines)) if lines[index].lstrip().startswith("[")),
        len(lines),
    )
    section = lines[start + 1 : end]
    for key, value_line in desired.items():
        pattern = re.compile(rf"^\s*{re.escape(key)}\s*=")
        match_index = next((index for index, line in enumerate(section) if pattern.match(line)), None)
        if match_index is None:
            section.append(value_line)
        else:
            section[match_index] = value_line
    return "\n".join([*lines[: start + 1], *section, *lines[end:]]).rstrip() + "\n"


def update_codex_config(text: str, notify_path: Path) -> tuple[str, list[str] | None]:
    """Codex の外部通知と TUI 通知を設定し、置換対象コマンドを返す。"""
    parsed = tomllib.loads(text) if text.strip() else {}
    existing = parsed.get("notify")
    previous: list[str] | None = None
    has_our_notifier = isinstance(existing, list) and any("agent-notify-codex" in str(item) for item in existing)
    if isinstance(existing, list) and existing and not has_our_notifier:
        previous = [str(item) for item in existing]
    if has_our_notifier:
        updated = text
    else:
        notify_line = f"notify = [{json.dumps(str(notify_path))}]"
        updated = _replace_root_key(text, "notify", notify_line)
    return _upsert_tui(updated), previous


def install(home: Path) -> None:
    """通知ヘルパーと CLI 設定をホームディレクトリへ配置する。"""
    script_dir = Path(__file__).resolve().parent
    bin_dir = home / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    for name in ("agent-notify", "agent-notify-codex"):
        destination = bin_dir / name
        _backup(destination)
        shutil.copy2(script_dir / name, destination)
        destination.chmod(0o755)

    claude_settings = home / ".claude" / "settings.json"
    claude_settings.parent.mkdir(parents=True, exist_ok=True)
    settings = json.loads(claude_settings.read_text()) if claude_settings.exists() else {}
    _backup(claude_settings)
    merged = merge_claude_hooks(settings, bin_dir / "agent-notify")
    claude_settings.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n")

    codex_config = home / ".codex" / "config.toml"
    codex_config.parent.mkdir(parents=True, exist_ok=True)
    original = codex_config.read_text() if codex_config.exists() else ""
    updated, previous = update_codex_config(original, bin_dir / "agent-notify-codex")
    _backup(codex_config)
    codex_config.write_text(updated)
    if previous:
        previous_path = home / ".config" / "agent-notifications" / "codex-previous-notify.json"
        previous_path.parent.mkdir(parents=True, exist_ok=True)
        previous_path.write_text(json.dumps(previous, ensure_ascii=False) + "\n")

    print("Installed notification helpers and merged Claude/Codex configuration.")


def check(home: Path) -> int:
    """現在の通知構成を検査し、欠落があれば非ゼロを返す。"""
    results: list[tuple[str, bool, str]] = []
    notify_path = home / ".local" / "bin" / "agent-notify"
    codex_notify_path = home / ".local" / "bin" / "agent-notify-codex"
    results.append(("notification helper", os.access(notify_path, os.X_OK), str(notify_path)))
    results.append(("Codex wrapper", os.access(codex_notify_path, os.X_OK), str(codex_notify_path)))

    claude_settings = home / ".claude" / "settings.json"
    claude_ok = False
    if claude_settings.exists():
        raw = claude_settings.read_text()
        claude_ok = "agent-notify" in raw and '"Notification"' in raw and '"Stop"' in raw
    results.append(("Claude hooks", claude_ok, str(claude_settings)))

    codex_config = home / ".codex" / "config.toml"
    codex_external = False
    codex_tui = False
    if codex_config.exists():
        config = tomllib.loads(codex_config.read_text())
        codex_external = "agent-notify-codex" in json.dumps(config.get("notify", []))
        tui = config.get("tui", {})
        codex_tui = tui.get("notifications") is True and tui.get("notification_condition") == "unfocused"
    results.append(("Codex external notify", codex_external, str(codex_config)))
    results.append(("Codex TUI notifications", codex_tui, str(codex_config)))

    backend = shutil.which("terminal-notifier") or ("/usr/bin/osascript" if Path("/usr/bin/osascript").exists() else "")
    results.append(("macOS backend", bool(backend), backend or "missing"))
    for label, ok, detail in results:
        print(f"{'OK' if ok else 'MISSING':7} {label}: {detail}")
    return 0 if all(ok for _, ok, _ in results) else 1


def test_notification(home: Path) -> int:
    """Claude と Codex の実通知経路をテストする。"""
    commands = [
        [str(home / ".local" / "bin" / "agent-notify"), "Claude Code", "入力待ち(テスト)", "通知経路のテストです"],
        [
            str(home / ".local" / "bin" / "agent-notify-codex"),
            json.dumps({"type": "input-required-test", "last-assistant-message": "Codex通知経路のテストです"}),
        ],
    ]
    return max(subprocess.run(command, check=False).returncode for command in commands)


def main() -> int:
    """CLI エントリーポイント。"""
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--install", action="store_true")
    group.add_argument("--test", action="store_true")
    parser.add_argument("--home", type=Path, default=Path.home(), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if platform.system() != "Darwin" and args.home == Path.home():
        print("This setup targets macOS.", file=sys.stderr)
        return 2
    if args.install:
        install(args.home)
        return check(args.home)
    if args.test:
        return test_notification(args.home)
    return check(args.home)


if __name__ == "__main__":
    raise SystemExit(main())
