import os
import sys

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Error: faster-whisper is not installed.", file=sys.stderr)
    sys.exit(1)

def transcribe_audio(audio_path, output_path="transcript.txt", model_size="small", language="ja"):
    """
    音声ファイルを文字起こしする
    
    Args:
        audio_path: 音声ファイルのパス
        output_path: 出力先のテキストファイルパス
        model_size: Whisperモデルのサイズ (tiny, base, small, medium, large)
        language: 音声の言語コード (ja, en等)
    """
    if not os.path.exists(audio_path):
        print(f"Error: File {audio_path} not found.", file=sys.stderr)
        raise FileNotFoundError(f"File {audio_path} not found.")

    print(f"Loading Whisper model (size: {model_size})...", file=sys.stderr)
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    print(f"Transcribing {audio_path}...", file=sys.stderr)
    segments, info = model.transcribe(audio_path, beam_size=5, language=language)

    print(f"Detected language '{info.language}' with probability {info.language_probability}", file=sys.stderr)

    transcript = ""
    last_text = ""
    repeat_count = 0
    
    for segment in segments:
        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}", file=sys.stderr)
        
        # ループ検出（Whisperのハルシネーション対策）
        if segment.text.strip() == last_text:
            repeat_count += 1
        else:
            repeat_count = 0
        
        if repeat_count > 5:
            print("Warning: Detected looping text, stopping transcription.", file=sys.stderr)
            break
            
        last_text = segment.text.strip()
        transcript += segment.text + "\n"
    
    # 出力
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(transcript)
    
    print(f"\nTranscription saved to: {output_path}", file=sys.stderr)
    return transcript
