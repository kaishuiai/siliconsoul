# SiliconSoul

言語 / Languages:

- 简体中文（デフォルト）: README.md
- 简体中文: README.zh-CN.md
- 繁體中文: README.zh-TW.md
- English: README.en.md
- Русский: README.ru.md
- Tiếng Việt: README.vi.md
- Français: README.fr.md
- Español: README.es.md
- Italiano: README.it.md
- 日本語: README.ja.md
- 한국어: README.ko.md
- ᠮᠠᠨᠵᡠ ᡤᡳᠰᡠᠨ (Manchu): README.mnc.md
- ᠮᠣᠩᠭᠣᠯ ᠬᠡᠯᠡ (Mongolian, traditional script): README.mn.md
- العربية: README.ar.md

> 更新状況（2026-04-08）：PRD Phase 1（第9バッチ）でChatGPT風のマルチセッション対話ホーム（セッション管理/生成停止/再生成/疑似ストリーミング）を追加しました。

## 用途 / 価値 / 位置づけ / 差別化

SiliconSoul は、創業者・経営者・投資家・CFO 向けの多エージェント（MOE）意思決定支援プロダクトのプロトタイプです。複数ドキュメント（PDF/Excel/PPT/Word）を入力し、複数の専門家エージェントが並列推論して、根拠付きの結論、構造化された不足資料リスト、そして再現可能な履歴を出力します。

### 価値

- 複数ドキュメント入力 → 再利用できる出力（結論 + 根拠 + 次に必要なもの）
- サブ事業/サブ製品分析：スコープや配賦のチェックを明示し、補足資料の優先度を提示
- 再現可能なワークフロー：History / Replay / Diff / レポート出力

### プロダクトの位置づけ

- 分析とレビューのツールであり、会計ソフトではなく、ERP/BI の代替でもありません
- DD、予算レビュー、経営分析、セグメント分析、投資リサーチ支援に適用

### 差別化

- バッチアップロード + 用途タグ（財務/セグメント売上/コスト/配賦/KPI/契約・価格など）、根拠は用途別に整理
- 資料不足時は needs_structured（チェックリスト）を優先度付きで返却
- メインサイトの History で CFO フィルタ + replay/diff/download が可能
- 強いセキュリティ：token/秘密鍵/app id をコミットしない。push 前に安全チェックを実行

複数エージェント（MOE）による意思決定支援システム。主な構成：

- Python バックエンド API（aiohttp）＋専門家オーケストレーション
- React メインサイト（Dashboard / Portfolio / KnowledgeBase / History）
- Streamlit CFO ページ（複数ドキュメントのアップロード、サブ事業/サブ製品分析、レポート出力）

## クイックスタート（Docker Compose）

```bash
docker compose up -d siliconsoul siliconsoul-web siliconsoul-cfo
```

- Web（React）: 通常 http://localhost:3000
- API: 通常 http://localhost:8000/api
- CFO（Streamlit）: http://localhost:8501（メインサイトから外部リンクで新規タブ表示）

## ローカル開発

### バックエンド

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

### フロントエンド

```bash
cd frontend
npm install
npm start
```

## 設定と機密情報

このリポジトリには token / 秘密鍵 / app id を絶対にコミットしません。環境変数またはローカル設定ファイルで注入してください。

- コミット禁止: `.env*`、`data/`、`logs/`、`*.db`、`*.key`、`*.pem`（.gitignore で除外）
- push 前に推奨: `./scripts/security_check.sh`
- フロントエンド例: `frontend/.env.example`
- よく使う環境変数（名前のみ。値はコミットしない）:
  - `TUSHARE_TOKEN`: Tushare トークン
  - `SILICONSOUL_API_TOKENS`: バックエンド認証トークンのマッピング（`/api/me` など）
  - `REACT_APP_API_URL`: メインサイトの API base url
  - `REACT_APP_CFO_URL`: CFO ページ外部リンク url
  - `CFO_API_URL`: CFO ページの API base url

## ドキュメント

- [CFO シナリオ](docs/cfo.md)
- [API リファレンス](docs/api.md)
- [開発ガイド](docs/development.md)
