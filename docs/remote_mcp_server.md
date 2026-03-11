# リモートMCPサーバー設計

## 概要

現在の `ore-skills-server` は **stdio (標準入出力) ベース** のローカル専用MCPサーバーです。
このドキュメントでは、EC2などでホストして他のPCから利用可能な **SSE (Server-Sent Events) ベース** のリモートMCPサーバーの設計を説明します。

## MCPのトランスポート方式

### 1. stdio (現在の実装)

**特徴:**
- ローカルプロセスとして起動
- 標準入出力で通信
- Claude Desktopなどのクライアントが同じマシン上で実行

**設定例:**
```json
{
  "mcpServers": {
    "ore-skills": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/ore-skills", "ore-skills-server"]
    }
  }
}
```

**制約:**
- ❌ 他のPCからアクセス不可
- ❌ ネットワーク経由での利用不可
- ✅ セットアップが簡単
- ✅ セキュリティリスクが低い

### 2. SSE (Server-Sent Events) - リモート対応

**特徴:**
- HTTPサーバーとして起動
- SSE (Server-Sent Events) で通信
- ネットワーク経由でアクセス可能

**設定例:**
```json
{
  "mcpServers": {
    "ore-skills": {
      "url": "http://your-ec2-instance.com:8000/sse"
    }
  }
}
```

**メリット:**
- ✅ EC2などでホスト可能
- ✅ 他のPCから利用可能
- ✅ チーム全体で共有可能
- ✅ スケーラブル

**デメリット:**
- ❌ セキュリティ対策が必要（認証・認可）
- ❌ インフラ管理が必要
- ❌ ネットワーク遅延の影響を受ける

## SSE版の実装設計

### アーキテクチャ

```
┌─────────────────┐
│  Claude Desktop │
│  (Client PC)    │
└────────┬────────┘
         │ HTTPS
         │ SSE
         ▼
┌─────────────────────────────┐
│  EC2 Instance               │
│  ┌─────────────────────┐    │
│  │ ore-skills-server   │    │
│  │ (SSE Transport)     │    │
│  │                     │    │
│  │ ┌─────────────────┐ │    │
│  │ │ FastAPI/Starlette│ │   │
│  │ └─────────────────┘ │    │
│  │ ┌─────────────────┐ │    │
│  │ │ MCP SSE Handler │ │    │
│  │ └─────────────────┘ │    │
│  │ ┌─────────────────┐ │    │
│  │ │ Skills (media,  │ │    │
│  │ │        spec)    │ │    │
│  │ └─────────────────┘ │    │
│  └─────────────────────┘    │
└─────────────────────────────┘
```

### ディレクトリ構成

```
ore-skills/
├── servers/
│   ├── ore-skills-server/          # stdio版（既存）
│   │   ├── src/ore_skills_server/
│   │   │   └── main.py
│   │   └── pyproject.toml
│   └── ore-skills-server-sse/      # SSE版（新規）
│       ├── src/ore_skills_server_sse/
│       │   ├── main.py             # FastAPI + SSE実装
│       │   ├── auth.py             # 認証・認可
│       │   └── config.py           # 設定管理
│       ├── pyproject.toml
│       ├── Dockerfile              # コンテナ化
│       └── README.md
```

### 実装例（概要）

#### `servers/ore-skills-server-sse/src/ore_skills_server_sse/main.py`

```python
from fastapi import FastAPI, Request
from mcp.server.sse import SseServerTransport
from mcp.server import Server
from media import get_youtube_transcript
from spec import check_spec_file
import asyncio

app = FastAPI()
mcp_server = Server("ore-skills")

# ツールの登録
@mcp_server.list_tools()
async def list_tools():
    return [
        {
            "name": "get_transcript",
            "description": "YouTube動画の文字起こしを取得",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "video_id": {"type": "string"}
                },
                "required": ["video_id"]
            }
        },
        {
            "name": "check_spec",
            "description": "仕様書をチェック",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"}
                },
                "required": ["content"]
            }
        }
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_transcript":
        result = get_youtube_transcript(arguments["video_id"])
        return {"content": [{"type": "text", "text": result}]}
    elif name == "check_spec":
        issues = check_spec_file(arguments["content"])
        if not issues:
            result = "問題は見つかりませんでした。"
        else:
            result = "以下の問題が見つかりました：\n" + "\n".join(f"- {issue}" for issue in issues)
        return {"content": [{"type": "text", "text": result}]}

# SSEエンドポイント
@app.get("/sse")
async def sse_endpoint(request: Request):
    async with SseServerTransport("/messages") as transport:
        await mcp_server.run(
            transport.read_stream,
            transport.write_stream,
            mcp_server.create_initialization_options()
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### `servers/ore-skills-server-sse/pyproject.toml`

```toml
[project]
name = "ore-skills-server-sse"
version = "0.1.0"
description = "Remote MCP Server for ore-skills (SSE Transport)"
requires-python = ">=3.12"
dependencies = [
    "mcp>=1.0.0",
    "fastapi>=0.115.0",
    "uvicorn>=0.32.0",
    "common",
    "media",
    "spec",
]

[project.scripts]
ore-skills-server-sse = "ore_skills_server_sse.main:main"
```

#### `servers/ore-skills-server-sse/Dockerfile`

```dockerfile
# マルチステージビルド
FROM python:3.12-slim AS builder

WORKDIR /app

# uvのインストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 依存関係のコピー
COPY pyproject.toml uv.lock ./
COPY skills/ ./skills/
COPY servers/ore-skills-server-sse/ ./servers/ore-skills-server-sse/

# 依存関係のインストール
RUN uv sync --frozen

# 実行ステージ
FROM python:3.12-slim

WORKDIR /app

# uvと依存関係のコピー
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

# 環境変数
ENV PATH="/app/.venv/bin:$PATH"

# ポート公開
EXPOSE 8000

# サーバー起動
CMD ["python", "-m", "ore_skills_server_sse.main"]
```

## セキュリティ対策

### 1. 認証・認可

**APIキー認証の実装例:**

```python
# servers/ore-skills-server-sse/src/ore_skills_server_sse/auth.py
from fastapi import Header, HTTPException
import os

API_KEY = os.getenv("ORE_SKILLS_API_KEY", "your-secret-key")

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key
```

**FastAPIでの適用:**

```python
from fastapi import Depends
from .auth import verify_api_key

@app.get("/sse", dependencies=[Depends(verify_api_key)])
async def sse_endpoint(request: Request):
    # ...
```

**クライアント設定:**

```json
{
  "mcpServers": {
    "ore-skills": {
      "url": "https://your-ec2-instance.com/sse",
      "headers": {
        "X-API-Key": "your-secret-key"
      }
    }
  }
}
```

### 2. HTTPS化

**Let's Encryptを使用:**

```bash
# Certbotのインストール
sudo apt-get install certbot python3-certbot-nginx

# 証明書の取得
sudo certbot --nginx -d your-domain.com
```

**Nginxリバースプロキシ設定:**

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # SSE用の設定
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }
}
```

### 3. レート制限

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/sse")
@limiter.limit("10/minute")
async def sse_endpoint(request: Request):
    # ...
```

## デプロイ手順

### EC2へのデプロイ

#### 1. EC2インスタンスの準備

```bash
# インスタンスタイプ: t3.small 以上推奨
# OS: Ubuntu 22.04 LTS
# セキュリティグループ: 443 (HTTPS), 22 (SSH) を開放
```

#### 2. 必要なソフトウェアのインストール

```bash
# Dockerのインストール
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker $USER

# Nginxのインストール
sudo apt-get install -y nginx
```

#### 3. リポジトリのクローン

```bash
git clone https://github.com/gon9/ore-skills.git
cd ore-skills
```

#### 4. 環境変数の設定

```bash
# .env ファイルの作成
cat > .env << EOF
ORE_SKILLS_API_KEY=your-super-secret-api-key-here
EOF
```

#### 5. Dockerビルド・起動

```bash
# イメージのビルド
docker build -t ore-skills-server-sse -f servers/ore-skills-server-sse/Dockerfile .

# コンテナの起動
docker run -d \
  --name ore-skills-server \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  ore-skills-server-sse
```

#### 6. Nginxの設定

```bash
# 設定ファイルの作成
sudo nano /etc/nginx/sites-available/ore-skills

# SSL証明書の取得
sudo certbot --nginx -d your-domain.com

# Nginxの再起動
sudo systemctl restart nginx
```

### Docker Composeを使用する場合

#### `docker-compose.yml`

```yaml
version: '3.8'

services:
  ore-skills-server:
    build:
      context: .
      dockerfile: servers/ore-skills-server-sse/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ORE_SKILLS_API_KEY=${ORE_SKILLS_API_KEY}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - ore-skills-server
    restart: unless-stopped
```

#### 起動

```bash
docker-compose up -d
```

## クライアント設定

### Claude Desktop

```json
{
  "mcpServers": {
    "ore-skills-remote": {
      "url": "https://your-domain.com/sse",
      "headers": {
        "X-API-Key": "your-secret-key"
      }
    }
  }
}
```

### その他のMCPクライアント

同様に `url` と `headers` を設定することで利用可能です。

## 監視・ログ

### ログの確認

```bash
# Dockerログ
docker logs -f ore-skills-server

# Nginxログ
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### メトリクス収集（オプション）

Prometheus + Grafana を使用した監視も可能です。

## コスト試算

### EC2 (t3.small)
- インスタンス: ~$15/月
- データ転送: 使用量による
- EBS: ~$1/月

**合計: 約 $16-20/月**

### 代替案: AWS Lambda + API Gateway
- より安価（使用量ベース）
- コールドスタート問題あり

## まとめ

| 項目 | stdio版 (現在) | SSE版 (リモート) |
|------|---------------|-----------------|
| 利用範囲 | ローカルのみ | ネットワーク経由 |
| セットアップ | 簡単 | やや複雑 |
| セキュリティ | 高い | 対策必要 |
| コスト | 無料 | ~$20/月 |
| スケーラビリティ | 低い | 高い |
| チーム共有 | 不可 | 可能 |

**推奨:**
- 個人利用: stdio版
- チーム利用: SSE版

## 次のステップ

1. SSE版の実装が必要な場合は、`servers/ore-skills-server-sse/` を作成
2. セキュリティ要件を確認（APIキー、HTTPS、レート制限）
3. デプロイ先を決定（EC2, ECS, Lambda等）
4. CI/CDパイプラインの構築（GitHub Actions等）
