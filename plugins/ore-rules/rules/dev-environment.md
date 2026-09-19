---
description: "開発環境の方針（Docker で統一、ローカルを汚さない、段階的セットアップ）"
trigger: always_on
---

## 環境

- ローカル環境は Mac（Apple Silicon）
- **ローカルファイルシステムを直接汚さない。** Docker / Docker Compose で開発環境を統一する
- Dockerfile はマルチステージビルドを使用する

## 進め方

- セットアップは段階的に実施し、各ステップで動作確認する
- スモールスタートで問題箇所を特定しやすくする
