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
    api_token: str = ""
    n8n_url: str = ""
    ha_url: str = ""
    ha_token: str = ""
    matter_url: str = ""
    data_dir: str = "/data"

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
            api_token=env.get("BLOPA_API_TOKEN", "").strip(),
            n8n_url=env.get("N8N_URL", "").strip().rstrip("/"),
            ha_url=env.get("HA_URL", "").strip().rstrip("/"),
            ha_token=env.get("HA_TOKEN", "").strip(),
            matter_url=env.get("MATTER_URL", "").strip(),
            data_dir=env.get("BLOPA_DATA_DIR", cls.data_dir),
        )
