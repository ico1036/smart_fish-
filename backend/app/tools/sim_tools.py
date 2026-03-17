from ..services.sim_engine import SimEngine

_engine = SimEngine()

def get_engine() -> SimEngine:
    return _engine

def reset_engine():
    global _engine
    _engine = SimEngine()

def create_post(platform: str, agent_id: int, content: str) -> str:
    """Create a new post on the social media platform. Returns post_id."""
    return _engine.create_post(platform, agent_id, content)

def like_post(platform: str, agent_id: int, post_id: str) -> str:
    """Like a post. Returns success status."""
    ok = _engine.like_post(platform, agent_id, post_id)
    return f"Liked: {ok}"

def reply_to_post(platform: str, agent_id: int, post_id: str, content: str) -> str:
    """Reply to a post with a comment. Returns comment_id."""
    return _engine.reply_to_post(platform, agent_id, post_id, content)

def repost(platform: str, agent_id: int, post_id: str) -> str:
    """Repost/share an existing post. Returns success status."""
    ok = _engine.repost(platform, agent_id, post_id)
    return f"Reposted: {ok}"

def follow_user(platform: str, follower_id: int, target_id: int) -> str:
    """Follow another user on the platform."""
    _engine.follow(platform, follower_id, target_id)
    return f"Agent {follower_id} now follows {target_id}"

def get_feed(platform: str, limit: int = 20) -> list[dict]:
    """Get the latest posts from the platform feed."""
    return _engine.get_feed(platform, limit)

def get_platform_stats(platform: str) -> dict:
    """Get statistics for a platform."""
    return _engine.get_platform_stats(platform)
