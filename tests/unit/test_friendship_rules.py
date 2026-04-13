from domain.friendship.rules import friendship_title_and_progress


def test_friendship_progress_at_start():
    title, progress = friendship_title_and_progress(0)
    assert title == "Stranger"
    assert progress == 0.0


def test_friendship_progress_mid_tier():
    title, progress = friendship_title_and_progress(150)
    assert title == "Acquaintance"
    assert progress == 25.0


def test_friendship_progress_exact_max_tier():
    title, progress = friendship_title_and_progress(2500)
    assert title == "Veyra's favourite 💖"
    assert progress == 100.0


def test_friendship_progress_above_max_tier():
    title, progress = friendship_title_and_progress(999999)
    assert title == "Veyra's favourite 💖"
    assert progress == 100.0
