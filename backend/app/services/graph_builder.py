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
- Use consistent IDs (lowercase, no spaces, e.g. "alice_chen")
- Each entity: id, name, type (must match ontology), summary, attributes
- Each relationship: source (entity id), target (entity id), type (must match ontology)

Respond with JSON:
{{
  "entities": [{{"id": "...", "name": "...", "type": "...", "summary": "...", "attributes": {{}}}}],
  "relationships": [{{"source": "...", "target": "...", "type": "...", "attributes": {{}}}}]
}}"""


class GraphBuilder:
    def __init__(self, graph_service: GraphService = None):
        self.graph_service = graph_service or GraphService()
        self.llm = get_llm_client()

    def build(self, graph_id: str, ontology: dict, chunks: list[str], on_progress: Callable = None) -> str:
        self.graph_service.create_graph(graph_id)
        et_desc = "\n".join(f"- {et['name']}: {et.get('description', '')}" for et in ontology.get("entity_types", []))
        edge_desc = "\n".join(f"- {et['name']}: {et.get('description', '')}" for et in ontology.get("edge_types", []))
        system_prompt = EXTRACTION_SYSTEM_PROMPT.format(entity_types=et_desc, edge_types=edge_desc)
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
                    temperature=0.3, max_tokens=4096,
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
                        self.graph_service.add_edge(graph_id, rel["source"], rel["target"], rel.get("type", "RELATED"), rel.get("attributes"))
            except Exception as e:
                if on_progress:
                    on_progress(int((i / len(chunks)) * 100), f"Error on chunk {i+1}: {str(e)[:100]}")

        if on_progress:
            on_progress(100, "Graph build complete")
        return graph_id
