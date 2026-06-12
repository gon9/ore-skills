# YouTube Data API v3 セットアップガイド

## 1. Google Cloud Console でプロジェクト作成

1. https://console.cloud.google.com/ にアクセス
2. 新規プロジェクトを作成 (例: `owlclaw-news`)
3. YouTube Data API v3 を有効化

## 2. OAuth 2.0 クライアント作成

1. APIs & Services > Credentials
2. Create Credentials > OAuth client ID
3. Application type: Desktop app
4. 作成後、`client_secret.json` をダウンロード

## 3. 初回認証

```bash
export YOUTUBE_CLIENT_SECRET_PATH=/path/to/client_secret.json
uv run news-youtube --video-only /path/to/daily.md
```

初回実行時にブラウザが開き、Googleアカウントでの認証が求められる。
認証後、トークンが `~/.config/news-youtube/token.json` にキャッシュされる。

## 4. Google Home での再生

動画タイトルが `owlclaw AI Digest YYYY-MM-DD` 形式で統一されるため、
Google Home / Nest デバイスで以下のように呼びかけて再生可能:

- 「OK Google, YouTubeで owlclaw を再生」
- 「OK Google, owlclaw AI Digest を再生して」

チャネル内で最新動画が優先的に再生される。

## 5. カテゴリID

デフォルト: `25` (News & Politics)
変更する場合は `upload_video()` の `category_id` 引数を指定。

## 6. クォータ制限

YouTube Data API v3 のデフォルトクォータ: 10,000 units/日
動画アップロード: 1,600 units/回
1日あたり約6回のアップロードが可能。
