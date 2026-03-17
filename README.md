<div align="center">

# SMARTFISH

**군집 지능 엔진, 모든 것을 예측하다**</br>
*Swarm Intelligence Engine, Predicting Anything*

*문서를 올리면 세상이 만들어지고, 그 안의 에이전트를 인터뷰할 수 있습니다.*</br>
*Upload a document. Watch a world come alive. Interview the agents inside.*

[![GitHub Stars](https://img.shields.io/github/stars/ico1036/smart_fish-?style=flat-square&color=DAA520)](https://github.com/ico1036/smart_fish-/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/ico1036/smart_fish-?style=flat-square)](https://github.com/ico1036/smart_fish-/network)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Vue 3](https://img.shields.io/badge/Vue-3-4FC08D?style=flat-square&logo=vuedotjs&logoColor=white)](https://vuejs.org)
[![Claude API](https://img.shields.io/badge/Claude-Anthropic-CC785C?style=flat-square&logo=anthropic&logoColor=white)](https://anthropic.com)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue?style=flat-square)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Build-2496ED?style=flat-square&logo=docker&logoColor=white)](https://hub.docker.com/)

[English](./README-EN.md) | [한국어](./README.md)

</div>

---

## 개요 / Overview

**SmartFish**는 멀티에이전트 군집지능 시뮬레이터입니다. 아무 문서나 넣으면:

**SmartFish** is a multi-agent swarm intelligence simulator. Give it any document and it will:

1. **지식그래프 자동 추출** — 인물, 조직, 개념 간 관계를 파악합니다
2. **AI 에이전트로 변환** — 각 엔티티가 고유한 성격을 가진 에이전트로 살아납니다
3. **소셜미디어 시뮬레이션** — 가상 트위터/레딧에서 포스팅, 좋아요, 댓글, 논쟁합니다
4. **예측 보고서 생성** — Claude가 시뮬레이션 결과를 분석합니다
5. **에이전트 인터뷰** — "왜 그 글에 반대했어?" → 인캐릭터 응답

---

1. **Extract a knowledge graph** of entities and relationships
2. **Bring them to life** as AI agents with distinct personalities
3. **Simulate their interactions** on virtual social media (Twitter/Reddit)
4. **Generate a prediction report** analyzing what happened
5. **Let you interview any agent** about their motivations

> **입력**: 문서 + 시뮬레이션 요구사항 (자연어)</br>
> **출력**: 예측 보고서 + 탐색 가능한 디지털 평행세계
>
> **Input**: A document + what you want to simulate (plain language)</br>
> **Output**: A prediction report + a fully interactive digital parallel world

### 누구를 위한 도구인가? / Who is this for?

- **의사결정자 / Decision-makers**: 정책, PR 발표 전 제로 리스크 여론 리허설 / Zero-risk rehearsal for policies and announcements
- **연구자 / Researchers**: 사회적 행동, 여론 전파, 집단역학 관찰 / Observe emergent social behaviors and group dynamics
- **누구나 / Everyone**: "만약 ~하면?" 에 답하는 창의적 샌드박스 / A sandbox where every "what if" gets an answer

---

## 작동 원리 / How It Works

```
문서 업로드 ──→ 지식그래프 ──→ AI 에이전트 ──→ 소셜미디어 시뮬 ──→ 분석 보고서
Document       Knowledge      AI Agent        Social Media       Analysis
Upload         Graph          Profiles        Simulation         Report
(PDF/MD/TXT)   (auto-extract) (LLM-generated) (Twitter/Reddit)   (with interviews)
```

### 5단계 워크플로우 / 5-Step Workflow

| 단계 | 무엇이 일어나는가 / What Happens | 화면에 보이는 것 / What You See |
|:----:|-------------------------------|-------------------------------|
| **01** | **그래프 빌드** — Claude가 문서에서 엔티티와 관계를 추출 | D3 인터랙티브 그래프 (노드 클릭 가능) |
| **02** | **환경 설정** — 각 엔티티가 고유 성격의 AI 에이전트로 변환 | 에이전트 프로필 카드 |
| **03** | **시뮬레이션** — 에이전트들이 자율적으로 포스팅, 좋아요, 댓글 | WebSocket 실시간 피드 |
| **04** | **보고서 생성** — Claude가 행동과 패턴을 분석 | 6개 섹션 구조화 보고서 |
| **05** | **딥 인터랙션** — 보고서 Q&A + 에이전트 인캐릭터 인터뷰 | 대화 인터페이스 |

---

## 빠른 시작 / Quick Start

### 필요한 것 / Prerequisites

| 도구 | 버전 | 확인 |
|------|------|------|
| [Python](https://python.org) | 3.11+ | `python --version` |
| [uv](https://docs.astral.sh/uv/) | 최신 / latest | `uv --version` |
| [Node.js](https://nodejs.org) | 18+ | `node --version` |
| [Anthropic API Key](https://console.anthropic.com/) | — | console.anthropic.com 에서 발급 |

### 1. 클론 & 설정 / Clone & Configure

```bash
git clone https://github.com/ico1036/smart_fish-.git
cd smart_fish-
cp .env.example .env
```

`.env` 파일을 열고 API 키 입력 / Open `.env` and add your API key:

```env
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

### 2. 설치 / Install

```bash
# 백엔드 / Backend
uv sync

# 프론트엔드 / Frontend
cd frontend && npm install && cd ..
```

### 3. 실행 / Run

```bash
# 터미널 1: 백엔드
uv run uvicorn backend.app.main:app --reload --port 5001

# 터미널 2: 프론트엔드
cd frontend && npm run dev
```

**http://localhost:3000** 접속

### Docker

```bash
cp .env.example .env
# .env에 ANTHROPIC_API_KEY 입력
docker compose up -d
# http://localhost:5001 접속
```

---

## 사용 가이드 / Usage Guide

### Step 1: 문서 업로드

1. http://localhost:3000 접속
2. PDF, MD, TXT 파일을 드래그&드롭
3. 시뮬레이션 요구사항을 자연어로 입력:
   - *"이 회사의 구조조정 발표 후 여론 변화를 시뮬레이션해줘"*
   - *"이 소설 등장인물들이 소셜미디어에서 어떻게 반응할지 예측해줘"*
   - *"Simulate how public opinion evolves after this company announces layoffs"*
4. **"Launch Engine →"** 클릭

### Step 2: 그래프 빌드

- Claude가 문서를 분석하고 온톨로지(엔티티 타입 + 관계) 설계
- 엔티티와 관계가 인터랙티브 그래프로 시각화
- 노드 클릭 → 속성, 연결, 컨텍스트 확인

### Step 3: 시뮬레이션

- 그래프 엔티티에서 에이전트 프로필 자동 생성 (고유 성격)
- 라운드 수, 플랫폼 설정
- 에이전트들이 실시간으로 포스팅, 댓글, 좋아요, 논쟁

### Step 4: 보고서

- 요약, 행동 분석, 인터랙션 역학, 여론 흐름, 창발적 패턴, 예측

### Step 5: 인터뷰

- 보고서 에이전트에게: *"가장 영향력 있는 에이전트는?"*
- 개별 에이전트에게: *"왜 그 정책에 반대했어?"* → 시뮬레이션 속 인물로서 대답

---

## 비용 / Cost

| 단계 | 모델 | 비용 |
|------|------|------|
| 온톨로지 생성 | Sonnet | ~$0.05 |
| 그래프 빌드 | Sonnet | ~$0.10/청크 |
| 프로필 생성 | Sonnet | ~$0.03/에이전트 |
| 시뮬레이션 | **Haiku** | ~$0.005/에이전트/라운드 |
| 보고서 | Sonnet | ~$0.10 |
| 채팅/인터뷰 | Haiku | ~$0.002/질문 |

**예시**: 에이전트 10명 x 5라운드 = **약 $1~2**

---

## 기술 스택 / Tech Stack

| 레이어 | 기술 |
|--------|-----|
| **LLM** | Anthropic Claude (Sonnet + Haiku) |
| **백엔드** | FastAPI (Python 3.11+) |
| **프론트엔드** | Vue 3 + Vite + D3.js |
| **지식그래프** | NetworkX |
| **시뮬레이션** | Custom Social Media Engine |
| **실시간** | WebSocket |
| **배포** | Docker Compose |

---

## 프로젝트 구조 / Project Structure

```
smart_fish-/
├── backend/
│   ├── app/
│   │   ├── agents/          # 에이전트 정의 (ontology, graph, sim, report, interview)
│   │   ├── api/             # FastAPI 라우터 (project, graph, simulation, report)
│   │   ├── models/          # Pydantic 데이터 모델
│   │   ├── services/        # 핵심 서비스 (LLM, ontology, graph builder, sim runner, report)
│   │   ├── tools/           # 도구 래퍼 (file, graph, sim, report)
│   │   └── utils/           # 유틸리티 (파일 파서, 텍스트 처리, LLM 클라이언트)
│   └── tests/               # 120개 테스트
├── frontend/
│   ├── src/
│   │   ├── views/           # 9개 페이지 뷰
│   │   ├── components/      # 7개 컴포넌트 (GraphPanel, Step1-5, HistoryDB)
│   │   └── api/             # API 클라이언트
├── pyproject.toml            # Python 의존성 (uv)
├── docker-compose.yml
└── Dockerfile
```

---

## API 레퍼런스 / API Reference

### Project
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/project/upload` | 파일 업로드 + 프로젝트 생성 |
| `GET` | `/api/project/list` | 프로젝트 목록 |
| `GET` | `/api/project/{id}` | 프로젝트 상세 |

### Graph
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/graph/ontology/generate` | 온톨로지 생성 |
| `POST` | `/api/graph/build` | 지식그래프 빌드 (비동기) |
| `GET` | `/api/graph/build/status?task_id=X` | 빌드 진행률 |
| `GET` | `/api/graph/{id}` | 그래프 데이터 |

### Simulation
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/simulation/create` | 시뮬레이션 생성 |
| `POST` | `/api/simulation/{id}/prepare` | 에이전트 프로필 생성 (비동기) |
| `WS` | `/api/simulation/{id}/stream` | WebSocket 실시간 시뮬레이션 |
| `GET` | `/api/simulation/history` | 시뮬레이션 히스토리 |

### Report
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/report/generate` | 보고서 생성 (비동기) |
| `GET` | `/api/report/{id}` | 보고서 내용 |
| `POST` | `/api/report/{id}/chat` | 보고서 에이전트 채팅 |
| `POST` | `/api/report/interview` | 에이전트 인터뷰 |

---

## 감사의 글 / Acknowledgments

SmartFish는 [MiroFish](https://github.com/666ghj/MiroFish)를 기반으로 처음부터 새로 구현했습니다:
- **Anthropic Claude** (OpenAI 대체)
- **FastAPI** (Flask 대체)
- **NetworkX** (Zep Cloud 대체)
- **커스텀 시뮬레이션 엔진** (OASIS/CAMEL-AI 대체)

원본: [@666ghj](https://github.com/666ghj) — AGPL-3.0

---

## 라이선스 / License

[AGPL-3.0](LICENSE)

---

<div align="center">

*미래를 에이전트 군집 속에서 리허설하고, 백전 후에 결정을 내리세요.*</br>
*Let the future rehearse in Agent swarms, let decisions prevail after a hundred battles.*

**[시작하기 / Get Started](#빠른-시작--quick-start)** · **[버그 제보 / Report Bug](https://github.com/ico1036/smart_fish-/issues)** · **[기능 요청 / Feature Request](https://github.com/ico1036/smart_fish-/issues)**

</div>
