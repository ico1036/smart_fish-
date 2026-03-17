<div align="center">

# SMARTFISH

**군집 지능 엔진, 모든 것을 예측하다**

*문서를 올리면 세상이 만들어지고, 그 안의 에이전트를 인터뷰할 수 있습니다.*

[![GitHub Stars](https://img.shields.io/github/stars/ico1036/smart_fish-?style=flat-square&color=DAA520)](https://github.com/ico1036/smart_fish-/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/ico1036/smart_fish-?style=flat-square)](https://github.com/ico1036/smart_fish-/network)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Vue 3](https://img.shields.io/badge/Vue-3-4FC08D?style=flat-square&logo=vuedotjs&logoColor=white)](https://vuejs.org)
[![Claude API](https://img.shields.io/badge/Claude-Anthropic-CC785C?style=flat-square&logo=anthropic&logoColor=white)](https://anthropic.com)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue?style=flat-square)](LICENSE)

[English](./README.md) | [한국어](./README-KR.md)

</div>

---

## 개요

**SmartFish**는 멀티에이전트 군집지능 시뮬레이터입니다. 아무 문서나 넣으면:

1. **지식그래프를 자동 추출**합니다 (인물, 조직, 개념 + 관계)
2. **각 엔티티를 AI 에이전트로** 살려냅니다 (고유한 성격, 직업, MBTI)
3. **가상 소셜미디어에서 시뮬레이션**합니다 (트위터/레딧)
4. **예측 보고서를 생성**합니다 (행동분석, 여론흐름, 패턴)
5. **에이전트를 직접 인터뷰**할 수 있습니다 ("왜 그 글에 반대했어?")

> **입력**: 문서 + 시뮬레이션 요구사항 (자연어)
>
> **출력**: 예측 보고서 + 탐색 가능한 디지털 평행세계

### 누구를 위한 도구인가?

- **의사결정자**: 정책, PR, 공시 발표 전에 제로 리스크로 여론 리허설
- **연구자**: 사회적 행동, 여론 전파, 집단역학 관찰
- **누구나**: "만약 ~하면?" 에 대한 답을 얻을 수 있는 창의적 샌드박스

---

## 작동 원리

```
문서 업로드 ──→ 지식그래프 ──→ AI 에이전트 프로필 ──→ 소셜미디어 시뮬레이션 ──→ 분석 보고서
(PDF/MD/TXT)    (자동 추출)     (LLM 생성)           (트위터/레딧)              (인터뷰 포함)
```

### 5단계 워크플로우

| 단계 | 무엇이 일어나는가 | 화면에 보이는 것 |
|:----:|-----------------|----------------|
| **01** | **그래프 빌드** — Claude가 문서를 분석, 엔티티와 관계 추출 | D3 인터랙티브 그래프 (노드 클릭 가능) |
| **02** | **환경 설정** — 각 엔티티가 고유한 성격의 AI 에이전트로 변환 | 에이전트 프로필 카드 |
| **03** | **시뮬레이션 실행** — 에이전트들이 자율적으로 포스팅, 좋아요, 댓글, 리트윗 | WebSocket 실시간 액티비티 피드 |
| **04** | **보고서 생성** — Claude가 모든 행동과 패턴을 분석 | 6개 섹션 구조화 보고서 |
| **05** | **딥 인터랙션** — 보고서 에이전트에게 질문하거나 개별 에이전트를 인캐릭터 인터뷰 | 대화 인터페이스 |

---

## 빠른 시작

### 필요한 것

| 도구 | 버전 | 확인 방법 |
|------|------|----------|
| [Python](https://python.org) | 3.11+ | `python --version` |
| [uv](https://docs.astral.sh/uv/) | 최신 | `uv --version` |
| [Node.js](https://nodejs.org) | 18+ | `node --version` |
| [Anthropic API 키](https://console.anthropic.com/) | — | console.anthropic.com에서 발급 |

### 1. 클론 & 설정

```bash
git clone https://github.com/ico1036/smart_fish-.git
cd smart_fish-
cp .env.example .env
```

`.env` 파일을 열고 Anthropic API 키를 입력하세요:

```env
ANTHROPIC_API_KEY=sk-ant-api03-여기에-키-입력
```

### 2. 의존성 설치

```bash
# 백엔드 (Python)
uv sync

# 프론트엔드 (Node.js)
cd frontend && npm install && cd ..
```

### 3. 실행

```bash
# 터미널 1: 백엔드
uv run uvicorn backend.app.main:app --reload --port 5001

# 터미널 2: 프론트엔드
cd frontend && npm run dev
```

브라우저에서 **http://localhost:3000** 접속

### Docker 배포

```bash
cp .env.example .env
# .env에 ANTHROPIC_API_KEY 입력
docker compose up -d
```

**http://localhost:5001** 에서 접속

---

## 사용 가이드

### Step 1: 문서 업로드

1. http://localhost:3000 접속
2. PDF, Markdown, 또는 텍스트 파일을 드래그&드롭
3. 시뮬레이션 요구사항을 자연어로 입력:
   - *"이 회사가 구조조정을 발표한 후 여론이 어떻게 변하는지 시뮬레이션해줘"*
   - *"이 소설의 등장인물들이 소셜미디어에서 어떻게 반응할지 예측해줘"*
   - *"이 정책 제안에 대한 논쟁을 모델링해줘"*
4. **"Launch Engine →"** 클릭

### Step 2: 그래프 구축 관찰

- Claude가 문서를 분석하고 온톨로지(엔티티 타입 + 관계)를 설계
- 엔티티와 관계가 추출되어 인터랙티브 그래프로 시각화
- 아무 노드나 클릭하면 속성, 연결, 컨텍스트 확인 가능

### Step 3: 시뮬레이션 실행

- 그래프 엔티티에서 에이전트 프로필이 생성됨 (각각 고유한 성격)
- 시뮬레이션 라운드 수와 플랫폼 설정
- 에이전트들이 실시간으로 포스팅, 댓글, 좋아요, 논쟁하는 것을 관찰

### Step 4: 보고서 확인

- Claude가 시뮬레이션 데이터를 분석하고 구조화 보고서 생성
- 포함 내용: 요약, 행동 분석, 인터랙션 역학, 여론 흐름, 창발적 패턴, 예측

### Step 5: 에이전트 인터뷰

- 보고서 에이전트에게 질문: "가장 영향력 있는 에이전트는?"
- 개별 에이전트를 인캐릭터로 인터뷰:
  - *"왜 그 정책에 반대했어?"*
  - *"그 글을 리트윗한 이유가 뭐야?"*
  - AI가 아니라 시뮬레이션 속 인물로서 대답합니다

---

## 비용 안내

분석에는 Claude Sonnet, 시뮬레이션 에이전트에는 Claude Haiku를 사용하여 비용을 최적화합니다.

| 단계 | 모델 | 대략적 비용 |
|------|------|------------|
| 온톨로지 생성 | Sonnet | ~$0.05 |
| 그래프 빌드 | Sonnet | ~$0.10/청크 |
| 프로필 생성 | Sonnet | ~$0.03/에이전트 |
| 시뮬레이션 | **Haiku** | ~$0.005/에이전트/라운드 |
| 보고서 | Sonnet | ~$0.10 |
| 채팅/인터뷰 | Haiku | ~$0.002/질문 |

**예시**: 에이전트 10명, 5라운드 = **약 $1~2**

---

## 기술 스택

| 레이어 | 기술 |
|--------|-----|
| **LLM** | Anthropic Claude (Sonnet + Haiku) |
| **백엔드** | FastAPI (Python 3.11+) |
| **프론트엔드** | Vue 3 + Vite + D3.js |
| **지식그래프** | NetworkX |
| **시뮬레이션** | 커스텀 소셜미디어 엔진 |
| **실시간 통신** | WebSocket |
| **배포** | Docker Compose |

---

## 감사의 글

SmartFish는 [MiroFish](https://github.com/666ghj/MiroFish)를 기반으로 처음부터 새로 구현한 프로젝트입니다:
- **Anthropic Claude** (OpenAI 대체)
- **FastAPI** (Flask 대체)
- **NetworkX** (Zep Cloud 대체)
- **커스텀 시뮬레이션 엔진** (OASIS/CAMEL-AI 대체)

원본 MiroFish: [@666ghj](https://github.com/666ghj) — AGPL-3.0 라이선스.

---

## 라이선스

이 프로젝트는 [AGPL-3.0 라이선스](LICENSE)를 따릅니다.

---

<div align="center">

*미래를 에이전트 군집 속에서 리허설하고, 백전 후에 결정을 내리세요.*

**[시작하기](#빠른-시작)** · **[버그 제보](https://github.com/ico1036/smart_fish-/issues)** · **[기능 요청](https://github.com/ico1036/smart_fish-/issues)**

</div>
