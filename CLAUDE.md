# SmartFish - Project Guide

## What is SmartFish?

SmartFish는 **멀티에이전트 군집지능 시뮬레이터**다. 문서를 넣으면 그 안의 등장인물/조직이 AI 에이전트로 살아나서 가상 소셜미디어에서 자율적으로 행동하고, 결과를 분석하는 시스템.

**핵심 파이프라인**: 문서 → 지식그래프 → AI 에이전트 프로필 → 소셜미디어 시뮬레이션 → 예측 보고서 → 에이전트 인터뷰

원본 [MiroFish](https://github.com/666ghj/MiroFish)를 Anthropic Claude + FastAPI + NetworkX로 재구현한 프로젝트.

## Architecture

```
Frontend (Vue 3 + D3.js)  ←→  Backend (FastAPI)  ←→  Claude API (Anthropic)
     :3000                        :5001                 Sonnet + Haiku
```

### Backend Structure (`backend/app/`)

| 디렉토리 | 역할 |
|----------|------|
| `api/` | FastAPI 라우터 (project, graph, simulation, report) |
| `services/` | 핵심 비즈니스 로직 (ontology, graph_builder, profile_generator, simulation_runner, report_generator, chat_service) |
| `tools/` | 서비스 래퍼 함수 (file, graph, sim, report) |
| `agents/` | 에이전트 프롬프트 + 설정 (ontology, graph, sim, report, interview) |
| `models/` | Pydantic 데이터 모델 (project, graph, simulation, report) |
| `utils/` | 유틸리티 (llm_client, file_parser, text_processor) |

### Key Files

- `utils/llm_client.py` — Anthropic SDK 래퍼. `chat()`, `chat_json()`, system 메시지 분리 처리
- `services/ontology_service.py` — LLM으로 문서에서 온톨로지(엔티티/관계 타입) 생성
- `services/graph_builder.py` — LLM으로 텍스트 청크에서 엔티티/관계 자동 추출
- `services/graph_service.py` — NetworkX DiGraph 기반 그래프 CRUD + 검색
- `services/profile_generator.py` — 그래프 엔티티 → AI 에이전트 프로필 (성격, MBTI 등)
- `services/simulation_runner.py` — 라운드별 에이전트 의사결정 루프 (haiku 모델)
- `services/sim_engine.py` — 가상 소셜미디어 엔진 (포스트, 좋아요, 댓글, 리트윗)
- `services/report_generator.py` — 시뮬레이션 데이터 수집 → LLM 분석 보고서
- `services/chat_service.py` — 보고서 Q&A + 에이전트 인캐릭터 인터뷰

### Frontend Structure (`frontend/src/`)

- `views/HomeView.vue` — 랜딩 (히어로 + 업로드 + 히스토리)
- `views/MainView.vue` — 듀얼 패널 (그래프 + Step1/2 워크벤치)
- `components/GraphPanel.vue` — D3 포스 그래프 (1400줄, 핵심 시각화)
- `components/Step1-5` — 5단계 워크플로우 컴포넌트

## Development

### Setup
```bash
cp .env.example .env  # ANTHROPIC_API_KEY 입력
uv sync
cd frontend && npm install && cd ..
```

### Run
```bash
uv run uvicorn backend.app.main:app --reload --port 5001  # 백엔드
cd frontend && npm run dev                                  # 프론트
```

### Test
```bash
uv run pytest -v          # 120 tests
uv run ruff check backend/  # lint
```

### Key Commands
```bash
uv sync                     # Python 의존성 설치/업데이트
uv run pytest -v            # 전체 테스트
uv run pytest -k "test_name" # 특정 테스트
cd frontend && npm run build  # 프론트 빌드
```

## Conventions

- **Python**: FastAPI async endpoints, Pydantic models, type hints
- **테스트**: TDD 기반, `unittest.mock.patch`로 LLM 호출 모킹
- **LLM 호출**: 항상 `LLMClient` 래퍼를 통해 (`get_llm_client()` 또는 `get_fast_llm_client()`)
- **모델 사용**: 분석/생성 = Sonnet, 시뮬레이션 에이전트 = Haiku (비용 최적화)
- **비동기 작업**: `threading.Thread(daemon=True)` + 딕셔너리 기반 태스크 추적
- **프론트 API**: `frontend/src/api/` 모듈로 분리, axios 인스턴스 공유
- **커밋**: `feat:`, `fix:`, `docs:`, `refactor:` prefix 사용

## API Overview

| 기능 | Endpoint | 비동기? |
|------|----------|--------|
| 파일 업로드 | `POST /api/project/upload` | No |
| 온톨로지 생성 | `POST /api/graph/ontology/generate` | No |
| 그래프 빌드 | `POST /api/graph/build` | Yes (thread) |
| 시뮬레이션 준비 | `POST /api/simulation/{id}/prepare` | Yes (thread) |
| 시뮬레이션 실행 | `WS /api/simulation/{id}/stream` | Yes (WebSocket) |
| 보고서 생성 | `POST /api/report/generate` | Yes (thread) |
| 보고서 채팅 | `POST /api/report/{id}/chat` | No |
| 에이전트 인터뷰 | `POST /api/report/interview` | No |

## Gotchas

- GraphService와 SimEngine은 **인메모리** — 서버 재시작 시 그래프/시뮬레이션 데이터 소실
- Project/SimState/Report는 JSON 파일로 영속 (`backend/data/`)
- `chat_json()`은 시스템 메시지에 "JSON만 응답하라"를 자동 추가
- Anthropic SDK는 system을 messages 밖 별도 파라미터로 보냄 (OpenAI와 다름)
- 프론트 프록시: Vite가 `/api` → `localhost:5001`로 프록시
