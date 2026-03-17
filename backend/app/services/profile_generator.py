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

    def generate(self, graph_id, simulation_requirement, entity_types=None, on_progress=None):
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
            user_msg = f"Entity: {node['name']}\nType: {', '.join(node.get('labels', []))}\nSummary: {node.get('summary', '')}\nRelationships: {edges}\nConnected to: {neighbors}\nSimulation context: {simulation_requirement}"
            try:
                result = self.llm.chat_json(
                    messages=[{"role": "system", "content": PROFILE_SYSTEM_PROMPT}, {"role": "user", "content": user_msg}],
                    temperature=0.7, max_tokens=2000,
                )
                profile = AgentProfile(
                    agent_id=i + 1, name=node["name"], username=node["node_id"],
                    bio=result.get("bio", ""), persona=result.get("persona", ""),
                    age=result.get("age", 25), profession=result.get("profession", ""),
                    mbti=result.get("mbti", ""), entity_type=node.get("labels", ["Person"])[0],
                )
                profiles.append(profile)
            except Exception:
                profiles.append(AgentProfile(agent_id=i + 1, name=node["name"], username=node["node_id"], entity_type=node.get("labels", ["Person"])[0]))
        if on_progress:
            on_progress(100, "Profile generation complete")
        return profiles
