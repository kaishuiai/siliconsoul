# ᠰᡳᠯᡳᠴᠣᠨᠰᠣᡠᠯ (SiliconSoul)

ᠮᠠᠨᠵᡠ ᡤᡳᠰᡠᠨ ᡩᡝ ᡩᡝᠷᡤᡳ ᡳᠰᡝᠮᡝ (Manchu, Unicode script):

- Default (简体中文): README.md
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
- Manchu: README.mnc.md
- Mongolian (traditional script): README.mn.md
- العربية: README.ar.md

> Update status (2026-04-08): PRD Phase 1 (batch 10) adds server-side streaming chat API, cloud session sync, and session search.

ᠠᠮᠪᠠ ᠰᡝᡳᠴᡝᠨ:

SiliconSoul ᠪᡝ ᠵᡝᠨᠵᡠᡝᠯᡝᠮᡝ ᡩᡝ ᠠᠷᡤᠠᠨ ᠪᡝ ᠵᡝᠪᠰᡝᠮᡝ ᠨᡳᠶᠠᠯᠮᠠ ᠮᡠᠰᡝ ᠠᠪᡥᠠᠮᠪᡳ (multi-agent / MOE) ᠠᠯᡳᠨ ᡩᡝ ᡳᡵᡤᡝᠪᡝ ᠪᡝ ᠠᠯᡳᠪᡳ ᡳᠰᡝᠮᡝ ᠪᡝ ᡩᡝᠷᡤᡳ ᡩᡝ ᠪᡝᠰᡝᠮᡝ ᡩᡝ ᡩᡝᠷᡤᡳ ᡳᠰᡝᠮᡝ.

Romanization (draft): SiliconSoul be multi-agent (MOE) decision-support niyalma muse ahambi. (Native-speaker review recommended.)

## Purpose / Value / Positioning / Differentiators (English)

SiliconSoul is a multi-agent (MOE) decision-support product prototype for founders, operators, investors, and CFOs. It ingests multi-document materials (PDF/Excel/PPT/Word) and produces evidence-backed conclusions, structured missing-material checklists, and replayable history.

## Quick Start (Docker Compose)

```bash
docker compose up -d siliconsoul siliconsoul-web siliconsoul-cfo
```

## Configuration & Secrets

Do not commit tokens / private keys / app ids. Use environment variables or local config files.

- Do not commit: `.env*`, `data/`, `logs/`, `*.db`, `*.key`, `*.pem`
- Recommended before push: `./scripts/security_check.sh`
