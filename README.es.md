# SiliconSoul

Idiomas:

- 简体中文 (Predeterminado): README.md
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

> Estado de actualización (2026-04-08): PRD Fase 1 (lote 8) añade operation receipts para quick-actions (estado/new request ID/duración), con filtro y exportación JSON/MD.

## Uso / Valor / Posicionamiento / Diferenciadores

SiliconSoul es un prototipo de producto de soporte a la decisión multi‑agente (MOE) para fundadores, operadores, inversores y CFO. Combina entradas de múltiples documentos (PDF/Excel/PPT/Word) con razonamiento paralelo de expertos para producir conclusiones con evidencia, una lista estructurada de faltantes y un historial reproducible.

### Valor

- Múltiples documentos → salidas reutilizables: conclusiones + evidencia + “qué pedir después”
- Análisis por sub‑negocio/sub‑producto con verificación explícita de alcance y asignaciones
- Flujo reproducible: history, replay, diff y exportación de informes

### Posicionamiento del producto

- Herramienta de análisis y revisión; no es un sistema contable ni reemplaza ERP/BI
- Útil para due diligence, revisión presupuestaria, análisis operativo, análisis por segmento e investigación de inversión

### Diferenciadores

- Carga por lotes + etiquetas de propósito (finanzas / ingresos por segmento / costos / asignaciones / KPIs / contratos y precios), evidencia agrupada por propósito
- Si falta información, devuelve needs_structured (checklist) con prioridades
- History del sitio principal soporta filtro CFO + replay/diff/descarga
- Seguridad estricta: nunca commitear tokens/claves/app id; ejecutar script de seguridad antes de push

Sistema de soporte a la decisión multi‑agente (MOE), que incluye:

- API backend en Python (aiohttp) + orquestación de expertos
- Sitio principal en React (Dashboard / Portfolio / KnowledgeBase / History)
- Página CFO en Streamlit (carga de múltiples documentos, análisis por sub‑negocio/sub‑producto, exportación de informe)

## Inicio rápido (Docker Compose)

```bash
docker compose up -d siliconsoul siliconsoul-web siliconsoul-cfo
```

- Web (React): normalmente http://localhost:3000
- API: normalmente http://localhost:8000/api
- CFO (Streamlit): http://localhost:8501 (se abre desde el sitio principal mediante enlace externo)

## Desarrollo local

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

## Configuración y secretos

Este repositorio NO debe contener tokens / claves privadas / app id. Usa variables de entorno o archivos de configuración locales.

- No commits: `.env*`, `data/`, `logs/`, `*.db`, `*.key`, `*.pem` (ignorados en .gitignore)
- Recomendado antes de push: `./scripts/security_check.sh`
- Ejemplo frontend: `frontend/.env.example`
- Variables comunes (solo nombres; nunca commits valores):
  - `TUSHARE_TOKEN`: token de Tushare
  - `SILICONSOUL_API_TOKENS`: mapeo de tokens de auth backend (para `/api/me`)
  - `REACT_APP_API_URL`: base url del API del sitio
  - `REACT_APP_CFO_URL`: url externa de la página CFO
  - `CFO_API_URL`: base url del API para la página CFO

## Documentación

- [Escenario CFO](docs/cfo.md)
- [Referencia API](docs/api.md)
- [Guía de desarrollo](docs/development.md)
