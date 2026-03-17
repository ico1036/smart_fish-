"""Simulation Agent - persona-based social media participant."""

SIM_AGENT_PROMPT_TEMPLATE = """You are {agent_name}, a participant in a social media simulation.

YOUR PERSONA:
{persona}

YOUR BACKGROUND:
- Age: {age}, Profession: {profession}, MBTI: {mbti}
- Bio: {bio}

SIMULATION CONTEXT:
{sim_context}

CURRENT ROUND: {round_num}
PLATFORM: {platform}

Look at the current feed and decide your action for this round. You MUST choose exactly ONE action:
- create_post: Write an original post expressing your views
- like_post: Like a post you agree with
- reply_to_post: Comment on a post with your perspective
- repost: Share a post you find important
- follow_user: Follow someone interesting
- DO_NOTHING: Skip this round (you're busy or not interested)

Stay in character. Your posts and comments should reflect your persona, profession, and viewpoint.
Consider your relationships with other agents when deciding how to interact."""


def create_sim_agent_config(agent_profile: dict, sim_context: str, round_num: int, platform: str) -> dict:
    """Create a simulation agent config with a specific persona."""
    prompt = SIM_AGENT_PROMPT_TEMPLATE.format(
        agent_name=agent_profile["name"],
        persona=agent_profile.get("persona", ""),
        age=agent_profile.get("age", 25),
        profession=agent_profile.get("profession", ""),
        mbti=agent_profile.get("mbti", ""),
        bio=agent_profile.get("bio", ""),
        sim_context=sim_context,
        round_num=round_num,
        platform=platform,
    )
    return {
        "name": f"sim-{agent_profile['name']}",
        "description": f"Simulates {agent_profile['name']} ({agent_profile.get('entity_type', 'Person')}) on {platform}",
        "system_prompt": prompt,
        "tools": ["create_post", "like_post", "reply_to_post", "repost", "follow_user", "get_feed"],
        "model": "haiku",
    }
