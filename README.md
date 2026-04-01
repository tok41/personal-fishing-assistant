# personal-fishing-assistant

## 目的

- 釣行の記録をつけるサポートをする
- 記録をベースに釣行プランの計画サポートをする
- というアプリをネタに、複数のエージェント＋外部APIを利用した開発の練習をする

## ドキュメント

- AI エージェント向けの作業入口: `AGENTS.md`
- 設計書置き場: `docs/design/`

## Phase 1 実装

依存関係と仮想環境は `uv` で管理する。

## 実行手順

### 1. 初回セットアップ

```bash
uv sync
```

### 2. 環境変数を設定

`.env.example` を元に `.env` を作成し、少なくとも `OPENAI_API_KEY` を設定する。

```bash
cp .env.example .env
```

### 3. 釣行記録を配置

- 取り込み対象は `data/records/`
- ファイル形式は Notion エクスポートの Markdown
- ファイル名は `YYYY-MM-DD_場所名.md` 形式

例:

```text
data/records/2026-02-15_日立港.md
```

### 4. アプリを起動

```bash
uv run streamlit run app/frontend/main.py
```

リポジトリルートで実行する。

起動後、ブラウザで表示された Streamlit UI から以下を実行する。

- サイドバーの「Markdown をインポート」で `data/records/` 配下を一括取り込み
- チャット入力欄から質問して、関連記録を参照した回答を確認

### 5. テストを実行

```bash
uv run pytest
```

## テスト

- `uv run pytest`

## Python 環境方針

- システムの `python` / `pip` を直接使わず、`uv` 経由で実行する
- 仮想環境は `uv` が作る `.venv/` を使う
- 依存定義は `requirements.txt` ではなく `pyproject.toml` を正とする
- 日常的なコマンドは `uv run ...` で統一する

## 運用方針

- AI エージェントは `AGENTS.md` を起点に、担当ロールに応じたガイドだけを読む
- 設計内容は `docs/design/` に蓄積する
- 共通のAI運用ルール、レビュー観点、テンプレートは `docs/ai/` に置く
