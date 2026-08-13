---
name: setup-agent-notifications
description: Configure and diagnose reliable macOS notifications for Claude Code and Codex CLI. Use when notifications for completion, approval, or input waiting are missing, when validating CLI notification hooks, or when replicating the notification setup to another Mac.
---

# Setup agent notifications

Set up two complementary notification paths:

- Use Codex TUI notifications for approval and input-waiting events.
- Use a macOS notification command for turn completion and Claude Code hooks.

## Workflow

1. Require macOS and confirm `python3`, `claude`, and/or `codex` availability.
2. Run the read-only doctor first:

   ```bash
   python3 scripts/setup_agent_notifications.py --check
   ```

3. If configuration is missing, run:

   ```bash
   python3 scripts/setup_agent_notifications.py --install
   ```

   Preserve existing Claude hooks and Codex `notify` commands. The installer creates timestamped backups before changing config.

4. In System Settings > Notifications, configure `terminal-notifier` or `Script Editor` with notifications enabled, sounds enabled, Persistent alert style, and Notification Summary disabled. Also check Focus modes.
5. Run the live test from the normal macOS user context, not a restricted sandbox:

   ```bash
   python3 scripts/setup_agent_notifications.py --test
   ```

6. Re-run `--check` and report each path separately: Claude hook, Codex TUI, Codex external notifier, and macOS delivery.

## Safety

- Do not overwrite unrelated hooks or notification commands.
- Do not install Homebrew packages without user approval. `terminal-notifier` is preferred; AppleScript is the built-in fallback.
- Do not claim success from config inspection alone. Send a live test notification and ask whether the popup appeared.
- Treat an `Abort trap` inside a restricted agent sandbox as inconclusive; retry the notification test in the normal user context.

For the rationale and event coverage, read [references/design.md](references/design.md).
