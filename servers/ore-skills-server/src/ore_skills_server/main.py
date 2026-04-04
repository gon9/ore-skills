from common import setup_logger
from mcp.server.fastmcp import FastMCP
from media import get_youtube_transcript
from spec import check_spec_file

# ロガー設定
logger = setup_logger("ore-skills-server")

# FastMCPサーバーの初期化
mcp = FastMCP("ore-skills")

@mcp.tool()
def get_transcript(video_id: str) -> str:
    """
    指定されたYouTube動画の文字起こしを取得します。
    
    Args:
        video_id (str): YouTube動画ID
    """
    logger.info(f"Tool called: get_transcript for {video_id}")
    return get_youtube_transcript(video_id)

@mcp.tool()
def check_spec(content: str) -> str:
    """
    仕様書（Markdown）の内容を簡易チェックし、結果を文字列で返します。
    
    Args:
        content (str): 仕様書の内容
    """
    logger.info("Tool called: check_spec")
    issues = check_spec_file(content)
    if not issues:
        return "問題は見つかりませんでした。"
    return "以下の問題が見つかりました：\n" + "\n".join(f"- {issue}" for issue in issues)

def main():
    mcp.run()

if __name__ == "__main__":
    main()
