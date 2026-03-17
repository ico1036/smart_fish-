from app.tools.sim_tools import (
    create_post, like_post, reply_to_post, repost,
    follow_user, get_feed, get_platform_stats, get_engine, reset_engine
)

def setup_function():
    reset_engine()
    engine = get_engine()
    engine.create_platform("twitter")

def test_create_post_tool():
    post_id = create_post("twitter", 1, "Hello from tool!")
    assert post_id is not None

def test_like_post_tool():
    post_id = create_post("twitter", 1, "Likeable post")
    result = like_post("twitter", 2, post_id)
    assert "True" in result

def test_reply_tool():
    post_id = create_post("twitter", 1, "Original")
    comment_id = reply_to_post("twitter", 2, post_id, "Reply!")
    assert comment_id is not None

def test_repost_tool():
    post_id = create_post("twitter", 1, "Repostable")
    result = repost("twitter", 2, post_id)
    assert "True" in result

def test_follow_tool():
    result = follow_user("twitter", 1, 2)
    assert "follows" in result

def test_get_feed_tool():
    create_post("twitter", 1, "Post 1")
    create_post("twitter", 2, "Post 2")
    feed = get_feed("twitter", limit=10)
    assert len(feed) == 2

def test_get_stats_tool():
    create_post("twitter", 1, "Post")
    stats = get_platform_stats("twitter")
    assert stats["total_posts"] == 1
