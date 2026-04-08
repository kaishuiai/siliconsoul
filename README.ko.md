# SiliconSoul

언어 / Languages:

- 简体中文 (기본): README.md
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

> 업데이트 상태(2026-04-08): PRD Phase 1(1차 배치)에서 replay 체인 추적(`replay_of`)과 History replay 필터를 추가해 복기 루프를 강화했습니다.

## 용도 / 가치 / 포지셔닝 / 차별점

SiliconSoul은 창업자, 운영자, 투자자, CFO를 위한 다중 에이전트(MOE) 의사결정 지원 제품 프로토타입입니다. 여러 문서(PDF/Excel/PPT/Word)를 입력으로 받아, 여러 전문가 에이전트가 병렬 추론하여 근거 기반 결론, 구조화된 “추가로 필요한 자료” 목록, 재현 가능한 히스토리를 제공합니다.

### 가치

- 다문서 입력 → 재사용 가능한 산출물(결론 + 근거 + 다음에 무엇을 요청해야 하는지)
- 하위 사업/하위 제품 분석: 스코프 및 배분(allocations) 체크를 명시하고, 보완 자료를 우선순위로 제시
- 재현 가능한 워크플로우: History, Replay, Diff, 보고서 내보내기

### 제품 포지셔닝

- 분석 및 리뷰 도구이며, 회계 시스템이 아니고 ERP/BI를 대체하지 않습니다
- DD, 예산 리뷰, 운영 분석, 세그먼트 분석, 투자 리서치 보조에 적합

### 차별점

- 배치 업로드 + 문서 용도 태그(재무/세그먼트 매출/원가/배분/KPI/계약·가격), 근거를 용도별로 구성
- 자료가 부족하면 needs_structured(체크리스트)를 우선순위와 함께 반환
- 메인 사이트 History에서 CFO 필터 + replay/diff/download 지원
- 강한 보안: token/개인키/app id를 커밋하지 않음. push 전에 보안 검사 실행

다중 에이전트(MOE) 의사결정 지원 시스템으로, 다음을 포함합니다:

- Python 백엔드 API(aiohttp) + 전문가 오케스트레이션
- React 메인 사이트(Dashboard / Portfolio / KnowledgeBase / History)
- Streamlit CFO 페이지(다중 문서 업로드, 하위 사업/하위 제품 분석, 보고서 내보내기)

## 빠른 시작(Docker Compose)

```bash
docker compose up -d siliconsoul siliconsoul-web siliconsoul-cfo
```

- Web(React): 보통 http://localhost:3000
- API: 보통 http://localhost:8000/api
- CFO(Streamlit): http://localhost:8501 (메인 사이트에서 외부 링크로 새 창/탭 열림)

## 로컬 개발

### 백엔드

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

### 프론트엔드

```bash
cd frontend
npm install
npm start
```

## 설정 및 민감정보

이 저장소에는 token / 개인키 / app id 를 절대 커밋하지 않습니다. 환경 변수 또는 로컬 설정 파일로 주입하세요.

- 커밋 금지: `.env*`, `data/`, `logs/`, `*.db`, `*.key`, `*.pem` (.gitignore 에서 제외)
- push 전에 권장: `./scripts/security_check.sh`
- 프론트엔드 예시: `frontend/.env.example`
- 자주 쓰는 환경 변수(이름만, 값은 커밋 금지):
  - `TUSHARE_TOKEN`: Tushare 토큰
  - `SILICONSOUL_API_TOKENS`: 백엔드 인증 토큰 매핑(`/api/me` 등)
  - `REACT_APP_API_URL`: 메인 사이트 API base url
  - `REACT_APP_CFO_URL`: CFO 페이지 외부 링크 url
  - `CFO_API_URL`: CFO 페이지 API base url

## 문서

- [CFO 시나리오](docs/cfo.md)
- [API 문서](docs/api.md)
- [개발 가이드](docs/development.md)
