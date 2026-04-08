# SiliconSoul

語言 / Languages：

- 簡體中文（預設）：README.md
- 簡體中文：README.zh-CN.md
- 繁體中文：README.zh-TW.md
- English：README.en.md
- Русский：README.ru.md
- Tiếng Việt：README.vi.md
- Français：README.fr.md
- Español：README.es.md
- Italiano：README.it.md
- 日本語：README.ja.md
- 한국어：README.ko.md
- ᠮᠠᠨᠵᡠ ᡤᡳᠰᡠᠨ（Manchu）：README.mnc.md
- ᠮᠣᠩᠭᠣᠯ ᠬᠡᠯᠡ（Mongolian, traditional script）：README.mn.md
- العربية：README.ar.md

> 更新狀態（2026-04-08）：PRD Phase 1（第七批）已上線建議動作快捷執行（重放增強專家/衝突複核/鏈路摘要複製），復盤由「建議」升級為「可一鍵執行」。

## 專案用途 / 價值 / 定位 / 差異點

SiliconSoul 是面向創辦人、經營管理者、投研與 CFO 的多智能體（MOE）決策支援產品原型：將業務/財務材料（PDF/Excel/PPT/Word）與多專家並行推理結合，輸出可追溯證據的結論、結構化缺口清單與可復盤歷史。

### 價值

- 多文件輸入 → 輸出可復用的「結論 + 依據 + 需要補什麼」
- 子業務/子產品口徑分析：可標註材料用途、強制口徑校驗、輸出可執行的補充清單
- 可復盤：歷史查詢、重放（replay）、對比（diff）、匯出報告

### 產品定位

- 這是「分析與復盤工具」，不是會計/記帳系統，也不取代 ERP/BI
- 適用：盡調、預算評審、經營分析、子業務拆分分析、投研決策輔助

### 差異點

- 多文件批次上傳 + 用途標籤（財報/分部收入/成本/分攤/經營指標/合約定價等），證據摘錄按用途組織
- 材料不足時輸出 needs_structured（可勾選 checklist），並按優先級列出補充材料
- 主站 History 支援 CFO 過濾與復盤流程（重放/對比/下載）
- 強安全約束：不提交任何 token/私鑰/app id；推送前可執行安全檢查腳本

多智能體（MOE）決策支援系統，包含：

- Python 後端 API（aiohttp）＋多專家編排
- React 主站（Dashboard / Portfolio / KnowledgeBase / History）
- Streamlit CFO 頁面（多文件上傳、子業務/子產品分析、報告匯出）

## 快速開始（Docker Compose）

```bash
docker compose up -d siliconsoul siliconsoul-web siliconsoul-cfo
```

- 主站（React）：通常是 http://localhost:3000
- 後端（API）：通常是 http://localhost:8000/api
- CFO 頁面（Streamlit）：http://localhost:8501（主站會以外連新開頁面）

## 本機開發

### 後端

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

### 前端

```bash
cd frontend
npm install
npm start
```

## 設定與敏感資訊

本倉庫不會提交任何 token／私鑰／app id。請透過環境變數或本機設定檔注入。

- 不要提交：`.env*`、`data/`、`logs/`、`*.db`、`*.key`、`*.pem`（已在 .gitignore 忽略）
- 推送前建議執行：`./scripts/security_check.sh`
- 前端設定樣例：`frontend/.env.example`
- 常用環境變數（僅示例名稱，值不要寫進倉庫）：
  - `TUSHARE_TOKEN`：Tushare 資料源 token
  - `SILICONSOUL_API_TOKENS`：後端鑑權 token 對映（用於 `/api/me` 與授權存取）
  - `REACT_APP_API_URL`：主站呼叫 API 的 base url
  - `REACT_APP_CFO_URL`：主站外連 CFO 頁面 url
  - `CFO_API_URL`：CFO 頁面呼叫後端 API 的 base url

## 文件

- [CFO 場景說明](docs/cfo.md)
- [API 說明](docs/api.md)
- [開發說明](docs/development.md)
