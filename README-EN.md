<div align="center">

# SMARTFISH

**Swarm Intelligence Engine, Predicting Anything**

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

## Overview

**SmartFish** is a multi-agent swarm intelligence simulator. Give it any document — a news article, a policy draft, a novel chapter — and it will:

1. **Extract a knowledge graph** of entities and relationships
2. **Bring them to life** as AI agents with distinct personalities
3. **Simulate their interactions** on virtual social media (Twitter/Reddit)
4. **Generate a prediction report** analyzing what happened
5. **Let you interview any agent** about their motivations

> **Input**: A document + what you want to simulate (plain language)
>
> **Output**: A prediction report + a fully interactive digital parallel world

### Who is this for?

- **Decision-makers**: A zero-risk rehearsal lab — test policies, PR strategies, and announcements before they go live
- **Researchers**: Observe emergent social behaviors, opinion cascades, and group dynamics
- **Everyone**: A creative sandbox where every "what if" gets an answer

---

## How It Works

```
Document Upload ──→ Knowledge Graph ──→ AI Agent Profiles ──→ Social Media Simulation ──→ Analysis Report
   (PDF/MD/TXT)      (auto-extracted)    (LLM-generated)      (Twitter/Reddit)           (with interviews)
```

### 5-Step Workflow

| Step | What Happens | What You See |
|:----:|-------------|-------------|
| **01** | **Graph Build** — Claude analyzes your document, extracts entities (people, orgs, concepts) and their relationships | Interactive D3 force-directed graph with clickable nodes |
| **02** | **Environment Setup** — Each entity becomes an AI agent with a unique personality, profession, MBTI, and communication style | Agent profile cards with generated personas |
| **03** | **Run Simulation** — Agents autonomously post, like, reply, repost, and follow each other across simulated rounds | Real-time activity feed streaming via WebSocket |
| **04** | **Report Generation** — Claude analyzes all agent behaviors, interactions, and emergent patterns | 6-section structured analysis report |
| **05** | **Deep Interaction** — Chat with the report agent or interview any individual agent in character | Chat interface with conversation history |

---

## Quick Start

### Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| [Python](https://python.org) | 3.11+ | `python --version` |
| [uv](https://docs.astral.sh/uv/) | latest | `uv --version` |
| [Node.js](https://nodejs.org) | 18+ | `node --version` |
| [Anthropic API Key](https://console.anthropic.com/) | — | Sign up at console.anthropic.com |

### 1. Clone & Configure

```bash
git clone https://github.com/ico1036/smart_fish-.git
cd smart_fish-
cp .env.example .env
```

Open `.env` and add your Anthropic API key:

```env
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

### 2. Install Dependencies

```bash
# Backend (Python)
uv sync

# Frontend (Node.js)
cd frontend && npm install && cd ..
```

### 3. Run

```bash
# Terminal 1: Backend
uv run uvicorn backend.app.main:app --reload --port 5001

# Terminal 2: Frontend
cd frontend && npm run dev
```

Open **http://localhost:3000** in your browser.

### Docker Deployment

```bash
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
docker compose up -d
```

Access at **http://localhost:5001**

---

## Usage Guide

### Step 1: Upload Your Document

1. Open http://localhost:3000
2. Drag & drop a PDF, Markdown, or text file into the upload area
3. Write your simulation requirement in natural language:
   - *"Simulate how public opinion evolves after this company announces layoffs"*
   - *"Predict how characters in this novel would react on social media"*
   - *"Model the debate around this policy proposal"*
4. Click **"Launch Engine →"**

### Step 2: Watch the Graph Build

- Claude analyzes your document and designs an ontology (entity types + relationships)
- Entities and relationships are extracted and visualized as an interactive graph
- Click any node to see its properties, connections, and context

### Step 3: Run the Simulation

- Agent profiles are generated from graph entities (each with unique personality)
- Configure simulation rounds and platforms
- Watch agents interact in real-time — posting, replying, liking, debating

### Step 4: Read the Report

- Claude analyzes all simulation data and generates a structured report
- Covers: Executive Summary, Behavior Analysis, Interaction Dynamics, Opinion Flow, Emergent Patterns, Predictions

### Step 5: Interview Agents

- Ask the Report Agent questions about the findings
- Interview individual agents in character:
  - *"Why did you oppose the policy?"*
  - *"What made you repost that article?"*
  - They answer as their simulated persona, not as an AI

---

## Cost Estimate

SmartFish uses Claude Sonnet for analysis and Claude Haiku for simulation agents to optimize costs.

| Step | Model | Approx. Cost |
|------|-------|-------------|
| Ontology Generation | Sonnet | ~$0.05 |
| Graph Build | Sonnet | ~$0.10 per chunk |
| Profile Generation | Sonnet | ~$0.03 per agent |
| Simulation | **Haiku** | ~$0.005 per agent per round |
| Report | Sonnet | ~$0.10 |
| Chat / Interview | Haiku | ~$0.002 per question |

**Example**: 10 agents, 5 rounds = **~$1-2 total**

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Anthropic Claude (Sonnet + Haiku) |
| **Backend** | FastAPI (Python 3.11+) |
| **Frontend** | Vue 3 + Vite + D3.js |
| **Knowledge Graph** | NetworkX (in-memory) |
| **Simulation** | Custom social media engine |
| **Real-time** | WebSocket streaming |
| **Package Manager** | uv (Python) + npm (Node.js) |
| **Deployment** | Docker Compose |

---

## Project Structure

```
smart_fish-/
├── backend/
│   ├── app/
│   │   ├── agents/          # Agent definitions (ontology, graph, sim, report, interview)
│   │   ├── api/             # FastAPI routers (project, graph, simulation, report)
│   │   ├── models/          # Pydantic data models
│   │   ├── services/        # Core services (LLM, ontology, graph builder, sim runner, report)
│   │   ├── tools/           # Tool wrappers (file, graph, sim, report)
│   │   └── utils/           # Utilities (file parser, text processor, LLM client)
│   └── tests/               # 120 tests across all modules
├── frontend/
│   ├── src/
│   │   ├── views/           # 9 page views
│   │   ├── components/      # 7 components (GraphPanel, Step1-5, HistoryDB)
│   │   └── api/             # API client modules
├── pyproject.toml            # Python dependencies (uv)
├── docker-compose.yml
└── Dockerfile
```

---

## API Reference

### Project
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/project/upload` | Upload files and create project |
| `GET` | `/api/project/list` | List all projects |
| `GET` | `/api/project/{id}` | Get project details |

### Graph
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/graph/ontology/generate` | Generate ontology from documents |
| `POST` | `/api/graph/build` | Build knowledge graph (async) |
| `GET` | `/api/graph/build/status?task_id=X` | Check build progress |
| `GET` | `/api/graph/{id}` | Get graph nodes and edges |

### Simulation
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/simulation/create` | Create simulation instance |
| `POST` | `/api/simulation/{id}/prepare` | Generate agent profiles (async) |
| `WS` | `/api/simulation/{id}/stream` | WebSocket: real-time simulation |
| `GET` | `/api/simulation/history` | List simulation history |

### Report
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/report/generate` | Generate analysis report (async) |
| `GET` | `/api/report/{id}` | Get report content |
| `POST` | `/api/report/{id}/chat` | Chat with report agent |
| `POST` | `/api/report/interview` | Interview a simulation agent |

---

## Acknowledgments

SmartFish is a reimplementation of [MiroFish](https://github.com/666ghj/MiroFish), rebuilt from scratch with:
- **Anthropic Claude** instead of OpenAI
- **FastAPI** instead of Flask
- **NetworkX** instead of Zep Cloud
- **Custom simulation engine** instead of OASIS/CAMEL-AI

Original MiroFish by [@666ghj](https://github.com/666ghj) — licensed under AGPL-3.0.

---

## License

This project is licensed under the [AGPL-3.0 License](LICENSE). See [NOTICE.md](NOTICE.md) for attribution details.

---

<div align="center">

*Let the future rehearse in Agent swarms, let decisions prevail after a hundred battles.*

**[Get Started](#quick-start)** · **[Report Bug](https://github.com/ico1036/smart_fish-/issues)** · **[Request Feature](https://github.com/ico1036/smart_fish-/issues)**

</div>
