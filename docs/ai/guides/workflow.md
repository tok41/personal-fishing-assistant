# Development Workflow Guide

## 概要

このドキュメントは、プロジェクト開始から実装、レビューまでの基本的なワークフローを示します。

## 基本フロー

```
要件定義 → 設計 → 実装 → テスト → レビュー → リリース
```

各ステップで必要な成果物とドキュメントを以下に示します。

## 1. 要件定義

**担当ロール**: Architect

**目的**:
- 何を作るのかを明確にする
- 実装前の曖昧さを減らす
- 受け入れ条件を定義する

**作業内容**:
1. 背景と目的の整理
2. 機能要件と非機能要件の洗い出し
3. スコープと対象外の明確化
4. 受け入れ条件の定義
5. 制約条件と依存関係の確認

**成果物**:
- `docs/design/requirements/[feature-name]-requirements.md`（requirements-template.md を使用）

**参照ドキュメント**:
- `docs/ai/templates/requirements-template.md`
- `docs/ai/checklists/requirements-review-checklist.md`

**次のステップへの条件**:
- 要件がレビューされ、承認されていること
- 受け入れ条件が明確であること
- 未解決事項が許容範囲内であること

## 2. 設計

**担当ロール**: Architect

**目的**:
- 要件を実現するための構成を決める
- データモデルとインターフェースを定義する
- 実装とテストの見通しを立てる

**作業内容**:
1. 要件書の確認
2. アーキテクチャ構成の検討
3. データモデルの設計
4. インターフェース定義
5. 代替案の比較と判断理由の記録
6. リスクと未解決事項の明示

**成果物**:
- `docs/design/[feature-name]-design.md`（design-template.md を使用）
- 必要に応じて ADR（`docs/design/adr/[number]-[title].md`）

**参照ドキュメント**:
- `docs/design/requirements/[feature-name]-requirements.md`
- `docs/ai/templates/design-template.md`
- `docs/ai/templates/adr-template.md`
- `docs/ai/checklists/design-review-checklist.md`

**次のステップへの条件**:
- 設計がレビューされ、承認されていること
- 実装に進むための見通しが立っていること
- テスト方針が明確であること

## 3. 実装

**担当ロール**: Implementer

**目的**:
- 承認された設計をコードに落とし込む
- テスト可能な実装を提供する

**作業内容**:
1. 要件書と設計書の確認
2. 不明点や矛盾の洗い出し（あれば Architect にエスカレーション）
3. モジュール境界を明確にした実装
4. 単体テストの作成
5. 必要に応じてドキュメントの更新

**成果物**:
- 本番コード
- テストコード
- 必要に応じたドキュメント更新

**参照ドキュメント**:
- `docs/design/requirements/[feature-name]-requirements.md`
- `docs/design/[feature-name]-design.md`
- `docs/ai/checklists/code-review-checklist.md`

**次のステップへの条件**:
- 単体テストが通っていること
- コードレビューの準備ができていること

## 4. テスト

**担当ロール**: Tester

**目的**:
- 要件を満たしているかを検証する
- カバレッジ不足を見つける

**作業内容**:
1. 要件書の受け入れ条件の確認
2. テストケースの作成
3. 正常系、異常系、境界値のカバレッジ確認
4. 統合テストやE2Eテストの実施（必要に応じて）
5. 不足しているテストの指摘

**成果物**:
- テストケースと実行結果
- カバレッジレポート
- テスト不足の指摘

**参照ドキュメント**:
- `docs/design/requirements/[feature-name]-requirements.md`
- `docs/design/[feature-name]-design.md`
- `docs/ai/checklists/test-review-checklist.md`

## 5. レビュー

**担当ロール**: Reviewer

**目的**:
- 要件と設計への整合性を確認する
- リスクと未検証事項を明らかにする

**作業内容**:
1. 要件、設計、実装、テストの整合性確認
2. コード品質、保守性、テスト容易性の評価
3. 指摘事項の重大度順の整理
4. フォローアップ提案

**成果物**:
- レビュー指摘リスト
- 未解決事項とリスクの整理

**参照ドキュメント**:
- 各成果物（要件書、設計書、コード、テスト）
- `docs/ai/checklists/requirements-review-checklist.md`
- `docs/ai/checklists/design-review-checklist.md`
- `docs/ai/checklists/code-review-checklist.md`
- `docs/ai/checklists/test-review-checklist.md`

## 要件変更時の原則

開発中に要件の追加や変更が発生した場合、以下の原則に従います。

### 1. 影響範囲の確認

変更が以下のどこに影響するかを確認する:
- 既存の要件書
- 設計書やADR
- 実装済みのコード
- テストコード
- 他の機能への波及

### 2. Architect の関与

設計への影響がある場合は、Architect ロールで以下を実施:
- 設計変更の必要性評価
- 代替案の検討
- 変更の妥当性判断

### 3. ドキュメントの更新順序

トレーサビリティを保つため、以下の順序で更新:
1. 要件書の更新（変更理由を更新履歴に記録）
2. 設計書の更新（必要に応じてADRを追加）
3. 実装とテストの更新

### 4. トレーサビリティの確保

変更の追跡可能性を保つ:
- 要件書の更新履歴に変更理由を記録
- 重要な判断はADRとして記録
- コミットメッセージに関連する要件IDや設計書を記載

### 5. 影響確認のチェックリスト

変更時に以下を確認:
- [ ] 変更理由が明確か
- [ ] 影響を受ける既存機能を特定したか
- [ ] 関連するドキュメントをすべて更新したか
- [ ] テストケースを追加・修正したか
- [ ] 他の機能への波及を確認したか
- [ ] 受け入れ条件が更新されたか

## プロジェクト開始時のチェックリスト

新しい機能や大きな変更を始める際の確認事項:

- [ ] `docs/ai/common/project-context.md` を読んだ
- [ ] `docs/ai/common/working-agreement.md` を読んだ
- [ ] 担当ロールのドキュメントを読んだ
- [ ] 既存の関連要件や設計書を確認した
- [ ] 必要なテンプレートとチェックリストを把握した
- [ ] 不明点や未解決事項を明示した

## ロール間の連携

各ロールは独立しているが、以下のような連携が必要:

- **Architect → Implementer**: 設計の不明点があればフィードバック
- **Implementer → Tester**: 実装の意図とテスト観点を共有
- **Tester → Reviewer**: テスト結果とカバレッジ情報を提供
- **Reviewer → Architect**: 設計の見直しが必要な場合はエスカレーション

## 参考: ドキュメント配置ルール

- **要件書**: `docs/design/requirements/`
- **設計書**: `docs/design/`
- **ADR**: `docs/design/adr/`
- **AI向けガイド**: `docs/ai/`（プロジェクト固有の内容は含めない）
