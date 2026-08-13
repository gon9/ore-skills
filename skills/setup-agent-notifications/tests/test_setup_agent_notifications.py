"""setup-agent-notifications の設定マージを検証する。"""

from __future__ import annotations

import importlib.util
import json
import tomllib
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "setup_agent_notifications.py"
SPEC = importlib.util.spec_from_file_location("setup_agent_notifications", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_merge_claude_hooks_preserves_existing_and_is_idempotent(tmp_path: Path) -> None:
    settings = {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "existing"}]}]}}
    notify_path = tmp_path / "agent-notify"

    first = MODULE.merge_claude_hooks(settings, notify_path)
    second = MODULE.merge_claude_hooks(first, notify_path)

    assert second["hooks"]["Stop"][0]["hooks"][0]["command"] == "existing"
    rendered = json.dumps(second, ensure_ascii=False)
    assert rendered.count("応答が完了しました") == 1
    assert rendered.count("操作を待っています") == 1


def test_update_codex_config_adds_tui_and_preserves_previous_notify(tmp_path: Path) -> None:
    source = 'model = "gpt-test"\nnotify = ["/usr/local/bin/existing", "arg"]\n\n[tui]\nalternate_screen = "auto"\n'

    updated, previous = MODULE.update_codex_config(source, tmp_path / "agent-notify-codex")
    parsed = tomllib.loads(updated)

    assert previous == ["/usr/local/bin/existing", "arg"]
    assert parsed["notify"] == [str(tmp_path / "agent-notify-codex")]
    assert parsed["tui"]["alternate_screen"] == "auto"
    assert parsed["tui"]["notifications"] is True
    assert parsed["tui"]["notification_condition"] == "unfocused"


def test_update_codex_config_keeps_existing_chain_that_already_calls_notifier(tmp_path: Path) -> None:
    source = 'notify = ["/Applications/Client", "--previous-notify", "agent-notify-codex"]\n'

    updated, previous = MODULE.update_codex_config(source, tmp_path / "agent-notify-codex")
    parsed = tomllib.loads(updated)

    assert previous is None
    assert parsed["notify"] == ["/Applications/Client", "--previous-notify", "agent-notify-codex"]
    assert parsed["tui"]["notifications"] is True


def test_install_and_check_in_temporary_home(tmp_path: Path) -> None:
    MODULE.install(tmp_path)

    assert MODULE.check(tmp_path) == 0
    assert (tmp_path / ".local" / "bin" / "agent-notify").stat().st_mode & 0o111
    assert "Notification" in json.loads((tmp_path / ".claude" / "settings.json").read_text())["hooks"]
