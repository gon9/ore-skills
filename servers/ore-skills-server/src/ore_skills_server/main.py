from common import setup_logger
from mcp.server.fastmcp import FastMCP
from media import get_youtube_transcript
from spec import check_spec_file

# ロガー設定
logger = setup_logger("ore-skills-server")

# FastMCPサーバーの初期化
mcp = FastMCP(
    "ore-skills-experimental",
    instructions=(
        "Experimental backend for capabilities that benefit from a structured MCP contract. "
        "Use get_transcript for YouTube transcript retrieval and check_spec for deterministic Markdown validation. "
        "Do not use this server as a replacement for SKILL.md workflow guidance."
    ),
)


@mcp.tool()
def get_transcript(video_id: str) -> str:
    """指定されたYouTube動画IDの文字起こしを取得する。"""

    logger.info(f"Tool called: get_transcript for {video_id}")
    return get_youtube_transcript(video_id)


@mcp.tool()
def check_spec(content: str) -> str:
    """仕様書のMarkdownを検査し、問題を読みやすい文字列で返す。"""

    logger.info("Tool called: check_spec")
    issues = check_spec_file(content)
    if not issues:
        return "問題は見つかりませんでした。"
    return "以下の問題が見つかりました:\n" + "\n".join(f"- {issue}" for issue in issues)


def main() -> None:
    """experimentalなstdio MCPサーバーを起動する。"""

    mcp.run()


if __name__ == "__main__":
    main()
