from app.core.camera_worker import camera_indexes_to_try, camera_unavailable_message, open_camera_capture


class FakeCapture:
    def __init__(self, opened=False, readable=False):
        self.opened = opened
        self.readable = readable
        self.released = False
        self.settings = []

    def isOpened(self):
        return self.opened

    def set(self, prop, value):
        self.settings.append((prop, value))

    def read(self):
        return self.readable, object() if self.readable else None

    def release(self):
        self.released = True


class FakeCv2:
    CAP_DSHOW = 700
    CAP_MSMF = 1400
    CAP_ANY = 0
    CAP_PROP_FRAME_WIDTH = 3
    CAP_PROP_FRAME_HEIGHT = 4

    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []
        self.captures = []

    def VideoCapture(self, index, backend):
        self.calls.append((index, backend))
        opened, readable = self.outcomes.pop(0) if self.outcomes else (False, False)
        capture = FakeCapture(opened, readable)
        self.captures.append(capture)
        return capture


def test_camera_indexes_try_configured_first_then_common_indexes():
    assert camera_indexes_to_try(2) == [2, 0, 1, 3]
    assert camera_indexes_to_try(0) == [0, 1, 2, 3]


def test_open_camera_capture_falls_back_to_next_backend():
    fake = FakeCv2([(False, False), (True, True)])
    capture, index, backend, attempts = open_camera_capture(fake, 0)

    assert capture is fake.captures[1]
    assert index == 0
    assert backend == "Media Foundation"
    assert fake.calls[:2] == [(0, FakeCv2.CAP_DSHOW), (0, FakeCv2.CAP_MSMF)]
    assert "DirectShow: not_opened" in attempts[0]
    assert "Media Foundation: ok" in attempts[1]


def test_open_camera_capture_releases_opened_capture_that_cannot_read_frames():
    fake = FakeCv2([(True, False), (True, True)])
    capture, _index, backend, attempts = open_camera_capture(fake, 0)

    assert capture is fake.captures[1]
    assert fake.captures[0].released is True
    assert backend == "Media Foundation"
    assert "opened_but_no_frames" in attempts[0]


def test_camera_unavailable_message_mentions_privacy_and_attempts():
    message = camera_unavailable_message(["index 0 via DirectShow: not_opened"])

    assert "Privacy" in message
    assert "antivirus" in message
    assert "index 0 via DirectShow" in message
