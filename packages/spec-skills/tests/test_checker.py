import pytest
from spec_skills.checker import check_spec_file

def test_check_spec_file_empty():
    issues = check_spec_file("")
    assert len(issues) == 1
    assert "仕様書が空です" in issues[0]

def test_check_spec_file_missing_sections():
    content = "# 概要\nここに概要を書きます。"
    issues = check_spec_file(content)
    assert len(issues) == 2
    assert any("要件" in issue for issue in issues)
    assert any("構成" in issue for issue in issues)

def test_check_spec_file_valid():
    content = """
# 概要
概要です。

# 要件
要件です。

# 構成
構成です。
"""
    issues = check_spec_file(content)
    assert len(issues) == 0
