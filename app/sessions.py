import secrets
import threading
import time


class Session:
    def __init__(self, agent):
        self.agent = agent
        self.lock = threading.Lock()
        self.touched_at = time.monotonic()


class SessionStore:
    def __init__(self, agent_factory, ttl=6 * 3600, limit=20, clock=time.monotonic):
        self.agent_factory = agent_factory
        self.ttl = ttl
        self.limit = limit
        self.clock = clock
        self.sessions = {}
        self.lock = threading.Lock()

    def fetch(self, session_id):
        with self.lock:
            self._expire()
            session = self.sessions.get(session_id)
            if session is None:
                session_id = secrets.token_urlsafe(24)
                session = self.sessions[session_id] = Session(self.agent_factory())
                self._evict_oldest()
            session.touched_at = self.clock()
            return session_id, session

    def _expire(self):
        now = self.clock()
        for session_id in [key for key, value in self.sessions.items() if now - value.touched_at > self.ttl]:
            del self.sessions[session_id]

    def _evict_oldest(self):
        while len(self.sessions) > self.limit:
            del self.sessions[min(self.sessions, key=lambda key: self.sessions[key].touched_at)]
