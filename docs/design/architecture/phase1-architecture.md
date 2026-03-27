# Phase 1 アーキテクチャ設計

## 概要

釣行アシスタントアプリケーション Phase 1（MVP）のシステムアーキテクチャを定義する。Phase 1では、NotionからエクスポートしたMarkdownファイルをインポートし、RAG（Retrieval-Augmented Generation）を使ってAIと対話できる基本機能を実装する。

## 背景

### 解決したい課題

- 釣行記録を知識ベースとして活用し、過去の記録を参照しながらAIと対話したい
- 手動で記録を貼り付ける運用から脱却し、自動的に関連記録を検索して参照できるようにしたい
- 個人利用のため、ローカル環境で動作する軽量な構成にしたい

### 前提条件

- ローカル環境（PC）で動作
- インターネット接続あり（OpenAI API利用のため）
- Python 3.10以上の実行環境
- 個人利用（単一ユーザー）

### 制約

- Phase 1では会話履歴の永続化なし（バックエンドはステートレス）
- 会話履歴はフロントエンドのセッション状態（`st.session_state`）で保持し、ページリロードで消える
- Phase 1では構造化データの抽出なし（全文検索のみ）
- 外部公開なし（ローカルホストのみ）
- 1ファイル1ベクトルとする（概ね3,000文字を超えるファイルは警告ログを出力）

## ゴール

Phase 1で実現すること：

- Markdownファイルからの釣行記録インポート
- FAISSを使った全文ベクトル検索
- OpenAI API（gpt-5-mini）を使ったRAGベースのAI対話
- Web UIでのチャットインターフェース
- 主要な異常系のエラーハンドリング

## 非ゴール

Phase 1では実装しないこと（Phase 2以降）：

- 会話履歴の永続化と管理
- プロフィール・サマリ・課題の自動生成
- Notion API連携
- 構造化データによるフィルタリング検索
- マルチユーザー対応

## 要件

要件定義書（`docs/design/requirements/fishing-assistant-v1.md`）のPhase 1部分を参照：

- FR-1: 釣行記録のインポート
- FR-2: 釣行記録の検索
- FR-3: AI対話機能
- FR-4: チャットインターフェース

## 提案する設計

### システム全体構成

```
┌─────────────────────────────────────────────────────────────┐
│                         ユーザー                              │
└──────────────────────────┬──────────────────────────────────┘
                           │ ブラウザ
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              フロントエンド (Streamlit)                        │
│  - チャット UI（st.chat_message）                             │
│  - インポート UI                                              │
│  - 会話履歴（st.session_state）                               │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           ビジネスロジック層                          │    │
│  │  ┌──────────────┐  ┌──────────────┐                 │    │
│  │  │ インポート    │  │ チャット      │                 │    │
│  │  │ サービス      │  │ サービス      │                 │    │
│  │  └──────┬───────┘  └───────┬──────┘                 │    │
│  │         │                    │                        │    │
│  │         ↓                    ↓                        │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │    │
│  │  │ ドキュメント  │  │ 検索          │  │ AI        │  │    │
│  │  │ パーサー      │  │ エンジン      │  │ クライアント│  │    │
│  │  └──────┬───────┘  └───────┬──────┘  └─────┬─────┘  │    │
│  └─────────┼──────────────────┼───────────────┼────────┘    │
│            ↓                  ↓               ↓              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              データアクセス層                         │    │
│  │  ┌──────────────┐  ┌──────────────┐                 │    │
│  │  │ ドキュメント  │  │ ベクトルストア │                │    │
│  │  │ リポジトリ    │  │ リポジトリ    │                 │    │
│  │  └──────┬───────┘  └───────┬──────┘                 │    │
│  └─────────┼──────────────────┼────────────────────────┘    │
└────────────┼──────────────────┼─────────────────────────────┘
             ↓                  ↓
┌─────────────────────────────────────────────────────────────┐
│                      データストレージ                          │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  data/records/   │  │ data/vector_store/│                │
│  │  - *.md ファイル  │  │ - FAISS インデックス│               │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                           ↑
                           │
                  ┌────────┴────────┐
                  │  OpenAI API     │
                  │  (gpt-5-mini)   │
                  └─────────────────┘
```

### モジュール構成

#### 1. フロントエンド (`app/frontend/`)

**責務**: UI表示とユーザー操作の受付、セッション状態の管理

- `main.py`: Streamlitアプリエントリポイント（`streamlit run app/frontend/main.py`）
  - チャットUI（`st.chat_message` / `st.chat_input`）
  - インポートUI（ファイルパス入力 / 実行ボタン）
  - 会話履歴の表示と管理（`st.session_state["messages"]`）
  - エラー表示（`st.error()` / `st.warning()`）

#### 2. ビジネスロジック層 (`app/services/`)

**責務**: アプリケーションのコアロジック

- `import_service.py`: インポート処理の統括
  - Markdownファイルの読み込み
  - パース処理の実行
  - ベクトル化とインデックス登録

- `chat_service.py`: チャット処理の統括
  - ユーザー入力の受付
  - 検索エンジンの呼び出し
  - AIクライアントの呼び出し
  - フォールバック処理（検索結果0件時）

#### 3. コアモジュール (`app/core/`)

**責務**: 再利用可能なコア機能

- `document_parser.py`: Markdownパーサー
  - Markdownファイルの読み込み
  - フォーマットバリデーション
  - テキスト抽出

- `search_engine.py`: 検索エンジン
  - クエリのベクトル化
  - FAISS検索の実行
  - 検索結果のフォーマット

- `ai_client.py`: OpenAI APIクライアント
  - APIキーの検証
  - プロンプト生成
  - API呼び出し
  - レスポンスのパース

#### 4. データアクセス層 (`app/repositories/`)

**責務**: データの永続化と取得

- `document_repository.py`: ドキュメント管理
  - Markdownファイルの保存
  - メタデータの管理（ファイル名、日付など）

- `vector_store_repository.py`: ベクトルストア管理
  - FAISSインデックスの作成
  - インデックスへの追加
  - インデックスの保存/読み込み
  - 類似度検索の実行

#### 5. 設定・ユーティリティ (`app/config/`, `app/utils/`)

- `config/settings.py`: 設定管理
  - 環境変数の読み込み
  - OpenAI APIキー
  - ディレクトリパス
  - 検索パラメータ（K=5など）

- `utils/logger.py`: ログ管理
- `utils/validators.py`: バリデーション関数

### データフロー

#### インポートフロー

```
1. ユーザーが「インポート」ボタンをクリック
   ↓
2. ImportService.import_documents()
   ↓
3. DocumentParser.parse_markdown_files(data/records/)
   - ファイル一覧取得
   - 各ファイルをパース（1ファイル1ベクトル）
   - 3,000文字超のファイルは警告ログを出力（処理は続行）
   - エラーファイルはスキップ（エラーログ記録）
   ↓
4. VectorStoreRepository.add_documents()
   - テキストをベクトル化（OpenAI Embeddings: text-embedding-3-small）
   - FAISSインデックス（IndexFlatL2）に追加
   ↓
5. VectorStoreRepository.save_index()
   - インデックスをディスクに保存
   ↓
6. Streamlit UI に結果表示（登録件数、エラー件数）
```

#### チャットフロー

```
1. ユーザーが質問を入力（st.chat_input）
   ↓
2. Streamlit が st.session_state["messages"] にユーザーメッセージを追加
   - ChatMessage(role="user", content="質問文")
   ↓
3. ChatService.process_message(query)
   ↓
4. SearchEngine.search(query, k=5)
   - クエリをベクトル化
   - FAISSで類似検索（IndexFlatL2、L2距離で評価）
   - 上位5件を取得
   ↓
5. AIClient.generate_response(query, documents)
   - プロンプト生成
     - システムプロンプト
     - 検索された記録（0件の場合は含めない）
     - ユーザーの質問
   - OpenAI API呼び出し（gpt-5-mini）
   - レスポンス取得
   ↓
6. Streamlit が st.session_state["messages"] にアシスタントメッセージを追加
   - ChatMessage(role="assistant", content="AIの回答")
   ↓
7. 画面上に会話履歴を全件再描画（st.chat_message でループ表示）
```

### データモデル

#### Document（ドキュメント）

```python
@dataclass
class Document:
    id: str                 # ファイル名をベースにしたID
    filename: str           # 元のファイル名（例: 2026-02-15_日立港.md）
    content: str            # Markdownの全文
    date: Optional[date]    # ファイル名から抽出した日付
    location: Optional[str] # ファイル名から抽出した場所
    created_at: datetime    # インポート日時
```

#### SearchResult（検索結果）

```python
@dataclass
class SearchResult:
    document: Document
    distance: float  # L2距離（小さいほど類似度が高い）
```

#### ChatMessage（会話メッセージ）

```python
@dataclass
class ChatMessage:
    role: str     # "user" または "assistant"
    content: str  # メッセージ本文
```

フロントエンドの `st.session_state["messages"]` に `List[ChatMessage]` として保持する。

#### ChatResponse（AIレスポンス）

```python
@dataclass
class ChatResponse:
    message: str          # AIの回答
    has_records: bool     # 関連記録が見つかったか
    record_count: int     # 検索された記録数
```

### 技術スタック

#### バックエンド / フロントエンド（統合）

- **言語**: Python 3.10+
- **UIフレームワーク**: Streamlit（採用確定）
  - 理由: Pythonで統一、チャットUIが標準機能で実装可能、高速プロトタイピング
  - 起動: `streamlit run app/frontend/main.py`
  - HTTPサーバー（FastAPI等）は Phase 1では不要（Streamlit が直接サービス層を呼び出す）
- **ベクトルストア**: FAISS（採用確定）
  - インデックスタイプ: `IndexFlatL2`（シンプルで小規模データ向け）
- **Embeddings**: OpenAI Embeddings API（`text-embedding-3-small`、採用確定）
- **LLM**: OpenAI Chat API（`gpt-5-mini`、採用確定）

#### データストレージ

```
data/
├── records/           # Markdownファイル（Git管理外）
│   ├── 2026-02-15_日立港.md
│   └── ...
├── vector_store/      # FAISSインデックス（Git管理外）
│   ├── index.faiss
│   └── metadata.json
└── logs/              # ログファイル
    └── app.log
```

### ディレクトリ構成

```
personal-fishing-assistant/
├── app/
│   ├── __init__.py
│   ├── frontend/              # Streamlit アプリ（エントリポイント）
│   │   ├── __init__.py
│   │   └── main.py            # streamlit run app/frontend/main.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── import_service.py
│   │   └── chat_service.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── document_parser.py
│   │   ├── search_engine.py
│   │   └── ai_client.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── document_repository.py
│   │   └── vector_store_repository.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── domain.py          # データクラス定義（Document, SearchResult, ChatMessage, ChatResponse）
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── validators.py
├── data/                       # Git管理外（.gitignore）
│   ├── records/
│   ├── vector_store/
│   └── logs/
├── tests/
│   ├── __init__.py
│   ├── test_import_service.py
│   ├── test_search_engine.py
│   └── test_ai_client.py
├── docs/
│   ├── ai/
│   └── design/
├── .env.example                # 環境変数テンプレート
├── .gitignore
├── requirements.txt
├── README.md
└── pyproject.toml              # Poetry使用の場合
```

### エラーハンドリング

#### APIキー未設定

```python
# 起動時チェック（frontend/main.py）
if not settings.OPENAI_API_KEY:
    st.error("OpenAI API key is not set. Please set OPENAI_API_KEY in .env file.")
    st.stop()
```

#### インポート時のエラー

- **対象ファイル0件**: `st.warning()` でメッセージ表示
- **Markdown形式不正**: 該当ファイルをスキップ、エラーログに記録、処理継続
- **ベクトル化エラー**: エラーログに記録、該当ファイルをスキップ
- 完了後に `st.success("○件インポート完了（△件エラー）")` を表示

#### チャット時のエラー

- **検索結果0件**: `has_records=False` でフォールバック、一般回答を生成（UI変化なし）
- **OpenAI APIエラー**: `st.error()` でエラーメッセージを表示
- **タイムアウト（30秒）**: `st.error()` でタイムアウトメッセージを表示

## 検討した代替案

### 1. フロントエンド技術選定

#### 採用: Streamlit（サービス層直接呼び出し）

**採用理由:**
- Pythonで統一でき、開発速度が速い
- チャットUIが標準機能で実装できる（`st.chat_message` / `st.chat_input`）
- `st.session_state` で会話履歴を保持でき、FR-4を満たせる
- Phase 1の要件（シンプルなチャットUI・個人利用・ローカル）に十分

**Streamlitのみ（APIサーバーなし）を採用した理由:**
- Streamlit から Python のサービス層を直接インポートして呼び出せるため、APIサーバーは不要
- Phase 1はローカル単一ユーザー利用のため、プロセス分離のメリットがない
- コード量と起動手順をシンプルに保てる

**トレードオフ:**
- 外部クライアントからのAPI呼び出しは不可（Phase 1では不要）
- Phase 3以降でクラウドデプロイや他クライアント対応が必要になった場合、FastAPIを追加する想定

#### 不採用: React + TypeScript

**不採用理由:**
- 開発時間が増える
- フロントエンド/バックエンドで言語が分かれる
- Phase 1の要件に対してオーバースペック

#### 不採用: Gradio

**不採用理由:**
- Streamlitと同等の機能だが、コミュニティとドキュメントがStreamlitより少ない

### 2. Webフレームワーク（HTTPサーバー）選定

#### 採用: なし（Phase 1）

**判断理由:**
- Streamlit が直接サービス層を呼び出すため、HTTPサーバーは不要
- FastAPI は Phase 3以降（外部公開・マルチクライアント）で追加を検討

#### 不採用: FastAPI

**不採用理由（Phase 1）:**
- Streamlit と同一プロセスで動かす必要がなく、HTTPを経由するメリットがない
- 個人利用・ローカル環境では責務分離よりシンプルさを優先

#### 不採用: Flask

**不採用理由:**
- FastAPIと同様に Phase 1では不要

### 3. ベクトルストア選定

#### 採用: FAISS

**採用理由:**
- ローカル環境で動作
- 小規模データ（100件程度）に十分な性能
- 外部サービス不要（コスト削減）

#### 案B: Pinecone / Weaviate

**不採用理由:**
- 外部サービスで利用料金が発生
- 個人利用でオーバースペック
- Phase 3以降で検討

## 判断理由

### なぜこの設計が妥当なのか

#### 1. レイヤー分離の徹底

- **フロントエンド（Streamlit）/ サービス層 / データ層**を明確に分離
- 理由: Phase 2以降での機能追加に対応しやすい
- 例: Phase 2で会話履歴機能を追加する際、サービス層に`ConversationService`を追加するだけで済む
- Phase 1では API層（HTTPサーバー）を持たない。Phase 3以降で外部公開が必要になった場合、Streamlit と並行して FastAPI を追加する

#### 2. シンプルな技術スタック

- **Pythonで統一**（バックエンド、フロントエンド）
- 理由: 個人開発で学習コストを最小化、保守性を高める

#### 3. FAISSの採用

- **ローカルで完結**
- 理由: 個人利用で外部サービスのコスト不要、データが外部に出ない

#### 4. Streamlitの採用

- **高速プロトタイピング**
- 理由: Phase 1のMVPを早く動かし、要件をフィードバックで改善できる

#### 5. ステートレス設計

- **Phase 1では会話履歴を永続化しない**
- 理由: 複雑さを避け、RAG機能の検証に集中できる
- Phase 2で会話履歴機能を追加する際、データベース（SQLite）を導入する想定

## リスクと未解決事項

### リスク

1. **FAISSの検索精度**
   - リスク: 全文ベクトル検索のみで、期待する精度が出ない可能性
   - 対策: Phase 1実装後、実際の記録で精度を検証。Phase 2で構造化データによるフィルタリングを追加

2. **Streamlitのパフォーマンス**
   - リスク: Streamlitはページ全体を再レンダリングするため、レスポンスが遅い可能性
   - 対策: 実装後に体感を確認。問題があればReactへの移行を検討

3. **OpenAI APIのコスト**
   - リスク: gpt-5-miniでもコストが予想より高い可能性
   - 対策: 使用量をモニタリング。必要に応じてgpt-3.5-turboへのダウングレードを検討

### 未解決事項

1. **ログレベルと出力先**
   - 現状: 開発時はDEBUG、本番（個人利用）はINFO
   - 確定タイミング: Phase 1実装時に決定

（以下は設計レビューを経て確定済み）
- FAISSインデックスタイプ: `IndexFlatL2` に確定
- Embeddingモデル: `text-embedding-3-small` に確定
- フロントエンド: Streamlit（APIサーバーなし）に確定
- チャンク化方針: 1ファイル1ベクトルに確定

## 検証方針

### 設計レビュー

- Reviewerに本設計書をレビューしてもらう
- 特に以下の観点を確認:
  - レイヤー分離の妥当性
  - モジュール間の責務分担
  - Phase 2への拡張性

### 実装方針

1. **ボトムアップで実装**
   - データアクセス層 → コアモジュール → サービス層 → フロントエンド（Streamlit）
   - 各層ごとにユニットテストを実装

2. **段階的な統合**
   - まずインポート機能を完成させる
   - 次にチャット機能（検索 + AI対話）を実装
   - 最後にフロントエンドを統合

3. **テスト戦略**
   - ユニットテスト: 各モジュールの単体テスト
   - 統合テスト: インポートフロー、チャットフローの E2E テスト
   - 手動テスト: 実際の釣行記録を使った動作確認

### 検証基準

要件定義書の受け入れ条件（Phase 1）をすべて満たすこと：
- インポート機能が動作すること
- 検索機能が動作すること
- AI対話機能が動作すること
- 主要な異常系でエラーメッセージが表示されること
