import glob
import os
import re
import subprocess
from urllib.parse import parse_qs, urlparse


def get_video_id(url):
    """
    YouTubeのURLから動画IDを抽出する
    """
    if not url.startswith('http'):
        return url
        
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            p = parse_qs(parsed_url.query)
            return p.get('v', [None])[0]
        if parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        if parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    return url

def clean_transcript_text(transcript_list):
    """
    JSON形式の字幕リストからテキストを結合する
    """
    full_text = ""
    for item in transcript_list:
        full_text += item['text'] + "\n"
    return full_text

def get_transcript_api(video_id):
    """
    youtube_transcript_apiを使用して字幕を取得する
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # 1. 直接 get_transcript を試す (日本語 -> 英語)
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja', 'en'])
            return clean_transcript_text(transcript)
        except Exception:
            pass
            
        # 2. list_transcripts 経由で探す
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 手動作成の日本語
            try:
                t = transcript_list.find_manually_created_transcript(['ja'])
                return clean_transcript_text(t.fetch())
            except:
                pass
                
            # 自動生成の日本語
            try:
                t = transcript_list.find_generated_transcript(['ja'])
                return clean_transcript_text(t.fetch())
            except:
                pass

            # 英語など
            for t in transcript_list:
                return clean_transcript_text(t.fetch())
                
        except Exception:
            pass
            
        return None

    except ImportError:
        return None
    except Exception:
        return None

def clean_vtt(vtt_content):
    lines = vtt_content.splitlines()
    text_lines = []
    seen = set()
    timestamp_pattern = re.compile(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}')
    
    for line in lines:
        line = line.strip()
        if not line: continue
        if line == 'WEBVTT' or line.startswith('Kind:') or line.startswith('Language:'): continue
        if timestamp_pattern.match(line): continue
        line = re.sub(r'<[^>]+>', '', line)
        if line not in seen:
            text_lines.append(line)
            seen.add(line)
    return "\n".join(text_lines)

def get_transcript_ytdlp(url):
    """
    yt-dlpを使用して字幕を取得する
    """
    video_id = get_video_id(url)
    output_template = f"transcript_{video_id}"
    
    # Clean up old files
    for f in glob.glob(f"{output_template}*"):
        try: os.remove(f)
        except: pass

    cmd = [
        "yt-dlp",
        "--write-auto-sub",
        "--sub-lang", "ja,en",
        "--skip-download",
        "--output", output_template,
        url
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        return None

    vtt_files = glob.glob(f"{output_template}*.vtt")
    if not vtt_files:
        return None
        
    # Prefer Japanese
    target_file = None
    for f in vtt_files:
        if ".ja." in f:
            target_file = f
            break
    if not target_file:
        target_file = vtt_files[0]
        
    with open(target_file, encoding='utf-8') as f:
        content = f.read()
    
    # Clean up
    for f in vtt_files:
        try: os.remove(f)
        except: pass
        
    return clean_vtt(content)
