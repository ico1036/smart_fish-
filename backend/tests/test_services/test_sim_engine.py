import pytest
from app.services.sim_engine import SimEngine

@pytest.fixture
def engine():
    e = SimEngine()
    e.create_platform("twitter")
    e.create_platform("reddit")
    return e

def test_create_platform(engine):
    assert "twitter" in engine.platforms
    assert "reddit" in engine.platforms

def test_create_post(engine):
    post_id = engine.create_post("twitter", agent_id=1, content="Hello world!")
    assert post_id is not None
    feed = engine.get_feed("twitter", limit=10)
    assert len(feed) == 1
    assert feed[0]["content"] == "Hello world!"

def test_like_post(engine):
    post_id = engine.create_post("twitter", 1, "Test post")
    ok = engine.like_post("twitter", agent_id=2, post_id=post_id)
    assert ok is True
    feed = engine.get_feed("twitter")
    assert feed[0]["likes"] == 1

def test_like_nonexistent_post(engine):
    ok = engine.like_post("twitter", 1, "fake-id")
    assert ok is False

def test_reply_to_post(engine):
    post_id = engine.create_post("twitter", 1, "Original post")
    comment_id = engine.reply_to_post("twitter", 2, post_id, "Nice post!")
    assert comment_id is not None
    post = engine.get_post_with_comments("twitter", post_id)
    assert len(post["comments"]) == 1
    assert post["comments"][0]["content"] == "Nice post!"

def test_repost(engine):
    post_id = engine.create_post("twitter", 1, "Viral content")
    ok = engine.repost("twitter", 2, post_id)
    assert ok is True
    feed = engine.get_feed("twitter")
    assert feed[0]["reposts"] == 1

def test_follow(engine):
    engine.follow("twitter", follower_id=1, target_id=2)
    stats = engine.get_platform_stats("twitter")
    assert stats["total_follows"] == 1

def test_get_feed_ordering(engine):
    engine.create_post("twitter", 1, "First")
    engine.create_post("twitter", 2, "Second")
    engine.create_post("twitter", 3, "Third")
    feed = engine.get_feed("twitter", limit=2)
    assert len(feed) == 2
    assert feed[0]["content"] == "Third"  # newest first

def test_platform_stats(engine):
    engine.create_post("twitter", 1, "Post 1")
    engine.create_post("twitter", 2, "Post 2")
    post_id = engine.get_feed("twitter")[0]["post_id"]
    engine.like_post("twitter", 3, post_id)
    engine.reply_to_post("twitter", 3, post_id, "Comment")
    stats = engine.get_platform_stats("twitter")
    assert stats["total_posts"] == 2
    assert stats["total_likes"] == 1
    assert stats["total_comments"] == 1

def test_get_nonexistent_post(engine):
    result = engine.get_post_with_comments("twitter", "fake")
    assert result is None
