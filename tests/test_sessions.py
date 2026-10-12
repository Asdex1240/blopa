from app.sessions import SessionStore


class Clock:
    def __init__(self):
        self.now = 0

    def __call__(self):
        return self.now


def test_unknown_session_gets_a_new_id():
    store = SessionStore(object)
    session_id, session = store.fetch("inventado")
    assert session_id != "inventado"
    assert store.fetch(session_id)[1] is session


def test_sessions_expire_after_ttl():
    clock = Clock()
    store = SessionStore(object, ttl=10, clock=clock)
    session_id, _ = store.fetch(None)
    clock.now = 11
    assert store.fetch(session_id)[0] != session_id


def test_oldest_session_is_evicted_over_limit():
    clock = Clock()
    store = SessionStore(object, limit=2, clock=clock)
    first, _ = store.fetch(None)
    clock.now = 1
    store.fetch(None)
    clock.now = 2
    store.fetch(None)
    assert first not in store.sessions
    assert len(store.sessions) == 2
