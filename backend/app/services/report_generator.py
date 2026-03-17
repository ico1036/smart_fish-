"""Report generation using Claude LLM with simulation data analysis."""
from ..utils.llm_client import get_llm_client
from ..models.report import Report
from .storage import Storage, get_storage
from ..tools.report_tools import get_simulation_actions, get_agent_behavior_summary, get_interaction_network

REPORT_SYSTEM_PROMPT = """You are a professional simulation analyst. Generate a comprehensive analysis report.

You are provided with simulation data including agent actions, behavior summaries, and interaction networks.

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
        state = self.storage.get_simulation(simulation_id)
        if not state:
            raise ValueError(f"Simulation {simulation_id} not found")
        if on_progress:
            on_progress(10, "Collecting simulation data...")
        all_actions = get_simulation_actions(simulation_id, storage=self.storage)
        agent_summaries = {}
        for agent in state.agents:
            agent_summaries[agent.name] = get_agent_behavior_summary(simulation_id, agent.agent_id, storage=self.storage)
        network = get_interaction_network(simulation_id, storage=self.storage)
        if on_progress:
            on_progress(30, "Analyzing data...")
        data_context = self._build_data_context(state, all_actions, agent_summaries, network)
        if on_progress:
            on_progress(50, "Generating report...")
        response = self.llm.chat(
            messages=[{"role": "system", "content": REPORT_SYSTEM_PROMPT}, {"role": "user", "content": data_context}],
            temperature=0.5, max_tokens=8192,
        )
        if on_progress:
            on_progress(90, "Saving report...")
        report = Report(simulation_id=simulation_id, summary=response)
        self.storage.save_report(report)
        if on_progress:
            on_progress(100, "Report complete")
        return report

    def _build_data_context(self, state, actions, summaries, network) -> str:
        lines = [f"## Simulation Overview", f"- Agents: {len(state.agents)}", f"- Rounds: {state.current_round}", f"- Platforms: {', '.join(state.platforms)}", f"- Total actions: {len(actions)}", ""]
        lines.append("## Agent Profiles")
        for agent in state.agents:
            lines.append(f"- **{agent.name}** ({agent.entity_type}): {agent.bio or (agent.persona[:100] if agent.persona else 'No bio')}")
        lines.append("")
        lines.append("## Agent Behavior Summaries")
        for name, summary in summaries.items():
            lines.append(f"- **{name}**: {summary.get('total_actions', 0)} actions, breakdown: {summary.get('action_breakdown', {})}")
        lines.append("")
        lines.append("## Interaction Network")
        lines.append(f"- Total interactions: {network.get('total', 0)}")
        for interaction in network.get("interactions", [])[:20]:
            lines.append(f"  - Agent {interaction['source']} -> Agent {interaction['target']} ({interaction['type']})")
        lines.append("")
        lines.append("## Sample Actions (most recent)")
        for action in actions[-30:]:
            lines.append(f"- R{action['round_num']} [{action['platform']}] {action['agent_name']}: {action['action_type']} {action.get('content', '')[:100]}")
        return "\n".join(lines)
