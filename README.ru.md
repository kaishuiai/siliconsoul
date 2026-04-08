# SiliconSoul

Языки:

- 简体中文 (по умолчанию): README.md
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

> Статус обновления (2026-04-08): PRD Phase 1 (пакет 7) добавляет one-click выполнение рекомендованных действий (усиленный replay, разбор конфликтов, копия summary цепочки).

## Назначение / Ценность / Позиционирование / Отличия

SiliconSoul — прототип продукта поддержки принятия решений на базе multi‑agent (MOE) для фаундеров, операционных руководителей, инвесторов и CFO. Система объединяет ввод нескольких документов (PDF/Excel/PPT/Word) и параллельное рассуждение “экспертов”, чтобы выдавать выводы с доказательствами, структурированный список недостающих материалов и историю, которую можно воспроизводить для ревью.

### Ценность

- Мульти‑документы → переиспользуемые результаты: выводы + доказательства + что запросить дальше
- Анализ по суб‑бизнесу/суб‑продукту с явной проверкой “скоупа” и правил аллокации
- Воспроизводимый workflow: History, Replay, Diff и экспорт отчёта

### Позиционирование продукта

- Инструмент анализа и ревью; не бухгалтерия и не замена ERP/BI
- Полезно для due diligence, бюджетных ревью, операционного анализа, сегментного анализа и инвестиционных исследований

### Отличия

- Пакетная загрузка + теги назначения файла (финансы / выручка по сегменту / затраты / аллокации / KPI / контракты и прайсинг), доказательства группируются по назначению
- При недостатке данных возвращает needs_structured (чек‑лист) с приоритетами
- History на главном сайте поддерживает фильтр CFO + replay/diff/download
- Жёсткая безопасность: никогда не коммитить токены/приватные ключи/app id; запускать проверку безопасности перед push

## Быстрый старт (Docker Compose)

```bash
docker compose up -d siliconsoul siliconsoul-web siliconsoul-cfo
```

- Web (React): обычно http://localhost:3000
- API: обычно http://localhost:8000/api
- CFO (Streamlit): http://localhost:8501 (открывается из главного сайта внешней ссылкой)

## Локальная разработка

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

## Конфигурация и секреты

Репозиторий НЕ должен содержать token / private key / app id. Используйте переменные окружения или локальные конфиги.

- Не коммитить: `.env*`, `data/`, `logs/`, `*.db`, `*.key`, `*.pem` (игнорируются .gitignore)
- Рекомендуется перед push: `./scripts/security_check.sh`
- Пример для фронтенда: `frontend/.env.example`
- Частые переменные окружения (только имена; значения не коммитить):
  - `TUSHARE_TOKEN`
  - `SILICONSOUL_API_TOKENS`
  - `REACT_APP_API_URL`
  - `REACT_APP_CFO_URL`
  - `CFO_API_URL`

## Документация

- [CFO сценарий](docs/cfo.md)
- [API документация](docs/api.md)
- [Гайд по разработке](docs/development.md)
