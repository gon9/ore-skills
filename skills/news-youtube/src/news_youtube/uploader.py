"""YouTube Data API v3を使用した動画アップロード."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
DEFAULT_TOKEN_DIR = Path.home() / ".config" / "news-youtube"
DEFAULT_TOKEN_PATH = DEFAULT_TOKEN_DIR / "token.json"


def get_credentials(
    client_secret_path: str | Path | None = None,
    token_path: str | Path | None = None,
) -> Credentials:
    """OAuth 2.0認証情報を取得する.

    初回はブラウザ認証フローを実行し、トークンをキャッシュする。
    2回目以降はキャッシュされたトークンを再利用する。

    Args:
        client_secret_path: client_secret.jsonのパス
        token_path: トークンキャッシュのパス

    Returns:
        認証情報オブジェクト
    """
    if client_secret_path is None:
        client_secret_path = os.environ.get("YOUTUBE_CLIENT_SECRET_PATH")
    if client_secret_path is None:
        raise ValueError(
            "YouTube OAuth client_secret.json のパスを指定してください。"
            " 環境変数 YOUTUBE_CLIENT_SECRET_PATH またはCLI引数で設定できます。"
        )
    client_secret_path = Path(client_secret_path)

    if token_path is None:
        token_path = Path(os.environ.get("YOUTUBE_TOKEN_PATH", str(DEFAULT_TOKEN_PATH)))
    else:
        token_path = Path(token_path)

    creds: Credentials | None = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if creds is None or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_path), SCOPES)
            creds = flow.run_local_server(port=0)

        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json(), encoding="utf-8")

    return creds


@dataclass
class UploadParams:
    """YouTube動画アップロードのパラメータ."""

    video_path: str | Path
    title: str
    description: str
    tags: list[str] = field(default_factory=lambda: ["owlclaw", "AI", "ニュース", "テック"])
    category_id: str = "25"
    privacy_status: str = "public"
    client_secret_path: str | Path | None = None
    token_path: str | Path | None = None


def upload_video(params: UploadParams) -> str:
    """YouTube に動画をアップロードする.

    Args:
        params: アップロードパラメータ

    Returns:
        アップロードされた動画のID
    """
    video_path = Path(params.video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")

    creds = get_credentials(params.client_secret_path, params.token_path)
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": params.title,
            "description": params.description,
            "tags": params.tags,
            "categoryId": params.category_id,
            "defaultLanguage": "ja",
        },
        "status": {
            "privacyStatus": params.privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = _execute_upload(request)
    video_id: str = response["id"]
    return video_id


def _execute_upload(request) -> dict:
    """アップロードリクエストを実行する (リジューム対応)."""
    response = None
    while response is None:
        _, response = request.next_chunk()
    return response
