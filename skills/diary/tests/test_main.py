
from diary.main import build_filename, generate_frontmatter, get_vault_path


def test_generate_frontmatter():
    date_str = "2026-04-04"
    tags = ["type/journal", "topic/ai"]
    
    result = generate_frontmatter(date_str, tags)
    
    assert "date: 2026-04-04" in result
    assert "  - type/journal" in result
    assert "  - topic/ai" in result
    assert "created: " in result
    assert "---" in result

def test_build_filename():
    assert build_filename("2026-04-04", "AIエージェントの可能性") == "2026-04-04_ai.md"
    assert build_filename("2026-04-04", "AI Agent Potential") == "2026-04-04_ai-agent-potential.md"
    assert build_filename("2026-04-04", "今日の日記") == "2026-04-04_entry.md"

def test_get_vault_path(monkeypatch):
    monkeypatch.setenv("OBSIDIAN_VAULT_DIR", "/path/to/vault")
    assert get_vault_path() == "/path/to/vault"
    
    monkeypatch.delenv("OBSIDIAN_VAULT_DIR", raising=False)
    assert get_vault_path() is None
