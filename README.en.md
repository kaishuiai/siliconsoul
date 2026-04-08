# SiliconSoul

Languages:

- 简体中文 (Default): README.md
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

> Update status (2026-04-08): PRD Phase 1 (batch 7) adds one-click execution for suggested actions (enhanced replay, conflict review, chain-summary copy).

## Purpose / Value / Positioning / Differentiators

SiliconSoul is a multi-agent (MOE) decision-support product prototype for founders, operators, investors, and CFOs. It combines multi-document inputs (PDF/Excel/PPT/Word) with parallel expert reasoning to produce evidence-backed conclusions, structured “what’s missing” lists, and replayable history.

### Value

- Multi-document input → reusable outputs: conclusions + evidence + what to request next
- Sub-business/sub-product analysis with explicit “scope” and allocation checks
- Replayable workflow: history, replay, diff, and report export

### Product Positioning

- An analysis & review tool, not an accounting system, and not a replacement for ERP/BI
- Useful for due diligence, budget reviews, operating analysis, segment analysis, and investment research

### Differentiators

- Batch upload with file purpose tags (financials / segment revenue / costs / allocations / KPIs / contracts & pricing), and evidence grouped by purpose
- If documents are insufficient, returns needs_structured (checklist) with priorities
- Main site History supports CFO filtering + replay/diff/download workflows
- Strong security posture: never commit tokens/private keys/app ids; run a security check before pushing

A multi-agent (MOE) decision support system, including:

- Python backend API (aiohttp) + expert orchestration
- React main site (Dashboard / Portfolio / KnowledgeBase / History)
- Streamlit CFO page (multi-document upload, sub-business/sub-product analysis, report export)

## Quick Start (Docker Compose)

```bash
docker compose up -d siliconsoul siliconsoul-web siliconsoul-cfo
```

- Web (React): typically http://localhost:3000
- API: typically http://localhost:8000/api
- CFO (Streamlit): http://localhost:8501 (opened from the main site via an external link)

## Local Development

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Configuration & Secrets

This repository must NOT contain any token / private key / app id. Inject them via environment variables or local config files.

- Do not commit: `.env*`, `data/`, `logs/`, `*.db`, `*.key`, `*.pem` (ignored by .gitignore)
- Recommended before pushing: `./scripts/security_check.sh`
- Frontend example: `frontend/.env.example`
- Common environment variables (names only, never commit values):
  - `TUSHARE_TOKEN`: Tushare API token
  - `SILICONSOUL_API_TOKENS`: backend auth token mapping (for `/api/me` and protected access)
  - `REACT_APP_API_URL`: main site API base url
  - `REACT_APP_CFO_URL`: main site external CFO page url
  - `CFO_API_URL`: CFO page backend API base url

## Docs

- [CFO scenario](docs/cfo.md)
- [API reference](docs/api.md)
- [Development guide](docs/development.md)
