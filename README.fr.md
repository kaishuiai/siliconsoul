# SiliconSoul

Langues :

- 简体中文 (Par défaut) : README.md
- 简体中文 : README.zh-CN.md
- 繁體中文 : README.zh-TW.md
- English : README.en.md
- Русский : README.ru.md
- Tiếng Việt : README.vi.md
- Français : README.fr.md
- Español : README.es.md
- Italiano : README.it.md
- 日本語 : README.ja.md
- 한국어 : README.ko.md
- ᠮᠠᠨᠵᡠ ᡤᡳᠰᡠᠨ (Manchu) : README.mnc.md
- ᠮᠣᠩᠭᠣᠯ ᠬᠡᠯᠡ (Mongolian, traditional script) : README.mn.md
- العربية : README.ar.md

> Statut de mise à jour (2026-04-08) : PRD Phase 1 (lot 6) ajoute des explications de risque (`risk_reasons`) et des actions suggérées (`suggested_actions`).

## Usage / Valeur / Positionnement / Différences

SiliconSoul est un prototype de produit d’aide à la décision multi‑agents (MOE) pour fondateurs, opérateurs, investisseurs et CFO. Il combine des entrées multi‑documents (PDF/Excel/PPT/Word) avec un raisonnement parallèle d’experts afin de produire des conclusions avec preuves, une liste structurée des éléments manquants, et un historique rejouable.

### Valeur

- Entrées multi‑documents → sorties réutilisables : conclusions + preuves + “quoi demander ensuite”
- Analyse par sous‑activité/sous‑produit avec contrôle explicite du périmètre et des allocations
- Workflow rejouable : history, replay, diff et export de rapport

### Positionnement produit

- Outil d’analyse & de revue, pas un logiciel de comptabilité et ne remplace pas ERP/BI
- Utile pour due diligence, revues budgétaires, analyses opérationnelles, analyses par segment, recherche investissement

### Différences

- Upload batch + tags d’usage (financiers / revenus segment / coûts / allocations / KPIs / contrats & pricing), preuves groupées par usage
- Si les documents sont insuffisants : needs_structured (checklist) avec priorités
- Le site principal (History) supporte le filtrage CFO + replay/diff/téléchargement
- Sécurité stricte : aucun token/clé privée/app id dans Git ; exécuter le script de sécurité avant push

Système d’aide à la décision multi‑agents (MOE), comprenant :

- API backend Python (aiohttp) + orchestration d’experts
- Site principal React (Dashboard / Portfolio / KnowledgeBase / History)
- Page CFO Streamlit (téléversement multi‑documents, analyse par sous‑activité/sous‑produit, export de rapport)

## Démarrage rapide (Docker Compose)

```bash
docker compose up -d siliconsoul siliconsoul-web siliconsoul-cfo
```

- Web (React) : généralement http://localhost:3000
- API : généralement http://localhost:8000/api
- CFO (Streamlit) : http://localhost:8501 (ouvert depuis le site principal via un lien externe)

## Développement local

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

## Configuration & secrets

Ce dépôt ne doit PAS contenir de token / clé privée / app id. Utilisez des variables d’environnement ou des fichiers de config locaux.

- Ne pas commiter : `.env*`, `data/`, `logs/`, `*.db`, `*.key`, `*.pem` (ignorés via .gitignore)
- Recommandé avant push : `./scripts/security_check.sh`
- Exemple frontend : `frontend/.env.example`
- Variables fréquentes (noms uniquement, ne jamais commiter les valeurs) :
  - `TUSHARE_TOKEN` : token Tushare
  - `SILICONSOUL_API_TOKENS` : mapping de tokens d’auth backend (pour `/api/me`)
  - `REACT_APP_API_URL` : base url API du site
  - `REACT_APP_CFO_URL` : url externe de la page CFO
  - `CFO_API_URL` : base url API pour la page CFO

## Documentation

- [Scénario CFO](docs/cfo.md)
- [Référence API](docs/api.md)
- [Guide de développement](docs/development.md)
