from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_stable_plugin_bundle_is_current() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "sync-stable-plugin.py"), "--check"],
        cwd=repo_root,
        check=True,
    )
