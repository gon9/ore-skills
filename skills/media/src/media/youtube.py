from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from common import setup_logger

logger = setup_logger(__name__)

def get_youtube_transcript(video_id: str, languages: list[str] = ['ja', 'en']) -> str:
    """
    指定されたYouTube動画の文字起こしを取得します。
    
    Args:
        video_id (str): YouTube動画ID
        languages (list[str]): 取得する言語の優先順位リスト
        
    Returns:
        str: 文字起こしテキスト
        
    Raises:
        Exception: 文字起こしの取得に失敗した場合
    """
    try:
        logger.info(f"Fetching transcript for video: {video_id}")
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        formatter = TextFormatter()
        text = formatter.format_transcript(transcript_list)
        return text
    except Exception as e:
        logger.error(f"Failed to fetch transcript: {e}")
        raise

if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="YouTube transcript fetcher")
    parser.add_argument("video_id", help="YouTube Video ID")
    parser.add_argument("--lang", nargs="+", default=['ja', 'en'], help="Languages to fetch (default: ja en)")
    
    args = parser.parse_args()
    
    try:
        print(get_youtube_transcript(args.video_id, args.lang))
    except Exception as e:
        sys.exit(1)
