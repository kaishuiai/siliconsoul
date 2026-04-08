# SiliconSoul

Lingue:

- 简体中文 (Predefinito): README.md
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

> Stato aggiornamento (2026-04-08): PRD Phase 1 (batch 7) aggiunge esecuzione one-click delle azioni suggerite (replay potenziato, review conflitti, copia summary chain).

## Scopo / Valore / Posizionamento / Differenziatori

SiliconSoul è un prototipo di prodotto di decision support multi‑agente (MOE) per founder, operatori, investitori e CFO. Combina input multi‑documento (PDF/Excel/PPT/Word) con ragionamento parallelo di esperti per produrre conclusioni supportate da evidenze, una lista strutturata di “cosa manca” e uno storico riproducibile.

### Valore

- Multi‑documento → output riutilizzabile: conclusioni + evidenze + cosa richiedere dopo
- Analisi per sotto‑business/sotto‑prodotto con verifiche esplicite di perimetro e allocazioni
- Workflow riproducibile: history, replay, diff ed export report

### Posizionamento del prodotto

- Strumento di analisi e review; non è un sistema di contabilità e non sostituisce ERP/BI
- Utile per due diligence, review budget, analisi operativa, analisi per segmenti e supporto all’investment research

### Differenziatori

- Upload batch + tag di scopo (financials / ricavi per segmento / costi / allocazioni / KPI / contratti e pricing), evidenze raggruppate per scopo
- Se i documenti sono insufficienti: needs_structured (checklist) con priorità
- History nel sito principale con filtro CFO + replay/diff/download
- Sicurezza rigorosa: mai committare token/chiavi/app id; eseguire lo script di sicurezza prima del push

Sistema di supporto decisionale multi‑agente (MOE), che include:

- API backend Python (aiohttp) + orchestrazione degli esperti
- Sito principale React (Dashboard / Portfolio / KnowledgeBase / History)
- Pagina CFO Streamlit (upload multi‑documento, analisi per sotto‑business/sotto‑prodotto, esportazione report)

## Avvio rapido (Docker Compose)

```bash
docker compose up -d siliconsoul siliconsoul-web siliconsoul-cfo
```

- Web (React): di solito http://localhost:3000
- API: di solito http://localhost:8000/api
- CFO (Streamlit): http://localhost:8501 (aperto dal sito principale tramite link esterno)

## Sviluppo locale

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

## Configurazione e segreti

Questo repository NON deve contenere token / chiavi private / app id. Usa variabili d’ambiente o file di configurazione locali.

- Non committare: `.env*`, `data/`, `logs/`, `*.db`, `*.key`, `*.pem` (ignorati in .gitignore)
- Consigliato prima del push: `./scripts/security_check.sh`
- Esempio frontend: `frontend/.env.example`
- Variabili comuni (solo nomi; non committare mai i valori):
  - `TUSHARE_TOKEN`: token Tushare
  - `SILICONSOUL_API_TOKENS`: mapping token auth backend (per `/api/me`)
  - `REACT_APP_API_URL`: base url API del sito
  - `REACT_APP_CFO_URL`: url esterno della pagina CFO
  - `CFO_API_URL`: base url API per la pagina CFO

## Documentazione

- [Scenario CFO](docs/cfo.md)
- [Riferimento API](docs/api.md)
- [Guida sviluppo](docs/development.md)
