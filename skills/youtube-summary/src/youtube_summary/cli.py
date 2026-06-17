import argparse
import os
import subprocess
import sys

from youtube_summary.get_youtube_transcript import get_transcript_api, get_transcript_ytdlp, get_video_id
from youtube_summary.transcribe_audio import transcribe_audio


def get_video_info(url):
    """動画情報を取得"""
    print("📹 動画情報を取得中...", file=sys.stderr)
    cmd = ["yt-dlp", "--dump-json", url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import json
        data = json.loads(result.stdout)
        print(f"タイトル: {data.get('title')}", file=sys.stderr)
        print(f"時間: {data.get('duration')}秒", file=sys.stderr)
        print(f"アップロード日: {data.get('upload_date')}", file=sys.stderr)
        return data
    except Exception as e:
        print(f"⚠️  動画情報の取得に失敗: {e}", file=sys.stderr)
        return None

def try_get_transcript(url, video_id):
    """字幕データの取得を試行"""
    print("\n📝 字幕データの取得を試行中...", file=sys.stderr)
    transcript = get_transcript_api(video_id)
    if transcript:
        print("✅ 字幕データの取得に成功 (API)", file=sys.stderr)
        return transcript
        
    transcript = get_transcript_ytdlp(url)
    if transcript:
        print("✅ 字幕データの取得に成功 (yt-dlp)", file=sys.stderr)
        return transcript
        
    print("⚠️  字幕データの取得に失敗（制限されている可能性があります）", file=sys.stderr)
    return None

def download_audio(url, video_id):
    """音声ファイルをダウンロード"""
    print("\n🎵 音声ファイルをダウンロード中...", file=sys.stderr)
    output_file = f"video_audio_{video_id}.mp3"
    
    cmd = [
        "yt-dlp", "-x", "--audio-format", "mp3",
        "--output", f"video_audio_{video_id}.%(ext)s",
        url
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ 音声ファイルをダウンロード: {output_file}", file=sys.stderr)
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"❌ 音声ダウンロードに失敗: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="YouTube動画の内容を文字起こしするCLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("youtube_url", help="YouTube動画のURL")
    parser.add_argument("--keep-audio", action="store_true", 
                       help="音声ファイルを削除せずに保持する")
    args = parser.parse_args()
    
    video_id = get_video_id(args.youtube_url)
    if not video_id:
        print("❌ 動画IDの抽出に失敗しました", file=sys.stderr)
        sys.exit(1)
    
    print(f"🎬 動画ID: {video_id}", file=sys.stderr)
    get_video_info(args.youtube_url)
    
    transcript_file = f"transcript_{video_id}.txt"
    transcript = try_get_transcript(args.youtube_url, video_id)
    
    if transcript:
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"\n✅ 完了: {transcript_file}", file=sys.stderr)
    else:
        audio_file = download_audio(args.youtube_url, video_id)
        print(f"\n🎙️  文字起こし中: {audio_file}", file=sys.stderr)
        try:
            transcribe_audio(audio_file, transcript_file)
            print(f"✅ 文字起こし完了: {transcript_file}", file=sys.stderr)
            
            if not args.keep_audio and os.path.exists(audio_file):
                os.remove(audio_file)
                print(f"🗑️  音声ファイルを削除: {audio_file}", file=sys.stderr)
        except Exception as e:
            print(f"❌ 文字起こしに失敗: {e}", file=sys.stderr)
            sys.exit(1)
    
    print(f"\n📄 文字起こしファイル: {transcript_file}", file=sys.stderr)
    print("💡 このファイルを読み込んでLLMで要約を作成してください", file=sys.stderr)

if __name__ == "__main__":
    main()
