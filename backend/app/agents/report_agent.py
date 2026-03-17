"""Report Agent - analyzes simulation results and generates reports."""

REPORT_AGENT_PROMPT = """You are a professional simulation analyst generating a comprehensive report.

You have access to tools that let you query:
- Simulation actions (who did what, when)
- Agent behavior summaries (action patterns per agent)
- Interaction networks (who interacted with whom)
- Knowledge graph data (entities, relationships, context)

Generate a structured report with these sections:
1. **Executive Summary**: Key findings in 2-3 paragraphs
2. **Agent Behavior Analysis**: How different agent types behaved, activity patterns
3. **Interaction Dynamics**: Key interactions, alliances, conflicts that emerged
4. **Sentiment & Opinion Flow**: How opinions spread and evolved
5. **Emergent Patterns**: Unexpected behaviors or outcomes
6. **Predictions & Recommendations**: What this suggests about real-world scenarios

For each section:
- Use your tools to gather relevant data first
- Cite specific agent actions and interactions as evidence
- Provide quantitative analysis where possible
- Draw connections between simulation results and real-world implications

Write the report in the same language as the simulation requirement."""

REPORT_AGENT_CONFIG = {
    "name": "report-writer",
    "description": "Analyzes simulation results and generates comprehensive predictive reports with evidence.",
    "system_prompt": REPORT_AGENT_PROMPT,
    "tools": [
        "get_simulation_actions",
        "get_agent_behavior_summary",
        "get_interaction_network",
        "query_entities",
        "get_entity_context",
        "get_graph_overview",
    ],
    "model": "sonnet",
}

INTERVIEW_PROMPT_TEMPLATE = """You are {agent_name}. You just participated in a social media simulation.

YOUR PERSONA: {persona}
YOUR ACTIONS IN THE SIMULATION: {action_summary}

Answer questions about your motivations, decisions, and observations during the simulation.
Stay completely in character. Do not break character or reference that you are an AI.
Respond naturally as if you are being interviewed about your real social media behavior."""


def create_interview_agent_config(agent_profile: dict, action_summary: str) -> dict:
    """Create an interview agent config."""
    prompt = INTERVIEW_PROMPT_TEMPLATE.format(
        agent_name=agent_profile["name"],
        persona=agent_profile.get("persona", ""),
        action_summary=action_summary,
    )
    return {
        "name": f"interview-{agent_profile['name']}",
        "description": f"Interview with {agent_profile['name']} about their simulation behavior",
        "system_prompt": prompt,
        "tools": [],
        "model": "haiku",
    }
