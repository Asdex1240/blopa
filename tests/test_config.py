from app.config import Settings


def test_defaults_when_env_is_empty():
    settings = Settings.from_env({})
    assert settings.model == "qwen3:4b-instruct"
    assert settings.think is False


def test_reads_env_values():
    settings = Settings.from_env({
        "OLLAMA_URL": "http://host.docker.internal:11434/",
        "BLOPA_NUM_CTX": "8192",
        "BLOPA_THINK": "true",
    })
    assert settings.ollama_url == "http://host.docker.internal:11434"
    assert settings.num_ctx == 8192
    assert settings.think is True
