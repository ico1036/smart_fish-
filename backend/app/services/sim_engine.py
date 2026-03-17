import uuid
from datetime import datetime

class SimEngine:
    def __init__(self):
        self.platforms: dict[str, dict] = {}

    def create_platform(self, name: str):
        self.platforms[name] = {"posts": [], "comments": [], "follows": [], "likes": []}

    def create_post(self, platform: str, agent_id: int, content: str) -> str:
        post_id = str(uuid.uuid4())[:8]
        self.platforms[platform]["posts"].append({
            "post_id": post_id,
            "agent_id": agent_id,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "likes": 0,
            "reposts": 0,
        })
        return post_id

    def like_post(self, platform: str, agent_id: int, post_id: str) -> bool:
        for post in self.platforms[platform]["posts"]:
            if post["post_id"] == post_id:
                post["likes"] += 1
                self.platforms[platform]["likes"].append({"agent_id": agent_id, "post_id": post_id})
                return True
        return False

    def reply_to_post(self, platform: str, agent_id: int, post_id: str, content: str) -> str:
        comment_id = str(uuid.uuid4())[:8]
        self.platforms[platform]["comments"].append({
            "comment_id": comment_id,
            "post_id": post_id,
            "agent_id": agent_id,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        return comment_id

    def repost(self, platform: str, agent_id: int, post_id: str) -> bool:
        for post in self.platforms[platform]["posts"]:
            if post["post_id"] == post_id:
                post["reposts"] += 1
                return True
        return False

    def follow(self, platform: str, follower_id: int, target_id: int):
        self.platforms[platform]["follows"].append({"follower_id": follower_id, "target_id": target_id})

    def get_feed(self, platform: str, limit: int = 20) -> list[dict]:
        return sorted(self.platforms[platform]["posts"], key=lambda x: x["timestamp"], reverse=True)[:limit]

    def get_post_with_comments(self, platform: str, post_id: str) -> dict | None:
        for post in self.platforms[platform]["posts"]:
            if post["post_id"] == post_id:
                comments = [c for c in self.platforms[platform]["comments"] if c["post_id"] == post_id]
                return {**post, "comments": comments}
        return None

    def get_platform_stats(self, platform: str) -> dict:
        p = self.platforms[platform]
        return {
            "total_posts": len(p["posts"]),
            "total_comments": len(p["comments"]),
            "total_likes": len(p["likes"]),
            "total_follows": len(p["follows"]),
        }
