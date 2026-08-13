# Notification design

## Why two Codex paths are needed

Codex `notify` invokes one external command with a JSON payload. It is useful for rich macOS turn-completion notifications. Codex TUI notifications are separate and cover interactive terminal events such as approvals or input waiting. Enable both instead of treating either as a complete replacement.

Recommended user-level `~/.codex/config.toml` settings:

```toml
notify = ["/Users/name/.local/bin/agent-notify-codex"]

[tui]
notifications = true
notification_condition = "unfocused"
notification_method = "auto"
```

Keep `notification_condition = "unfocused"` to avoid duplicate alerts while actively using the terminal. Use `"always"` only when explicitly requested.

## Claude Code

Use the `Notification` hook for approval or input waiting and the `Stop` hook for completion. Merge commands into `~/.claude/settings.json`; never replace the entire `hooks` object.

## macOS delivery

`terminal-notifier` provides a dedicated entry in System Settings. If it is unavailable or fails, the helper falls back to AppleScript, whose notification source may appear as Script Editor. macOS alert style, Notification Summary, Focus, and per-app permission remain machine-local and require verification on every Mac.
