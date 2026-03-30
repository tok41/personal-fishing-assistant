# personal-fishing-assistant

## 目的

- 釣行の記録をつけるサポートをする
- 記録をベースに釣行プランの計画サポートをする
- というアプリをネタに、複数のエージェント＋外部APIを利用した開発の練習をする

## ドキュメント

- AI エージェント向けの作業入口: `AGENTS.md`
- 設計書置き場: `docs/design/`

## Phase 1 実装

- 依存関係と仮想環境は `uv` で管理する
- 初回セットアップ: `uv sync`
- Streamlit UI: `uv run streamlit run app/frontend/main.py`
- 釣行記録: `data/records/` に `YYYY-MM-DD_場所名.md` 形式で配置
- 環境変数: `.env.example` を元に `.env` を作成し、`OPENAI_API_KEY` を設定

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
