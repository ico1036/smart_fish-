"""Chat with report agent and interview simulation agents."""
from __future__ import annotations
from ..utils.llm_client import get_llm_client, get_fast_llm_client
from .storage import Storage, get_storage

_conversations: dict[str, list[dict]] = {}

class ChatService:
    def __init__(self, storage: Storage = None):
        self.storage = storage or get_storage()

    def chat_report(self, report_id: str, message: str, conversation_id: str = None) -> str:
        report = self.storage.get_report(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")
        llm = get_llm_client()
        conv_id = conversation_id or f"report-{report_id}"
        system = f"You are a simulation analysis assistant. Answer questions based on this report:\n\n{report.summary}\n\nRules:\n1. Answer based on the report content first\n2. Be concise and specific\n3. Cite data from the report when possible"
        if conv_id not in _conversations:
            _conversations[conv_id] = []
        messages = [{"role": "system", "content": system}]
        messages.extend(_conversations[conv_id])
        messages.append({"role": "user", "content": message})
        response = llm.chat(messages=messages, temperature=0.5, max_tokens=2000)
        _conversations[conv_id].append({"role": "user", "content": message})
        _conversations[conv_id].append({"role": "assistant", "content": response})
        return response

    def interview_agent(self, simulation_id: str, agent_id: int, question: str) -> str:
        state = self.storage.get_simulation(simulation_id)
        if not state:
            raise ValueError(f"Simulation {simulation_id} not found")
        agent = next((a for a in state.agents if a.agent_id == agent_id), None)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        agent_actions = [a for a in state.actions if a.agent_id == agent_id]
        action_summary = "\n".join(f"Round {a.round_num} [{a.platform}]: {a.action_type} - {a.content[:100]}" for a in agent_actions[:20])
        llm = get_fast_llm_client()
        system = f"You are {agent.name}. You just participated in a social media simulation.\n\nYOUR PERSONA: {agent.persona}\nYOUR BIO: {agent.bio}\nYOUR PROFESSION: {agent.profession}\n\nYOUR ACTIONS:\n{action_summary}\n\nAnswer questions in character. Do not break character."
        response = llm.chat(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": question}],
            temperature=0.7, max_tokens=1000,
        )
        return response
