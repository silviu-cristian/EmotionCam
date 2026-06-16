from app.core.interaction_engine import InteractionEngine


def test_message_cooldown():
    engine = InteractionEngine(cooldown_seconds=10)
    assert engine.message_for("happy", "positive", now=0)
    assert engine.message_for("happy", "positive", now=5) == ""
    assert engine.message_for("happy", "positive", now=11)


def test_no_message_for_unknown_or_when_disabled():
    assert InteractionEngine().message_for("unknown", "neutral", now=1) == ""
    assert InteractionEngine(enabled=False).message_for("happy", "positive", now=1) == ""


def test_message_can_use_local_profile_name():
    assert InteractionEngine(name="Silviu").message_for("happy", "positive", now=1).startswith("Silviu,")
