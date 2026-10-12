import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ollama_url: str = "http://ollama:11434"
    model: str = "qwen3:4b-instruct"
    num_ctx: int = 4096
    max_tokens: int = 400
    think: bool = False
    timezone: str = "America/Monterrey"
    history_limit: int = 20
    request_timeout: float = 120.0

    @classmethod
    def from_env(cls, env=None):
        env = os.environ if env is None else env
        return cls(
            ollama_url=env.get("OLLAMA_URL", cls.ollama_url).rstrip("/"),
            model=env.get("BLOPA_MODEL", cls.model),
            num_ctx=int(env.get("BLOPA_NUM_CTX", cls.num_ctx)),
            max_tokens=int(env.get("BLOPA_MAX_TOKENS", cls.max_tokens)),
            think=env.get("BLOPA_THINK", "false").strip().lower() in ("1", "true", "yes"),
            timezone=env.get("BLOPA_TIMEZONE", cls.timezone),
        )
