# SmartFish Phase 2: The Brain — LLM Integration

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire up the Anthropic SDK to make all 6 pipeline stages functional — ontology generation, graph building, profile generation, simulation execution, report generation, and agent interview/chat — achieving 100% feature parity with MiroFish.

**Architecture:** Use the `anthropic` Python SDK directly (like MiroFish uses `openai`). Create an `LLMClient` wrapper with `chat()` and `chat_json()` methods. Each service calls LLM via this client. Simulation agents use haiku for cost efficiency. Report uses ReACT pattern with tool calling parsed from text. All long-running tasks use FastAPI BackgroundTasks with progress tracking.

**Tech Stack:** `anthropic` Python SDK, FastAPI BackgroundTasks, existing NetworkX graph + SimEngine

---

## File Structure (New/Modified)

```
backend/app/
├── utils/
│   └── llm_client.py          [CREATE] Anthropic SDK wrapper
├── services/
│   ├── ontology_service.py     [CREATE] Ontology generation with LLM
│   ├── graph_builder.py        [CREATE] Auto entity/relationship extraction
│   ├── profile_generator.py    [CREATE] Agent profile generation from entities
│   ├── simulation_runner.py    [CREATE] Multi-agent simulation loop
│   ├── report_generator.py     [CREATE] ReACT-based report generation
│   └── chat_service.py         [CREATE] Report chat + agent interview
├── api/
│   ├── graph.py                [MODIFY] Wire ontology + graph build
│   ├── simulation.py           [MODIFY] Wire profile gen + sim runner
│   └── report.py               [MODIFY] Wire report gen + chat
├── config.py                   [MODIFY] Add report/sim config constants
└── tests/
    ├── test_services/
    │   ├── test_llm_client.py  [CREATE]
    │   ├── test_ontology.py    [CREATE]
    │   ├── test_graph_builder.py [CREATE]
    │   ├── test_profile_gen.py [CREATE]
    │   └── test_report_gen.py  [CREATE]
    └── test_api/
        ├── test_graph_api.py   [MODIFY] Add ontology/build tests
        └── test_simulation_api.py [MODIFY] Add prepare/run tests
```

---

## Chunk 1: LLM Client + Ontology Service (Tasks 1-3)

### Task 1: Add Anthropic SDK + LLM Client

**Files:**
- Modify: `pyproject.toml`
- Create: `backend/app/utils/llm_client.py`
- Create: `backend/tests/test_services/test_llm_client.py`

- [ ] **Step 1: Write test for LLM client**

```python
# backend/tests/test_services/test_llm_client.py
import pytest
from unittest.mock import patch, MagicMock
from app.utils.llm_client import LLMClient

def test_llm_client_init():
    client = LLMClient(api_key="test-key", model="claude-sonnet-4-5")
    assert client.model == "claude-sonnet-4-5"

def test_llm_client_default_model():
    client = LLMClient(api_key="test-key")
    assert "claude" in client.model

@patch("app.utils.llm_client.Anthropic")
def test_chat_returns_text(mock_anthropic):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hello world")]
    mock_anthropic.return_value.messages.create.return_value = mock_response

    client = LLMClient(api_key="test-key")
    result = client.chat(messages=[{"role": "user", "content": "Hi"}])
    assert result == "Hello world"

@patch("app.utils.llm_client.Anthropic")
def test_chat_strips_think_tags(mock_anthropic):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="<think>reasoning</think>The answer is 42")]
    mock_anthropic.return_value.messages.create.return_value = mock_response

    client = LLMClient(api_key="test-key")
    result = client.chat(messages=[{"role": "user", "content": "test"}])
    assert result == "The answer is 42"

@patch("app.utils.llm_client.Anthropic")
def test_chat_json_parses_response(mock_anthropic):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='```json\n{"key": "value"}\n```')]
    mock_anthropic.return_value.messages.create.return_value = mock_response

    client = LLMClient(api_key="test-key")
    result = client.chat_json(messages=[{"role": "user", "content": "test"}])
    assert result == {"key": "value"}

@patch("app.utils.llm_client.Anthropic")
def test_chat_json_handles_bare_json(mock_anthropic):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"items": [1, 2, 3]}')]
    mock_anthropic.return_value.messages.create.return_value = mock_response

    client = LLMClient(api_key="test-key")
    result = client.chat_json(messages=[{"role": "user", "content": "test"}])
    assert result == {"items": [1, 2, 3]}

@patch("app.utils.llm_client.Anthropic")
def test_chat_json_invalid_json_raises(mock_anthropic):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="not json at all")]
    mock_anthropic.return_value.messages.create.return_value = mock_response

    client = LLMClient(api_key="test-key")
    with pytest.raises(ValueError, match="invalid JSON"):
        client.chat_json(messages=[{"role": "user", "content": "test"}])

@patch("app.utils.llm_client.Anthropic")
def test_chat_separates_system_message(mock_anthropic):
    """Anthropic SDK requires system as separate param, not in messages."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="response")]
    mock_instance = mock_anthropic.return_value
    mock_instance.messages.create.return_value = mock_response

    client = LLMClient(api_key="test-key")
    client.chat(messages=[
        {"role": "system", "content": "You are helpful"},
        {"role": "user", "content": "Hi"},
    ])

    call_kwargs = mock_instance.messages.create.call_args[1]
    assert call_kwargs["system"] == "You are helpful"
    assert len(call_kwargs["messages"]) == 1
    assert call_kwargs["messages"][0]["role"] == "user"
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
cd /Users/ryan/SmartFish && uv run pytest backend/tests/test_services/test_llm_client.py -v
```

- [ ] **Step 3: Add anthropic to dependencies**

In `pyproject.toml`, add `"anthropic>=0.40.0"` to `dependencies` list. Then `uv sync`.

- [ ] **Step 4: Implement LLM client**

```python
# backend/app/utils/llm_client.py
"""LLM client wrapper for Anthropic Claude API."""

import json
import re
from anthropic import Anthropic
from ..config import settings


class LLMClient:
    """Unified LLM client using Anthropic SDK."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.CLAUDE_MODEL
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        self.client = Anthropic(api_key=self.api_key)

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Send chat request. Separates system message for Anthropic API."""
        system = None
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                user_messages.append(msg)

        kwargs = {
            "model": self.model,
            "messages": user_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)
        content = response.content[0].text
        # Strip <think> tags from reasoning models
        content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
        return content

    def chat_json(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> dict:
        """Send chat request and parse JSON response."""
        # Add JSON instruction to system message
        enhanced = []
        has_system = False
        for msg in messages:
            if msg["role"] == "system":
                enhanced.append({
                    "role": "system",
                    "content": msg["content"] + "\n\nYou MUST respond with ONLY valid JSON. No markdown fences, no explanation, just the JSON object.",
                })
                has_system = True
            else:
                enhanced.append(msg)
        if not has_system:
            enhanced.insert(0, {
                "role": "system",
                "content": "Respond with ONLY valid JSON. No markdown fences, no explanation.",
            })

        response = self.chat(messages=enhanced, temperature=temperature, max_tokens=max_tokens)

        # Clean markdown code fences
        cleaned = response.strip()
        cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\n?```\s*$', '', cleaned)
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            raise ValueError(f"LLM returned invalid JSON: {cleaned[:200]}")


def get_llm_client(model: str = None) -> LLMClient:
    """Factory for LLM client."""
    return LLMClient(model=model)


def get_fast_llm_client() -> LLMClient:
    """Get LLM client with fast/cheap model (haiku) for simulation agents."""
    return LLMClient(model=settings.CLAUDE_SIM_MODEL)
```

- [ ] **Step 5: Run test — expect PASS**

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat: add Anthropic LLM client with chat/chat_json methods"
```

---

### Task 2: Ontology Generation Service

**Files:**
- Create: `backend/app/services/ontology_service.py`
- Create: `backend/tests/test_services/test_ontology.py`

- [ ] **Step 1: Write test**

```python
# backend/tests/test_services/test_ontology.py
import pytest
from unittest.mock import patch, MagicMock
from app.services.ontology_service import OntologyService

MOCK_ONTOLOGY_RESPONSE = {
    "entity_types": [
        {"name": "Student", "description": "University student", "attributes": ["major", "year"]},
        {"name": "Professor", "description": "University professor", "attributes": ["department"]},
        {"name": "University", "description": "Educational institution", "attributes": ["location"]},
        {"name": "Course", "description": "Academic course", "attributes": ["subject"]},
        {"name": "Department", "description": "Academic department", "attributes": ["faculty"]},
        {"name": "ResearchGroup", "description": "Research team", "attributes": ["focus"]},
        {"name": "MediaOutlet", "description": "News/media org", "attributes": ["type"]},
        {"name": "GovernmentAgency", "description": "Government body", "attributes": ["level"]},
        {"name": "Person", "description": "Generic person", "attributes": ["role"]},
        {"name": "Organization", "description": "Generic org", "attributes": ["sector"]},
    ],
    "edge_types": [
        {"name": "ENROLLED_IN", "description": "Student enrolled in course", "source_types": ["Student"], "target_types": ["Course"]},
        {"name": "TEACHES", "description": "Professor teaches course", "source_types": ["Professor"], "target_types": ["Course"]},
        {"name": "BELONGS_TO", "description": "Belongs to department", "source_types": ["Professor", "Student"], "target_types": ["Department"]},
        {"name": "AFFILIATED_WITH", "description": "Affiliated with university", "source_types": ["Person"], "target_types": ["University"]},
        {"name": "COLLABORATES", "description": "Research collaboration", "source_types": ["Professor"], "target_types": ["Professor"]},
        {"name": "REPORTS_ON", "description": "Media reports on entity", "source_types": ["MediaOutlet"], "target_types": ["University", "Person"]},
    ],
    "analysis_summary": "Ontology designed for university ecosystem simulation."
}

@patch("app.services.ontology_service.get_llm_client")
def test_generate_ontology(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat_json.return_value = MOCK_ONTOLOGY_RESPONSE
    mock_get_client.return_value = mock_client

    service = OntologyService()
    result = service.generate("Simulate university opinion dynamics", "Professor Zhang teaches CS101...")
    assert len(result["entity_types"]) == 10
    assert result["entity_types"][-1]["name"] == "Organization"
    assert result["entity_types"][-2]["name"] == "Person"
    assert len(result["edge_types"]) >= 6
    assert "analysis_summary" in result

@patch("app.services.ontology_service.get_llm_client")
def test_validate_adds_fallback_types(mock_get_client):
    incomplete_response = {
        "entity_types": [
            {"name": "Student", "description": "A student", "attributes": []},
        ],
        "edge_types": [{"name": "KNOWS", "description": "Knows", "source_types": ["Student"], "target_types": ["Student"]}],
        "analysis_summary": "Test"
    }
    mock_client = MagicMock()
    mock_client.chat_json.return_value = incomplete_response
    mock_get_client.return_value = mock_client

    service = OntologyService()
    result = service.generate("Test", "Some text")
    # Should add Person and Organization fallbacks
    names = [et["name"] for et in result["entity_types"]]
    assert "Person" in names
    assert "Organization" in names

@patch("app.services.ontology_service.get_llm_client")
def test_ontology_truncates_long_text(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat_json.return_value = MOCK_ONTOLOGY_RESPONSE
    mock_get_client.return_value = mock_client

    service = OntologyService()
    long_text = "x" * 100000
    service.generate("Test", long_text)

    call_args = mock_client.chat_json.call_args[1]["messages"]
    user_msg = [m for m in call_args if m["role"] == "user"][0]["content"]
    assert len(user_msg) < 60000  # truncated
```

- [ ] **Step 2: Run test — expect FAIL**

- [ ] **Step 3: Implement ontology service**

```python
# backend/app/services/ontology_service.py
"""Ontology generation service using Claude LLM."""

from ..utils.llm_client import get_llm_client

MAX_TEXT_LENGTH = 50000

ONTOLOGY_SYSTEM_PROMPT = """You are a knowledge graph ontology design expert for social media opinion simulation.

Given document text and a simulation requirement, design an ontology:

1. Design exactly 10 entity types representing real-world social actors:
   - The LAST 2 MUST be fallback types: "Person" and "Organization"
   - Each type needs: name, description, 1-3 attribute names
   - Attributes CANNOT use reserved names: name, uuid, summary, created_at

2. Design 6-10 relationship/edge types:
   - Each needs: name, description, source_types, target_types

3. Write an analysis_summary explaining your design rationale.

Respond with ONLY this JSON structure:
{
  "entity_types": [{"name": "...", "description": "...", "attributes": ["attr1", "attr2"]}],
  "edge_types": [{"name": "...", "description": "...", "source_types": ["..."], "target_types": ["..."]}],
  "analysis_summary": "..."
}"""


class OntologyService:
    def __init__(self):
        self.llm = get_llm_client()

    def generate(self, simulation_requirement: str, document_text: str) -> dict:
        """Generate ontology from documents and simulation requirement."""
        # Truncate long text
        text = document_text[:MAX_TEXT_LENGTH] if len(document_text) > MAX_TEXT_LENGTH else document_text

        user_message = f"""## Simulation Requirement
{simulation_requirement}

## Document Content
{text}"""

        result = self.llm.chat_json(
            messages=[
                {"role": "system", "content": ONTOLOGY_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=4096,
        )

        return self._validate_and_fix(result)

    def _validate_and_fix(self, result: dict) -> dict:
        """Ensure ontology has required fallback types."""
        entity_types = result.get("entity_types", [])
        names = [et["name"] for et in entity_types]

        if "Person" not in names:
            entity_types.append({"name": "Person", "description": "Generic person entity", "attributes": ["role"]})
        if "Organization" not in names:
            entity_types.append({"name": "Organization", "description": "Generic organization entity", "attributes": ["sector"]})

        # Ensure Person and Organization are last
        person = next(et for et in entity_types if et["name"] == "Person")
        org = next(et for et in entity_types if et["name"] == "Organization")
        entity_types = [et for et in entity_types if et["name"] not in ("Person", "Organization")]
        entity_types.extend([person, org])

        result["entity_types"] = entity_types
        if "edge_types" not in result:
            result["edge_types"] = []
        if "analysis_summary" not in result:
            result["analysis_summary"] = ""
        return result
```

- [ ] **Step 4: Run test — expect PASS**

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: add ontology generation service with LLM"
```

---

### Task 3: Graph Builder Service (Auto Entity Extraction)

**Files:**
- Create: `backend/app/services/graph_builder.py`
- Create: `backend/tests/test_services/test_graph_builder.py`

- [ ] **Step 1: Write test**

```python
# backend/tests/test_services/test_graph_builder.py
import pytest
from unittest.mock import patch, MagicMock
from app.services.graph_builder import GraphBuilder
from app.services.graph_service import GraphService

MOCK_EXTRACTION = {
    "entities": [
        {"id": "alice", "name": "Alice", "type": "Student", "summary": "CS student at MIT", "attributes": {"major": "CS"}},
        {"id": "bob", "name": "Bob", "type": "Professor", "summary": "AI professor", "attributes": {"department": "CS"}},
    ],
    "relationships": [
        {"source": "alice", "target": "bob", "type": "STUDIES_UNDER", "attributes": {}},
    ]
}

@patch("app.services.graph_builder.get_llm_client")
def test_build_graph_from_chunks(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat_json.return_value = MOCK_EXTRACTION
    mock_get_client.return_value = mock_client

    graph_svc = GraphService()
    builder = GraphBuilder(graph_service=graph_svc)

    ontology = {
        "entity_types": [{"name": "Student", "description": "A student", "attributes": ["major"]}],
        "edge_types": [{"name": "STUDIES_UNDER", "description": "Studies under professor"}],
    }
    chunks = ["Alice is a CS student studying under Professor Bob at MIT."]

    graph_id = builder.build("test-graph", ontology, chunks)

    assert graph_id == "test-graph"
    nodes = graph_svc.get_nodes("test-graph")
    assert len(nodes) == 2
    edges = graph_svc.get_edges("test-graph")
    assert len(edges) == 1

@patch("app.services.graph_builder.get_llm_client")
def test_build_deduplicates_entities(mock_get_client):
    mock_client = MagicMock()
    # Same entity in two chunks
    mock_client.chat_json.side_effect = [
        {"entities": [{"id": "alice", "name": "Alice", "type": "Student", "summary": "CS student", "attributes": {}}], "relationships": []},
        {"entities": [{"id": "alice", "name": "Alice", "type": "Student", "summary": "CS student updated", "attributes": {}}], "relationships": []},
    ]
    mock_get_client.return_value = mock_client

    graph_svc = GraphService()
    builder = GraphBuilder(graph_service=graph_svc)
    builder.build("g1", {"entity_types": [], "edge_types": []}, ["chunk1", "chunk2"])

    nodes = graph_svc.get_nodes("g1")
    assert len(nodes) == 1  # deduplicated

@patch("app.services.graph_builder.get_llm_client")
def test_build_with_progress_callback(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat_json.return_value = {"entities": [], "relationships": []}
    mock_get_client.return_value = mock_client

    graph_svc = GraphService()
    builder = GraphBuilder(graph_service=graph_svc)

    progress_updates = []
    builder.build("g1", {"entity_types": [], "edge_types": []}, ["c1", "c2"],
                   on_progress=lambda p, m: progress_updates.append((p, m)))
    assert len(progress_updates) >= 2
```

- [ ] **Step 2: Run test — expect FAIL**

- [ ] **Step 3: Implement graph builder**

```python
# backend/app/services/graph_builder.py
"""Builds knowledge graph by extracting entities/relationships from text chunks using LLM."""

from typing import Callable
from ..utils.llm_client import get_llm_client
from .graph_service import GraphService

EXTRACTION_SYSTEM_PROMPT = """You are a knowledge graph entity extraction specialist.

Given an ontology definition and a text chunk, extract ALL entities and relationships.

Ontology entity types:
{entity_types}

Ontology edge types:
{edge_types}

Rules:
- Extract every entity and relationship mentioned in the text
- Use consistent IDs for the same real-world entity (lowercase, no spaces, e.g. "alice_chen")
- Each entity needs: id, name, type (must match ontology), summary, attributes
- Each relationship needs: source (entity id), target (entity id), type (must match ontology)

Respond with JSON:
{{
  "entities": [{{"id": "...", "name": "...", "type": "...", "summary": "...", "attributes": {{}}}}],
  "relationships": [{{"source": "...", "target": "...", "type": "...", "attributes": {{}}}}]
}}"""


class GraphBuilder:
    def __init__(self, graph_service: GraphService = None):
        self.graph_service = graph_service or GraphService()
        self.llm = get_llm_client()

    def build(
        self,
        graph_id: str,
        ontology: dict,
        chunks: list[str],
        on_progress: Callable = None,
    ) -> str:
        """Build graph from text chunks using ontology."""
        self.graph_service.create_graph(graph_id)

        entity_types_desc = "\n".join(
            f"- {et['name']}: {et.get('description', '')}" for et in ontology.get("entity_types", [])
        )
        edge_types_desc = "\n".join(
            f"- {et['name']}: {et.get('description', '')}" for et in ontology.get("edge_types", [])
        )

        system_prompt = EXTRACTION_SYSTEM_PROMPT.format(
            entity_types=entity_types_desc,
            edge_types=edge_types_desc,
        )

        seen_entities = set()

        for i, chunk in enumerate(chunks):
            if on_progress:
                on_progress(int((i / len(chunks)) * 100), f"Processing chunk {i+1}/{len(chunks)}")

            try:
                result = self.llm.chat_json(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Extract entities and relationships from:\n\n{chunk}"},
                    ],
                    temperature=0.3,
                    max_tokens=4096,
                )

                for entity in result.get("entities", []):
                    eid = entity["id"]
                    if eid not in seen_entities:
                        self.graph_service.add_node(
                            graph_id, eid, entity["name"],
                            labels=[entity.get("type", "Entity")],
                            attributes={**entity.get("attributes", {}), "summary": entity.get("summary", "")},
                        )
                        seen_entities.add(eid)

                for rel in result.get("relationships", []):
                    if rel["source"] in seen_entities and rel["target"] in seen_entities:
                        self.graph_service.add_edge(
                            graph_id, rel["source"], rel["target"],
                            rel.get("type", "RELATED"),
                            rel.get("attributes"),
                        )
            except Exception as e:
                if on_progress:
                    on_progress(int((i / len(chunks)) * 100), f"Error on chunk {i+1}: {str(e)[:100]}")

        if on_progress:
            on_progress(100, "Graph build complete")

        return graph_id
```

- [ ] **Step 4: Run test — expect PASS**

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: add graph builder with LLM entity/relationship extraction"
```

---

## Chunk 2: Profile Generator + Simulation Runner (Tasks 4-5)

### Task 4: Profile Generator Service

**Files:**
- Create: `backend/app/services/profile_generator.py`
- Create: `backend/tests/test_services/test_profile_gen.py`

- [ ] **Step 1: Write test**

```python
# backend/tests/test_services/test_profile_gen.py
import pytest
from unittest.mock import patch, MagicMock
from app.services.profile_generator import ProfileGenerator
from app.services.graph_service import GraphService

MOCK_PROFILE = {
    "bio": "AI researcher passionate about NLP",
    "persona": "Dr. Bob is a meticulous professor who values academic rigor...",
    "age": 45,
    "profession": "Professor",
    "mbti": "INTJ",
    "interested_topics": ["AI", "NLP", "education"],
}

@patch("app.services.profile_generator.get_llm_client")
def test_generate_profiles(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat_json.return_value = MOCK_PROFILE
    mock_get_client.return_value = mock_client

    graph_svc = GraphService()
    graph_svc.create_graph("g1")
    graph_svc.add_node("g1", "bob", "Bob", ["Professor"], {"summary": "AI professor at MIT"})
    graph_svc.add_node("g1", "alice", "Alice", ["Student"], {"summary": "CS student"})

    gen = ProfileGenerator(graph_service=graph_svc)
    profiles = gen.generate("g1", "Simulate university dynamics")

    assert len(profiles) == 2
    assert profiles[0].name in ("Bob", "Alice")
    assert profiles[0].persona != ""

@patch("app.services.profile_generator.get_llm_client")
def test_generate_profiles_by_type(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat_json.return_value = MOCK_PROFILE
    mock_get_client.return_value = mock_client

    graph_svc = GraphService()
    graph_svc.create_graph("g1")
    graph_svc.add_node("g1", "bob", "Bob", ["Professor"], {"summary": "Prof"})
    graph_svc.add_node("g1", "alice", "Alice", ["Student"], {"summary": "Student"})

    gen = ProfileGenerator(graph_service=graph_svc)
    profiles = gen.generate("g1", "Test", entity_types=["Professor"])

    assert len(profiles) == 1
    assert profiles[0].name == "Bob"
```

- [ ] **Step 2: Run test — expect FAIL**

- [ ] **Step 3: Implement**

```python
# backend/app/services/profile_generator.py
"""Generate agent profiles from knowledge graph entities using LLM."""

from ..utils.llm_client import get_llm_client
from ..models.simulation import AgentProfile
from .graph_service import GraphService

PROFILE_SYSTEM_PROMPT = """You are an expert at creating detailed character profiles for social media simulation.

Given an entity from a knowledge graph, generate a realistic persona for a social media agent.

Respond with JSON:
{
  "bio": "Short bio (max 160 chars)",
  "persona": "Detailed personality description (500+ chars) including communication style, values, opinions",
  "age": 30,
  "profession": "Their profession",
  "mbti": "XXXX",
  "interested_topics": ["topic1", "topic2", "topic3"]
}"""


class ProfileGenerator:
    def __init__(self, graph_service: GraphService = None):
        self.graph_service = graph_service or GraphService()
        self.llm = get_llm_client()

    def generate(
        self,
        graph_id: str,
        simulation_requirement: str,
        entity_types: list[str] = None,
        on_progress: callable = None,
    ) -> list[AgentProfile]:
        """Generate agent profiles from graph entities."""
        nodes = self.graph_service.get_nodes(graph_id)

        if entity_types:
            nodes = [n for n in nodes if any(t in n.get("labels", []) for t in entity_types)]

        profiles = []
        for i, node in enumerate(nodes):
            if on_progress:
                on_progress(int((i / len(nodes)) * 100), f"Generating profile for {node['name']}")

            context = self.graph_service.get_node_context(graph_id, node["node_id"])
            neighbors = ", ".join(n["name"] for n in context.get("neighbors", []))
            edges = ", ".join(f"{e.get('relation_type', 'RELATED')} -> {e['target_id']}" for e in context.get("edges", []))

            user_msg = f"""Entity: {node['name']}
Type: {', '.join(node.get('labels', []))}
Summary: {node.get('summary', '')}
Relationships: {edges}
Connected to: {neighbors}
Simulation context: {simulation_requirement}"""

            try:
                result = self.llm.chat_json(
                    messages=[
                        {"role": "system", "content": PROFILE_SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=0.7,
                    max_tokens=2000,
                )

                profile = AgentProfile(
                    agent_id=i + 1,
                    name=node["name"],
                    username=node["node_id"],
                    bio=result.get("bio", ""),
                    persona=result.get("persona", ""),
                    age=result.get("age", 25),
                    profession=result.get("profession", ""),
                    mbti=result.get("mbti", ""),
                    entity_type=node.get("labels", ["Person"])[0],
                )
                profiles.append(profile)
            except Exception:
                profiles.append(AgentProfile(
                    agent_id=i + 1, name=node["name"], username=node["node_id"],
                    entity_type=node.get("labels", ["Person"])[0],
                ))

        if on_progress:
            on_progress(100, "Profile generation complete")
        return profiles
```

- [ ] **Step 4: Run test — expect PASS**

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: add profile generator with LLM persona creation"
```

---

### Task 5: Simulation Runner

**Files:**
- Create: `backend/app/services/simulation_runner.py`
- Create: `backend/tests/test_services/test_simulation_runner.py`

- [ ] **Step 1: Write test**

```python
# backend/tests/test_services/test_simulation_runner.py
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.simulation_runner import SimulationRunner
from app.models.simulation import SimState, AgentProfile, AgentAction
from app.services.sim_engine import SimEngine

MOCK_AGENT_DECISION = """I'll create a post about my research findings.

ACTION: create_post
CONTENT: Excited to share our latest findings on neural network interpretability! The results suggest new approaches to understanding model behavior. #AI #Research"""

@patch("app.services.simulation_runner.get_fast_llm_client")
def test_run_single_round(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat.return_value = MOCK_AGENT_DECISION
    mock_get_client.return_value = mock_client

    engine = SimEngine()
    engine.create_platform("twitter")

    agents = [
        AgentProfile(agent_id=1, name="Alice", username="alice", persona="A curious student", entity_type="Student"),
    ]

    runner = SimulationRunner(engine=engine)
    actions = runner.run_round(1, "twitter", agents, "Test simulation")

    assert len(actions) >= 1
    assert actions[0].agent_name == "Alice"
    assert actions[0].round_num == 1

@patch("app.services.simulation_runner.get_fast_llm_client")
def test_run_multiple_rounds(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat.return_value = "ACTION: DO_NOTHING"
    mock_get_client.return_value = mock_client

    engine = SimEngine()
    engine.create_platform("twitter")

    agents = [
        AgentProfile(agent_id=1, name="Alice", username="alice", persona="Student", entity_type="Student"),
        AgentProfile(agent_id=2, name="Bob", username="bob", persona="Professor", entity_type="Professor"),
    ]

    runner = SimulationRunner(engine=engine)
    all_actions = []
    for round_num in range(1, 4):
        actions = runner.run_round(round_num, "twitter", agents, "Test")
        all_actions.extend(actions)

    assert len(all_actions) == 6  # 2 agents * 3 rounds

@patch("app.services.simulation_runner.get_fast_llm_client")
def test_parse_create_post_action(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat.return_value = "ACTION: create_post\nCONTENT: Hello world!"
    mock_get_client.return_value = mock_client

    engine = SimEngine()
    engine.create_platform("twitter")

    runner = SimulationRunner(engine=engine)
    agents = [AgentProfile(agent_id=1, name="Alice", username="alice", persona="Student", entity_type="Student")]
    actions = runner.run_round(1, "twitter", agents, "Test")

    assert actions[0].action_type == "CREATE_POST"
    # Post should exist in engine
    feed = engine.get_feed("twitter")
    assert len(feed) == 1

@patch("app.services.simulation_runner.get_fast_llm_client")
def test_parse_like_action(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    engine = SimEngine()
    engine.create_platform("twitter")
    post_id = engine.create_post("twitter", 99, "Existing post")

    mock_client.chat.return_value = f"ACTION: like_post\nPOST_ID: {post_id}"

    runner = SimulationRunner(engine=engine)
    agents = [AgentProfile(agent_id=1, name="Alice", username="alice", persona="Student", entity_type="Student")]
    actions = runner.run_round(1, "twitter", agents, "Test")

    assert actions[0].action_type == "LIKE"
```

- [ ] **Step 2: Run test — expect FAIL**

- [ ] **Step 3: Implement**

```python
# backend/app/services/simulation_runner.py
"""Multi-agent simulation runner using Claude LLM for agent decisions."""

import re
import json
from ..utils.llm_client import get_fast_llm_client
from ..models.simulation import AgentProfile, AgentAction
from .sim_engine import SimEngine
from ..agents.sim_agent import SIM_AGENT_PROMPT_TEMPLATE

ACTION_PARSE_PATTERN = re.compile(r'ACTION:\s*(\w+)', re.IGNORECASE)
CONTENT_PARSE_PATTERN = re.compile(r'CONTENT:\s*(.+?)(?:\n|$)', re.IGNORECASE | re.DOTALL)
POST_ID_PARSE_PATTERN = re.compile(r'POST_ID:\s*(\S+)', re.IGNORECASE)
TARGET_PARSE_PATTERN = re.compile(r'TARGET(?:_ID)?:\s*(\S+)', re.IGNORECASE)


class SimulationRunner:
    def __init__(self, engine: SimEngine = None):
        self.engine = engine or SimEngine()
        self.llm = get_fast_llm_client()

    def run_round(
        self,
        round_num: int,
        platform: str,
        agents: list[AgentProfile],
        sim_context: str,
    ) -> list[AgentAction]:
        """Run one simulation round for all agents on a platform."""
        actions = []
        feed = self.engine.get_feed(platform, limit=10)
        feed_text = json.dumps(feed[:5], ensure_ascii=False, default=str) if feed else "No posts yet."

        for agent in agents:
            prompt = SIM_AGENT_PROMPT_TEMPLATE.format(
                agent_name=agent.name,
                persona=agent.persona,
                age=agent.age,
                profession=agent.profession,
                mbti=agent.mbti,
                bio=agent.bio,
                sim_context=sim_context,
                round_num=round_num,
                platform=platform,
            )

            try:
                response = self.llm.chat(
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": f"Current feed:\n{feed_text}\n\nDecide your ONE action for this round."},
                    ],
                    temperature=0.8,
                    max_tokens=500,
                )

                action = self._parse_and_execute(response, agent, round_num, platform)
                actions.append(action)
            except Exception:
                actions.append(AgentAction(
                    round_num=round_num, platform=platform, agent_id=agent.agent_id,
                    agent_name=agent.name, action_type="DO_NOTHING",
                ))

        return actions

    def _parse_and_execute(self, response: str, agent: AgentProfile, round_num: int, platform: str) -> AgentAction:
        """Parse LLM response and execute the action on the engine."""
        action_match = ACTION_PARSE_PATTERN.search(response)
        action_type = action_match.group(1).upper() if action_match else "DO_NOTHING"

        content = ""
        content_match = CONTENT_PARSE_PATTERN.search(response)
        if content_match:
            content = content_match.group(1).strip()

        post_id_match = POST_ID_PARSE_PATTERN.search(response)
        post_id = post_id_match.group(1) if post_id_match else None

        target_match = TARGET_PARSE_PATTERN.search(response)
        target_id = int(target_match.group(1)) if target_match and target_match.group(1).isdigit() else None

        # Execute on engine
        if action_type == "CREATE_POST" and content:
            self.engine.create_post(platform, agent.agent_id, content)
        elif action_type in ("LIKE", "LIKE_POST") and post_id:
            self.engine.like_post(platform, agent.agent_id, post_id)
            action_type = "LIKE"
        elif action_type in ("REPLY", "REPLY_TO_POST") and post_id and content:
            self.engine.reply_to_post(platform, agent.agent_id, post_id, content)
            action_type = "REPLY"
        elif action_type == "REPOST" and post_id:
            self.engine.repost(platform, agent.agent_id, post_id)
        elif action_type in ("FOLLOW", "FOLLOW_USER") and target_id:
            self.engine.follow(platform, agent.agent_id, target_id)
            action_type = "FOLLOW"
        else:
            action_type = "DO_NOTHING"

        return AgentAction(
            round_num=round_num, platform=platform,
            agent_id=agent.agent_id, agent_name=agent.name,
            action_type=action_type, content=content,
            target_agent_id=target_id, target_post_id=post_id,
        )
```

- [ ] **Step 4: Run test — expect PASS**

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: add simulation runner with LLM agent decision loop"
```

---

## Chunk 3: Report Generator + Chat Service (Tasks 6-7)

### Task 6: Report Generator (ReACT Pattern)

**Files:**
- Create: `backend/app/services/report_generator.py`
- Create: `backend/tests/test_services/test_report_gen.py`

- [ ] **Step 1: Write test**

```python
# backend/tests/test_services/test_report_gen.py
import pytest
from unittest.mock import patch, MagicMock
from app.services.report_generator import ReportGenerator
from app.models.simulation import SimState, AgentProfile, AgentAction
from app.models.report import Report
from app.services.storage import Storage

def _make_sim_state(storage):
    state = SimState(project_id="p1", graph_id="g1")
    state.agents = [
        AgentProfile(agent_id=1, name="Alice", username="alice", entity_type="Student"),
        AgentProfile(agent_id=2, name="Bob", username="bob", entity_type="Professor"),
    ]
    state.actions = [
        AgentAction(round_num=1, platform="twitter", agent_id=1, agent_name="Alice", action_type="CREATE_POST", content="Hello!"),
        AgentAction(round_num=1, platform="twitter", agent_id=2, agent_name="Bob", action_type="LIKE", target_agent_id=1),
        AgentAction(round_num=2, platform="twitter", agent_id=1, agent_name="Alice", action_type="REPLY", content="Thanks Bob!", target_agent_id=2),
    ]
    state.current_round = 2
    storage.save_simulation(state)
    return state

@patch("app.services.report_generator.get_llm_client")
def test_generate_report(mock_get_client, tmp_path):
    mock_client = MagicMock()
    mock_client.chat.return_value = "## Executive Summary\n\nThe simulation showed interesting patterns..."
    mock_get_client.return_value = mock_client

    storage = Storage(data_dir=tmp_path)
    state = _make_sim_state(storage)

    gen = ReportGenerator(storage=storage)
    report = gen.generate(state.simulation_id)

    assert report.simulation_id == state.simulation_id
    assert report.summary != ""
    assert len(report.summary) > 20

@patch("app.services.report_generator.get_llm_client")
def test_report_uses_simulation_data(mock_get_client, tmp_path):
    mock_client = MagicMock()
    mock_client.chat.return_value = "Analysis complete."
    mock_get_client.return_value = mock_client

    storage = Storage(data_dir=tmp_path)
    state = _make_sim_state(storage)

    gen = ReportGenerator(storage=storage)
    gen.generate(state.simulation_id)

    # Verify LLM was called with simulation context
    call_args = mock_client.chat.call_args[1]["messages"]
    system_msg = [m for m in call_args if m["role"] == "system"][0]["content"]
    assert "Alice" in system_msg or "Bob" in system_msg

@patch("app.services.report_generator.get_llm_client")
def test_report_saved_to_storage(mock_get_client, tmp_path):
    mock_client = MagicMock()
    mock_client.chat.return_value = "Report content here."
    mock_get_client.return_value = mock_client

    storage = Storage(data_dir=tmp_path)
    state = _make_sim_state(storage)

    gen = ReportGenerator(storage=storage)
    report = gen.generate(state.simulation_id)

    loaded = storage.get_report(report.report_id)
    assert loaded is not None
    assert loaded.summary == "Report content here."
```

- [ ] **Step 2: Run test — expect FAIL**

- [ ] **Step 3: Implement**

```python
# backend/app/services/report_generator.py
"""Report generation using Claude LLM with simulation data analysis."""

from ..utils.llm_client import get_llm_client
from ..models.report import Report
from .storage import Storage, get_storage
from ..tools.report_tools import get_simulation_actions, get_agent_behavior_summary, get_interaction_network

REPORT_SYSTEM_PROMPT = """You are a professional simulation analyst. Generate a comprehensive analysis report.

You are provided with simulation data including:
- Agent actions across rounds
- Agent behavior summaries
- Interaction network

Write a structured report covering:
1. Executive Summary (key findings)
2. Agent Behavior Analysis (how different types behaved)
3. Interaction Dynamics (alliances, conflicts)
4. Sentiment & Opinion Flow (how opinions spread)
5. Emergent Patterns (unexpected outcomes)
6. Predictions & Recommendations

Use specific data and quotes from agent actions as evidence.
Write in the same language as the simulation context provided."""


class ReportGenerator:
    def __init__(self, storage: Storage = None):
        self.storage = storage or get_storage()
        self.llm = get_llm_client()

    def generate(self, simulation_id: str, on_progress: callable = None) -> Report:
        """Generate analysis report from simulation data."""
        state = self.storage.get_simulation(simulation_id)
        if not state:
            raise ValueError(f"Simulation {simulation_id} not found")

        if on_progress:
            on_progress(10, "Collecting simulation data...")

        # Gather data
        all_actions = get_simulation_actions(simulation_id, storage=self.storage)
        agent_summaries = {}
        for agent in state.agents:
            agent_summaries[agent.name] = get_agent_behavior_summary(simulation_id, agent.agent_id, storage=self.storage)
        network = get_interaction_network(simulation_id, storage=self.storage)

        if on_progress:
            on_progress(30, "Analyzing data...")

        # Build context for LLM
        data_context = self._build_data_context(state, all_actions, agent_summaries, network)

        if on_progress:
            on_progress(50, "Generating report...")

        response = self.llm.chat(
            messages=[
                {"role": "system", "content": REPORT_SYSTEM_PROMPT},
                {"role": "user", "content": data_context},
            ],
            temperature=0.5,
            max_tokens=8192,
        )

        if on_progress:
            on_progress(90, "Saving report...")

        report = Report(simulation_id=simulation_id, summary=response)
        self.storage.save_report(report)

        if on_progress:
            on_progress(100, "Report complete")

        return report

    def _build_data_context(self, state, actions, summaries, network) -> str:
        """Build comprehensive context string for LLM."""
        lines = []
        lines.append(f"## Simulation Overview")
        lines.append(f"- Agents: {len(state.agents)}")
        lines.append(f"- Rounds: {state.current_round}")
        lines.append(f"- Platforms: {', '.join(state.platforms)}")
        lines.append(f"- Total actions: {len(actions)}")
        lines.append("")

        lines.append("## Agent Profiles")
        for agent in state.agents:
            lines.append(f"- **{agent.name}** ({agent.entity_type}): {agent.bio or agent.persona[:100] if agent.persona else 'No bio'}")
        lines.append("")

        lines.append("## Agent Behavior Summaries")
        for name, summary in summaries.items():
            lines.append(f"- **{name}**: {summary.get('total_actions', 0)} actions, breakdown: {summary.get('action_breakdown', {})}")
        lines.append("")

        lines.append("## Interaction Network")
        lines.append(f"- Total interactions: {network.get('total', 0)}")
        for interaction in network.get("interactions", [])[:20]:
            lines.append(f"  - Agent {interaction['source']} → Agent {interaction['target']} ({interaction['type']})")
        lines.append("")

        lines.append("## Sample Actions (most recent)")
        for action in actions[-30:]:
            content_preview = action.get("content", "")[:100]
            lines.append(f"- R{action['round_num']} [{action['platform']}] {action['agent_name']}: {action['action_type']} {content_preview}")

        return "\n".join(lines)
```

- [ ] **Step 4: Run test — expect PASS**

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: add report generator with simulation data analysis"
```

---

### Task 7: Chat & Interview Service

**Files:**
- Create: `backend/app/services/chat_service.py`
- Create: `backend/tests/test_services/test_chat_service.py`

- [ ] **Step 1: Write test**

```python
# backend/tests/test_services/test_chat_service.py
import pytest
from unittest.mock import patch, MagicMock
from app.services.chat_service import ChatService
from app.models.report import Report
from app.models.simulation import SimState, AgentProfile, AgentAction
from app.services.storage import Storage

@patch("app.services.chat_service.get_llm_client")
def test_chat_with_report(mock_get_client, tmp_path):
    mock_client = MagicMock()
    mock_client.chat.return_value = "The simulation showed that students were more active than professors."
    mock_get_client.return_value = mock_client

    storage = Storage(data_dir=tmp_path)
    report = Report(simulation_id="sim1", summary="Students posted 3x more than professors.")
    storage.save_report(report)

    svc = ChatService(storage=storage)
    response = svc.chat_report(report.report_id, "Who was more active?")
    assert "students" in response.lower() or "active" in response.lower()

@patch("app.services.chat_service.get_fast_llm_client")
def test_interview_agent(mock_get_client, tmp_path):
    mock_client = MagicMock()
    mock_client.chat.return_value = "As a student, I felt compelled to share my opinions about the policy change."
    mock_get_client.return_value = mock_client

    storage = Storage(data_dir=tmp_path)
    state = SimState(project_id="p1", graph_id="g1")
    state.agents = [AgentProfile(agent_id=1, name="Alice", username="alice", persona="A passionate CS student")]
    state.actions = [AgentAction(round_num=1, platform="twitter", agent_id=1, agent_name="Alice", action_type="CREATE_POST", content="Policy change is unfair!")]
    storage.save_simulation(state)

    svc = ChatService(storage=storage)
    response = svc.interview_agent(state.simulation_id, 1, "Why did you post about the policy?")
    assert len(response) > 10

@patch("app.services.chat_service.get_llm_client")
def test_chat_maintains_history(mock_get_client, tmp_path):
    mock_client = MagicMock()
    mock_client.chat.side_effect = ["First answer.", "Second answer based on context."]
    mock_get_client.return_value = mock_client

    storage = Storage(data_dir=tmp_path)
    report = Report(simulation_id="sim1", summary="Report content.")
    storage.save_report(report)

    svc = ChatService(storage=storage)
    conv_id = "conv-1"
    svc.chat_report(report.report_id, "Question 1", conversation_id=conv_id)
    svc.chat_report(report.report_id, "Question 2", conversation_id=conv_id)

    # Second call should have history
    second_call_messages = mock_client.chat.call_args_list[1][1]["messages"]
    assert len(second_call_messages) >= 3  # system + Q1 + A1 + Q2
```

- [ ] **Step 2: Run test — expect FAIL**

- [ ] **Step 3: Implement**

```python
# backend/app/services/chat_service.py
"""Chat with report agent and interview simulation agents."""

from ..utils.llm_client import get_llm_client, get_fast_llm_client
from .storage import Storage, get_storage

# In-memory conversation store
_conversations: dict[str, list[dict]] = {}


class ChatService:
    def __init__(self, storage: Storage = None):
        self.storage = storage or get_storage()

    def chat_report(self, report_id: str, message: str, conversation_id: str = None) -> str:
        """Chat with the report agent about simulation findings."""
        report = self.storage.get_report(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")

        llm = get_llm_client()
        conv_id = conversation_id or f"report-{report_id}"

        system = f"""You are a simulation analysis assistant. Answer questions based on this report:

{report.summary}

Rules:
1. Answer based on the report content first
2. Be concise and specific
3. Cite data from the report when possible"""

        # Build message history
        if conv_id not in _conversations:
            _conversations[conv_id] = []

        messages = [{"role": "system", "content": system}]
        messages.extend(_conversations[conv_id])
        messages.append({"role": "user", "content": message})

        response = llm.chat(messages=messages, temperature=0.5, max_tokens=2000)

        # Save to history
        _conversations[conv_id].append({"role": "user", "content": message})
        _conversations[conv_id].append({"role": "assistant", "content": response})

        return response

    def interview_agent(self, simulation_id: str, agent_id: int, question: str) -> str:
        """Interview a simulation agent about their behavior."""
        state = self.storage.get_simulation(simulation_id)
        if not state:
            raise ValueError(f"Simulation {simulation_id} not found")

        agent = next((a for a in state.agents if a.agent_id == agent_id), None)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        # Build action summary
        agent_actions = [a for a in state.actions if a.agent_id == agent_id]
        action_summary = "\n".join(
            f"Round {a.round_num} [{a.platform}]: {a.action_type} - {a.content[:100]}"
            for a in agent_actions[:20]
        )

        llm = get_fast_llm_client()
        system = f"""You are {agent.name}. You just participated in a social media simulation.

YOUR PERSONA: {agent.persona}
YOUR BIO: {agent.bio}
YOUR PROFESSION: {agent.profession}

YOUR ACTIONS IN THE SIMULATION:
{action_summary}

Answer questions about your motivations, decisions, and observations.
Stay completely in character. Do not break character or mention you are an AI."""

        response = llm.chat(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": question},
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        return response
```

- [ ] **Step 4: Run test — expect PASS**

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: add chat service for report Q&A and agent interviews"
```

---

## Chunk 4: API Wiring (Tasks 8-10)

### Task 8: Wire Graph API (Ontology + Build)

**Files:**
- Modify: `backend/app/api/graph.py`
- Modify: `backend/tests/test_api/test_graph_api.py`

- [ ] **Step 1: Add integration test**

```python
# Add to backend/tests/test_api/test_graph_api.py
from unittest.mock import patch, MagicMock

MOCK_ONTOLOGY = {
    "entity_types": [{"name": "Person", "description": "A person", "attributes": ["role"]}],
    "edge_types": [{"name": "KNOWS", "description": "Knows", "source_types": ["Person"], "target_types": ["Person"]}],
    "analysis_summary": "Simple test ontology",
}

@patch("app.api.graph.OntologyService")
@pytest.mark.asyncio
async def test_generate_ontology(mock_onto_cls, app, tmp_path):
    mock_instance = MagicMock()
    mock_instance.generate.return_value = MOCK_ONTOLOGY
    mock_onto_cls.return_value = mock_instance

    test_file = tmp_path / "test.txt"
    test_file.write_text("Alice knows Bob. They work at MIT.")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with open(test_file, "rb") as f:
            resp = await client.post(
                "/api/project/upload",
                files={"files": ("test.txt", f, "text/plain")},
                data={"project_name": "Onto Test", "simulation_requirement": "Test sim"},
            )
        project_id = resp.json()["project_id"]

        resp = await client.post(f"/api/graph/ontology/generate", json={
            "project_id": project_id,
            "simulation_requirement": "Simulate social dynamics",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "ontology" in data
        assert len(data["ontology"]["entity_types"]) >= 1
```

- [ ] **Step 2: Rewrite graph.py API**

```python
# backend/app/api/graph.py
"""Graph API - ontology generation, graph building, data retrieval."""

import asyncio
import threading
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from ..services.storage import get_storage
from ..services.ontology_service import OntologyService
from ..services.graph_builder import GraphBuilder
from ..tools.graph_tools import get_graph_service
from ..utils.text_processor import split_into_chunks
from ..models.project import ProjectStatus

router = APIRouter()

class OntologyRequest(BaseModel):
    project_id: str
    simulation_requirement: str = ""

class BuildRequest(BaseModel):
    project_id: str
    simulation_requirement: str = ""
    chunk_size: int = 500
    chunk_overlap: int = 50

_tasks: dict[str, dict] = {}

@router.post("/ontology/generate")
def generate_ontology(req: OntologyRequest):
    project = get_storage().get_project(req.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    combined_text = "\n\n---\n\n".join(f.text_content for f in project.files if f.text_content)
    if not combined_text:
        raise HTTPException(status_code=400, detail="No text content in uploaded files")

    service = OntologyService()
    ontology = service.generate(req.simulation_requirement, combined_text)

    from ..models.project import Ontology, EntityType, EdgeType
    project.ontology = Ontology(
        entity_types=[EntityType(**et) for et in ontology["entity_types"]],
        edge_types=[EdgeType(**et) for et in ontology["edge_types"]],
        analysis_summary=ontology.get("analysis_summary", ""),
    )
    project.status = ProjectStatus.ONTOLOGY_GENERATED
    get_storage().save_project(project)

    return {"project_id": project.project_id, "ontology": ontology}

@router.post("/build")
def build_graph(req: BuildRequest, background_tasks: BackgroundTasks):
    project = get_storage().get_project(req.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.ontology:
        raise HTTPException(status_code=400, detail="Generate ontology first")

    task_id = f"build-{req.project_id}"
    _tasks[task_id] = {"status": "processing", "progress": 0, "message": "Starting..."}

    def _run():
        try:
            combined_text = "\n\n".join(f.text_content for f in project.files if f.text_content)
            chunks = split_into_chunks(combined_text, req.chunk_size, req.chunk_overlap)

            ontology = {
                "entity_types": [et.model_dump() for et in project.ontology.entity_types],
                "edge_types": [et.model_dump() for et in project.ontology.edge_types],
            }

            graph_svc = get_graph_service()
            builder = GraphBuilder(graph_service=graph_svc)
            graph_id = f"graph-{req.project_id}"

            builder.build(
                graph_id, ontology, chunks,
                on_progress=lambda p, m: _tasks[task_id].update({"progress": p, "message": m}),
            )

            project.graph_id = graph_id
            project.status = ProjectStatus.GRAPH_COMPLETED
            get_storage().save_project(project)

            node_count = graph_svc.get_node_count(graph_id)
            edge_count = len(graph_svc.get_edges(graph_id))
            _tasks[task_id] = {
                "status": "completed", "progress": 100,
                "result": {"graph_id": graph_id, "node_count": node_count, "edge_count": edge_count},
            }
        except Exception as e:
            _tasks[task_id] = {"status": "failed", "progress": 0, "error": str(e)}
            project.status = ProjectStatus.FAILED
            get_storage().save_project(project)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return {"task_id": task_id, "status": "processing"}

@router.get("/build/status")
def build_status(task_id: str):
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return _tasks[task_id]

@router.get("/{graph_id}")
def get_graph_data(graph_id: str):
    svc = get_graph_service()
    try:
        nodes = svc.get_nodes(graph_id)
        edges = svc.get_edges(graph_id)
        return {"graph_id": graph_id, "nodes": nodes, "edges": edges, "node_count": len(nodes), "edge_count": len(edges)}
    except KeyError:
        raise HTTPException(status_code=404, detail="Graph not found")
```

- [ ] **Step 3: Run tests — expect PASS**

- [ ] **Step 4: Commit**

```bash
git add -A && git commit -m "feat: wire graph API with ontology generation and async graph building"
```

---

### Task 9: Wire Simulation API (Prepare + Run via WebSocket)

**Files:**
- Modify: `backend/app/api/simulation.py`

- [ ] **Step 1: Rewrite simulation API**

```python
# backend/app/api/simulation.py
"""Simulation API - create, prepare, run via WebSocket."""

import json
import asyncio
import threading
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from ..services.storage import get_storage
from ..services.profile_generator import ProfileGenerator
from ..services.simulation_runner import SimulationRunner
from ..services.sim_engine import SimEngine
from ..tools.graph_tools import get_graph_service
from ..models.simulation import SimState, SimStatus

router = APIRouter()

_tasks: dict[str, dict] = {}

class CreateSimRequest(BaseModel):
    project_id: str
    graph_id: str
    platforms: list[str] = ["twitter", "reddit"]
    max_rounds: int = 10

class PrepareRequest(BaseModel):
    simulation_requirement: str = ""
    entity_types: list[str] = []

@router.post("/create")
def create_simulation(req: CreateSimRequest):
    state = SimState(
        project_id=req.project_id, graph_id=req.graph_id,
        platforms=req.platforms, max_rounds=req.max_rounds,
    )
    get_storage().save_simulation(state)
    return state.model_dump()

@router.get("/{sim_id}")
def get_simulation(sim_id: str):
    state = get_storage().get_simulation(sim_id)
    if not state:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return state.model_dump()

@router.post("/{sim_id}/prepare")
def prepare_simulation(sim_id: str, req: PrepareRequest):
    state = get_storage().get_simulation(sim_id)
    if not state:
        raise HTTPException(status_code=404, detail="Simulation not found")

    task_id = f"prepare-{sim_id}"
    _tasks[task_id] = {"status": "processing", "progress": 0, "message": "Starting..."}

    def _run():
        try:
            state.status = SimStatus.PREPARING
            get_storage().save_simulation(state)

            graph_svc = get_graph_service()
            gen = ProfileGenerator(graph_service=graph_svc)
            profiles = gen.generate(
                state.graph_id, req.simulation_requirement,
                entity_types=req.entity_types or None,
                on_progress=lambda p, m: _tasks[task_id].update({"progress": p, "message": m}),
            )

            state.agents = profiles
            state.status = SimStatus.READY
            get_storage().save_simulation(state)
            _tasks[task_id] = {"status": "completed", "progress": 100, "agents_count": len(profiles)}
        except Exception as e:
            state.status = SimStatus.FAILED
            get_storage().save_simulation(state)
            _tasks[task_id] = {"status": "failed", "error": str(e)}

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return {"task_id": task_id, "status": "processing"}

@router.get("/{sim_id}/prepare/status")
def prepare_status(sim_id: str, task_id: str):
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return _tasks[task_id]

@router.websocket("/{sim_id}/stream")
async def simulation_stream(websocket: WebSocket, sim_id: str):
    await websocket.accept()
    state = get_storage().get_simulation(sim_id)
    if not state:
        await websocket.close(code=4004, reason="Simulation not found")
        return

    if not state.agents:
        await websocket.send_json({"type": "error", "message": "No agents prepared. Run /prepare first."})
        await websocket.close()
        return

    try:
        state.status = SimStatus.RUNNING
        get_storage().save_simulation(state)

        engine = SimEngine()
        for platform in state.platforms:
            engine.create_platform(platform)

        runner = SimulationRunner(engine=engine)

        for round_num in range(1, state.max_rounds + 1):
            await websocket.send_json({"type": "round_start", "round": round_num})

            for platform in state.platforms:
                actions = await asyncio.to_thread(
                    runner.run_round, round_num, platform, state.agents,
                    f"Round {round_num}/{state.max_rounds}",
                )

                for action in actions:
                    state.actions.append(action)
                    await websocket.send_json({
                        "type": "agent_action", "round": round_num, "platform": platform,
                        "agent": action.agent_name, "action_type": action.action_type,
                        "content": action.content, "message": f"{action.agent_name}: {action.action_type} {action.content[:80]}",
                    })

            state.current_round = round_num
            get_storage().save_simulation(state)
            await websocket.send_json({"type": "round_end", "round": round_num})

        state.status = SimStatus.COMPLETED
        get_storage().save_simulation(state)
        await websocket.send_json({"type": "simulation_complete", "total_actions": len(state.actions)})

    except WebSocketDisconnect:
        state.status = SimStatus.STOPPED
        get_storage().save_simulation(state)
    except Exception as e:
        state.status = SimStatus.FAILED
        get_storage().save_simulation(state)
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
```

- [ ] **Step 2: Run tests — expect existing tests PASS**

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: wire simulation API with profile generation and WebSocket agent loop"
```

---

### Task 10: Wire Report API (Generate + Chat + Interview)

**Files:**
- Modify: `backend/app/api/report.py`

- [ ] **Step 1: Rewrite report API**

```python
# backend/app/api/report.py
"""Report API - generate reports, chat, interview agents."""

import threading
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.storage import get_storage
from ..services.report_generator import ReportGenerator
from ..services.chat_service import ChatService

router = APIRouter()

_tasks: dict[str, dict] = {}

class GenerateRequest(BaseModel):
    simulation_id: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

class InterviewRequest(BaseModel):
    simulation_id: str
    agent_id: int
    question: str

@router.post("/generate")
def generate_report(req: GenerateRequest):
    state = get_storage().get_simulation(req.simulation_id)
    if not state:
        raise HTTPException(status_code=404, detail="Simulation not found")

    task_id = f"report-{req.simulation_id}"
    _tasks[task_id] = {"status": "processing", "progress": 0}

    def _run():
        try:
            gen = ReportGenerator()
            report = gen.generate(
                req.simulation_id,
                on_progress=lambda p, m: _tasks[task_id].update({"progress": p, "message": m}),
            )
            _tasks[task_id] = {"status": "completed", "progress": 100, "report_id": report.report_id}
        except Exception as e:
            _tasks[task_id] = {"status": "failed", "error": str(e)}

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return {"task_id": task_id, "status": "processing"}

@router.get("/generate/status")
def report_status(task_id: str):
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return _tasks[task_id]

@router.get("/{report_id}")
def get_report(report_id: str):
    report = get_storage().get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report.model_dump()

@router.post("/{report_id}/chat")
def chat_with_report(report_id: str, req: ChatRequest):
    try:
        svc = ChatService()
        response = svc.chat_report(report_id, req.message, req.conversation_id)
        return {"response": response, "conversation_id": req.conversation_id or f"report-{report_id}"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/interview")
def interview_agent(req: InterviewRequest):
    try:
        svc = ChatService()
        response = svc.interview_agent(req.simulation_id, req.agent_id, req.question)
        return {"response": response, "agent_id": req.agent_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

- [ ] **Step 2: Run ALL tests**

```bash
cd /Users/ryan/SmartFish && uv run pytest -v
```

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "feat: wire report API with generation, chat, and agent interviews"
```

---

### Task 11: Update Config + Final Push

**Files:**
- Modify: `backend/app/config.py`

- [ ] **Step 1: Add report/sim constants to config**

```python
# Add to Settings class in config.py:
    REPORT_MAX_TOKENS: int = 8192
    REPORT_TEMPERATURE: float = 0.5
    SIM_AGENT_TEMPERATURE: float = 0.8
    SIM_AGENT_MAX_TOKENS: int = 500
```

- [ ] **Step 2: Run full test suite**

```bash
cd /Users/ryan/SmartFish && uv run pytest -v
```

- [ ] **Step 3: Commit and push**

```bash
git add -A && git commit -m "feat: complete LLM integration — 100% feature parity with MiroFish"
git push origin main
```

---

## MiroFish → SmartFish Feature Parity Checklist

| Feature | MiroFish | SmartFish Task |
|---------|----------|----------------|
| Document upload + parse | Zep + PyMuPDF | Already done |
| Ontology generation (LLM) | OpenAI chat_json | Task 2 |
| Knowledge graph build (LLM) | Zep + OpenAI | Task 3 |
| Agent profile generation (LLM) | OpenAI chat_json | Task 4 |
| Multi-agent simulation | OASIS | Task 5 |
| Report generation | ReACT + OpenAI | Task 6 |
| Report chat | OpenAI | Task 7 |
| Agent interview | OpenAI | Task 7 |
| Graph API (ontology + build) | Flask | Task 8 |
| Simulation API (prepare + WS) | Flask + polling | Task 9 |
| Report API (generate + chat) | Flask | Task 10 |
