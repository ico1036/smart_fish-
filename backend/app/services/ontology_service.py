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
  "entity_types": [{"name": "...", "description": "...", "attributes": ["attr1"]}],
  "edge_types": [{"name": "...", "description": "...", "source_types": ["..."], "target_types": ["..."]}],
  "analysis_summary": "..."
}"""


class OntologyService:
    def __init__(self):
        self.llm = get_llm_client()

    def generate(self, simulation_requirement: str, document_text: str) -> dict:
        text = document_text[:MAX_TEXT_LENGTH]
        user_message = f"## Simulation Requirement\n{simulation_requirement}\n\n## Document Content\n{text}"
        result = self.llm.chat_json(
            messages=[
                {"role": "system", "content": ONTOLOGY_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3, max_tokens=4096,
        )
        return self._validate_and_fix(result)

    async def agenerate(self, simulation_requirement: str, document_text: str) -> dict:
        text = document_text[:MAX_TEXT_LENGTH]
        user_message = f"## Simulation Requirement\n{simulation_requirement}\n\n## Document Content\n{text}"
        result = await self.llm.achat_json(
            messages=[
                {"role": "system", "content": ONTOLOGY_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3, max_tokens=4096,
        )
        return self._validate_and_fix(result)

    def _validate_and_fix(self, result: dict) -> dict:
        entity_types = result.get("entity_types", [])
        names = [et["name"] for et in entity_types]
        if "Person" not in names:
            entity_types.append({"name": "Person", "description": "Generic person entity", "attributes": ["role"]})
        if "Organization" not in names:
            entity_types.append({"name": "Organization", "description": "Generic organization entity", "attributes": ["sector"]})
        person = next(et for et in entity_types if et["name"] == "Person")
        org = next(et for et in entity_types if et["name"] == "Organization")
        entity_types = [et for et in entity_types if et["name"] not in ("Person", "Organization")]
        entity_types.extend([person, org])
        result["entity_types"] = entity_types
        result.setdefault("edge_types", [])
        result.setdefault("analysis_summary", "")
        return result
