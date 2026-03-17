"""Multi-agent simulation runner using Claude LLM for agent decisions."""
import re
import json
from ..utils.llm_client import get_fast_llm_client
from ..models.simulation import AgentProfile, AgentAction
from .sim_engine import SimEngine
from ..agents.sim_agent import SIM_AGENT_PROMPT_TEMPLATE

ACTION_PARSE = re.compile(r'ACTION:\s*(\w+)', re.IGNORECASE)
CONTENT_PARSE = re.compile(r'CONTENT:\s*(.+?)(?:\n|$)', re.IGNORECASE | re.DOTALL)
POST_ID_PARSE = re.compile(r'POST_ID:\s*(\S+)', re.IGNORECASE)
TARGET_PARSE = re.compile(r'TARGET(?:_ID)?:\s*(\S+)', re.IGNORECASE)

class SimulationRunner:
    def __init__(self, engine: SimEngine = None):
        self.engine = engine or SimEngine()
        self.llm = get_fast_llm_client()

    def run_round(self, round_num, platform, agents, sim_context):
        actions = []
        feed = self.engine.get_feed(platform, limit=10)
        feed_text = json.dumps(feed[:5], ensure_ascii=False, default=str) if feed else "No posts yet."
        for agent in agents:
            prompt = SIM_AGENT_PROMPT_TEMPLATE.format(
                agent_name=agent.name, persona=agent.persona, age=agent.age,
                profession=agent.profession, mbti=agent.mbti, bio=agent.bio,
                sim_context=sim_context, round_num=round_num, platform=platform,
            )
            try:
                response = self.llm.chat(
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": f"Current feed:\n{feed_text}\n\nDecide your ONE action."},
                    ],
                    temperature=0.8, max_tokens=500,
                )
                action = self._parse_and_execute(response, agent, round_num, platform)
                actions.append(action)
            except Exception:
                actions.append(AgentAction(round_num=round_num, platform=platform, agent_id=agent.agent_id, agent_name=agent.name, action_type="DO_NOTHING"))
        return actions

    def _parse_and_execute(self, response: str, agent: AgentProfile, round_num: int, platform: str) -> AgentAction:
        action_match = ACTION_PARSE.search(response)
        action_type = action_match.group(1).upper() if action_match else "DO_NOTHING"
        content_match = CONTENT_PARSE.search(response)
        content = content_match.group(1).strip() if content_match else ""
        post_id_match = POST_ID_PARSE.search(response)
        post_id = post_id_match.group(1) if post_id_match else None
        target_match = TARGET_PARSE.search(response)
        target_id = int(target_match.group(1)) if target_match and target_match.group(1).isdigit() else None

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

        return AgentAction(round_num=round_num, platform=platform, agent_id=agent.agent_id, agent_name=agent.name, action_type=action_type, content=content, target_agent_id=target_id, target_post_id=post_id)
