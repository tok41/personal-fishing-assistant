# Agent Routing Guide

このリポジトリでは、役割ごとに分かれたエージェント運用を前提とします。AI 向けドキュメントを毎回すべて読むのではなく、担当ロールと作業内容に応じて必要なものだけを参照してください。

## 最初に必ず読む

- `docs/ai/common/project-context.md`
- `docs/ai/common/working-agreement.md`

## 担当ロールごとに読む

- Architect: `docs/ai/roles/architect.md`
- Implementer: `docs/ai/roles/implementer.md`
- Reviewer: `docs/ai/roles/reviewer.md`
- Tester: `docs/ai/roles/tester.md`

## 必要なときだけ読む

- 開発フロー確認: `docs/ai/guides/workflow.md`
- 要件定義: `docs/ai/templates/requirements-template.md`
- 要件レビュー: `docs/ai/checklists/requirements-review-checklist.md`
- 設計レビュー: `docs/ai/checklists/design-review-checklist.md`
- コードレビュー: `docs/ai/checklists/code-review-checklist.md`
- テストレビュー: `docs/ai/checklists/test-review-checklist.md`
- 設計書作成: `docs/ai/templates/design-template.md`
- ADR 作成: `docs/ai/templates/adr-template.md`

## 作業ルール

- 担当ロールは、原則としてユーザー指定を優先する。
- ユーザー指定がない場合、AI はロールを勝手に確定せず、作業内容に応じて暫定候補を示すか、必要に応じて確認する。
- 共通文書の確認や現状把握だけの段階では、特定ロールを名乗らなくてよい。
- まとまった作業に入るときは、自分の担当ロールを明示する。
- 重複したガイドを増やすより、既存ドキュメントの更新を優先する。
- 共通ルールは最小限に保ち、役割固有の内容は各ロールファイルに寄せる。
