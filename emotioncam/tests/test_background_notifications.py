from app.core.background_notifications import BackgroundNotificationEngine


def test_negative_notification_cooldown():
    engine = BackgroundNotificationEngine(negative_cooldown=10, recovery_cooldown=5)
    assert engine.message_for("negative", now=0)
    assert engine.message_for("negative", now=5) == ""
    assert engine.message_for("negative", now=11)


def test_positive_notification_only_after_negative():
    engine = BackgroundNotificationEngine(negative_cooldown=10, recovery_cooldown=5)
    assert engine.message_for("positive", now=0) == ""
    engine.message_for("negative", now=1)
    assert engine.message_for("positive", now=2)
    assert engine.message_for("positive", now=3) == ""


def test_background_messages_can_use_name():
    assert BackgroundNotificationEngine(name="Silviu").message_for("negative", now=1).startswith("Silviu,")
