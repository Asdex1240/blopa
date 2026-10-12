# BLOPA

Local personal assistant in Spanish: converses, searches current information on the web, runs n8n automations and controls home devices via Home Assistant.

**Project phases, scope and acceptance criteria live in [blopa.md](blopa.md).** Read it before starting any task and work on the current phase only.

---

## Principles

- **Local first:** the language model runs on the user's own hardware; no paid AI services.
- **Real data, not invented:** anything that changes (prices, news, flights, weather) comes from tools.
- **Secure by default:** nothing exposed to the Internet; sensitive actions require an explicit "yes".
- **Reproducible:** the same code runs on any machine, configured through `.env`.
- **Docker for everything:** no global installations on the host machine.

---

## Code rules

- No comments in code.
- One responsibility per file; small modules.
- Shared behavior via mixins (Rails concerns pattern).
- Everything named in English. User-facing text in Mexican Spanish.
- `snake_case` for variables and functions; `PascalCase` for classes; `UPPER_SNAKE_CASE` for constants.
- REST API: resource-based routes only — the HTTP verb describes the action.
  - `GET /devices` not `GET /devices/list`
  - `POST /chat/messages` not `POST /chat/send-message`
  - `DELETE /automations/1` not `DELETE /automations/delete/1`
- HTTP calls with `httpx` and explicit timeouts.
- Tests with `pytest` and a mock model: they must pass without Ollama, Docker or Internet.

---

## Infrastructure rules

- Everything runs in **Docker Compose** with persistent volumes and must survive a machine restart.
- Compose profiles: `core`, `voice`, `n8n`, `home`. Optional services stay optional: if a service is not configured, its feature does not appear.
- Development machine: Mac mini M4, 16 GB. Ollama runs in Docker (ARM64, CPU only: Docker does not pass the Metal GPU to containers).
- Configuration lives in `.env` (copied from `.env.example`). Only `.env.example` is versioned; `.env` is in `.gitignore`.

### Stack

| Layer | Technology | Notes |
|---|---|---|
| Model runtime | Ollama (Docker, ARM64, CPU) | Not exposed outside Docker |
| Model | Qwen3 4B Instruct | ~2.5 GB; leaves room in the Docker VM for other services |
| Language | Python 3.12 | |
| API | FastAPI + Uvicorn | |
| HTTP client | httpx | Always with timeouts |
| Web search | DuckDuckGo (`ddgs`) | Replaceable with SearXNG or paid API |
| Page reading | BeautifulSoup | Blocks private addresses |
| Desktop app | Electron | Wraps the web UI; microphone via browser APIs |
| Automations | n8n Community Edition | Profile `n8n`; internal Docker network only |
| Home automation | Home Assistant | Profile `home` |
| Speech to text | faster-whisper | Profile `voice`; `small` model |
| Text to speech | `say` (macOS) / Piper | `say` for MVP |
| Testing | pytest | Mock model |

### Environment variables

| Variable | Example | Description |
|---|---|---|
| `OLLAMA_URL` | `http://ollama:11434` | Ollama service address |
| `BLOPA_MODEL` | `qwen3:4b-instruct` | Model to use |
| `BLOPA_NUM_CTX` | `4096` | Context window size |
| `BLOPA_MAX_TOKENS` | `400` | Max tokens per model response (stops runaway generation) |
| `BLOPA_THINK` | `false` | Qwen3 internal reasoning (slower) |
| `BLOPA_TIMEZONE` | `America/Monterrey` | User timezone |
| `BLOPA_API_TOKEN` | *(empty for dev)* | Protects web and API access |
| `BLOPA_BIND` | `0.0.0.0` | Who can access the web server |
| `HA_URL` / `HA_TOKEN` | *(empty)* | Home Assistant URL and token |
| `BLOPA_WHISPER_MODEL` | `small` | Transcription model |

### Security

- No router ports open. Ollama is not exposed; n8n only on the internal Docker network.
- Optional `BLOPA_API_TOKEN` protects web and API access.
- Closed list of actions per device type; sensitive actions always ask for confirmation.
- `read_page` blocks private and local IPs (router, n8n, Home Assistant).
- Secrets never go into Git.

---

## Architecture

```
Voice → faster-whisper ─┐
                        ├→ BLOPA Agent (FastAPI) → Ollama (Qwen3)
Text (Electron/web/API)─┘        │
                                 ├→ Tool registry → web search · Home Assistant · n8n
                                 └→ Response → TTS (say / Piper) in voice mode
```

### Agent loop

1. Message arrives (text or transcribed voice).
2. Agent sends the model: system prompt, history (~20 messages) and tool list.
3. If the model requests a tool:
   - **Sensitive action:** stop and ask for confirmation.
   - **Normal action:** execute and return the result to the model.
4. Maximum 5 steps; then force a final response.

### Tools

| Tool | Description | Confirmation |
|---|---|---|
| `date_time` | Current date and time | No |
| `search_web` | General or news search | No |
| `read_page` | Text from a public page | No |
| `home_list_devices` | List Home Assistant devices | No |
| `home_device_status` | Status of a device | No |
| `home_control_device` | Actions on a device | By device type |
| `run_automation` | Trigger an n8n flow | Yes, by default |

### Project structure

```
blopa/
├── app/
│   ├── config.py
│   ├── llm.py
│   ├── agent.py
│   ├── factory.py
│   ├── cli.py
│   ├── errors.py
│   ├── system_prompt.py
│   ├── url_guard.py
│   ├── server.py
│   ├── voice.py
│   ├── concerns/
│   │   ├── conversation_memory.py
│   │   ├── time_limited.py
│   │   └── truncates_text.py
│   ├── search/
│   │   └── duckduckgo.py
│   └── tools/
│       ├── base.py
│       ├── registry.py
│       ├── date_time.py
│       ├── search_web.py
│       ├── read_page.py
│       ├── home_assistant.py
│       └── n8n.py
├── electron/
│   ├── main.js
│   ├── preload.js
│   └── src/
│       ├── index.html
│       ├── styles.css
│       └── app.js
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-voice.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
└── README.md
```
