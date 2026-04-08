# ᠰᠢᠯᠢᠺᠣᠨᠰᠣᠤᠯ (SiliconSoul)

ᠬᠡᠯᠡ / Languages:

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
- ᠮᠣᠩᠭᠣᠯ ᠬᠡᠯᠡ (traditional script): README.mn.md
- العربية: README.ar.md

> Update status (2026-04-08): PRD Phase 1 (batch 1) adds replay-chain tracing (`replay_of`) and replay filtering in History.

## ᠵᠣᠷᠢᠯᠭᠠ / ᠠᠴᠠ ᠲᠤᠰ / ᠪᠠᠢᠷᠢᠯᠠᠯ / ᠢᠯᠭᠠᠯᠲᠠ

ᠰᠢᠯᠢᠺᠣᠨᠰᠣᠤᠯ ᠪᠣᠯ ᠣᠯᠣᠨ ᠡᠵᠡᠨᠲ (MOE) ᠰᠢᠢᠳᠪᠡᠷ ᠳᠡᠮᠵᠢᠬᠦ ᠪᠦᠲᠦᠭᠡᠯᠳᠡᠬᠦᠨ ᠤ ᠲᠦᠷᠪᠡᠯ ᠵᠠᠭᠪᠠᠷ ᠪᠣᠯᠣᠨ᠎ᠠ. ᠣᠯᠣᠨ ᠪᠠᠷᠢᠮᠲᠠ (PDF/Excel/PPT/Word) ᠣᠷᠣᠯᠲ ᠪᠣᠯᠤᠨ᠎ᠠ ᠵᠣᠬᠢᠶᠠᠯᠳᠠᠢ ᠡᠰᠡᠯᠢ ᠡᠵᠡᠨᠲᠦᠳ ᠨᠢ ᠵᠡᠷᠭᠡ ᠵᠡᠷᠭᠡ ᠪᠡᠷ ᠪᠣᠳᠣᠵᠤ ᠨᠤᠲᠠᠭᠯᠠᠯᠲᠠᠢ ᠳᠦᠭᠨᠡᠯᠲ᠂ ᠳᠤᠲᠠᠭᠤᠷ ᠮᠠᠲᠧᠷᠢᠶᠠᠯ ᠵᠠᠭᠪᠠᠷᠯᠠᠯᠲ᠂ ᠪᠠ ᠳᠠᠬᠢᠨ ᠰᠡᠷᠭᠡᠭᠡᠬᠦ ᠲᠦᠦᠬᠢ ᠭᠠᠷᠭᠠᠨ᠎ᠠ.

(Тайлбар: Энэ файлд уламжлалт монгол бичгийн Unicode тэмдэгт ашигласан; GitHub дээр босоо бичвэрээр биш хэвтээ чиглэлээр харагдаж болно.)

## Quick Start (Docker Compose)

```bash
docker compose up -d siliconsoul siliconsoul-web siliconsoul-cfo
```

## Configuration & Secrets

- Do not commit: `.env*`, `data/`, `logs/`, `*.db`, `*.key`, `*.pem`
- Recommended before push: `./scripts/security_check.sh`
