# BLOPA

Local personal assistant in Spanish: converses, searches current information on the web, runs n8n automations and controls home devices via Home Assistant.

**Project phases, scope and acceptance criteria live in [blopa.md](blopa.md).** Read it before starting any task and work on the current phase only.

---

## Principles

- **Local first:** the language model runs on the user's own hardware; no paid AI services. Known exception: devices without Matter (e.g. the Steren bulb) go through Home Assistant's Tuya cloud integration.
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

## React rules (`web/`)

Stack: Vite + React + TypeScript + Tailwind + shadcn/ui. Built inside Docker; FastAPI serves `web/dist`.

- No emojis in the UI; always use `lucide-react` icons.
- shadcn components live in `src/components/ui/` and are added with the shadcn CLI, not edited by hand.
- Presentation layer, one folder per page/section:

```
src/
├── App.tsx                          shell: layout and active page
├── app/<name>/page.tsx              thin orchestrator: destructures the hook, assembles JSX, no logic
├── presentation/
│   ├── pages/<name>/                ONLY .tsx components (PascalCase)
│   ├── hooks/<name>/                ONLY hooks (useXxx.ts): state, API calls, handlers
│   ├── types/<name>/types.ts        ONLY types
│   ├── constants/<name>/constants.ts ONLY constants
│   ├── mocks/<name>/mockData.ts     ONLY mock data
│   └── utils/<name>/                ONLY pure functions
├── lib/                             API client, storage, cn
└── components/ui/                   shadcn
```

- `pages/<name>/` never contains `.ts` files.
- Each component with its own state goes in its own `.tsx`; small presentational components can share a `Components.tsx`.
- Pages with several tabs/sections use kebab-case subfolders per section inside `pages/<name>/`; a shared component lives in its owner section and is imported with `../owner-section/Component`. Imports inside the same folder use `./Component`.
- Page wrapper: `<div className="flex flex-col gap-4 pb-6">`. The `main` layout already provides `px-4`; pages never add `p-4`, `px-4`, `max-w-*` or `mx-auto` to their root wrapper.
- Forms:
  - Field wrapper: `<div className="space-y-1.5">`
  - Label: `<Label className="text-xs font-medium">`
  - Input and SelectTrigger: `className="h-9 bg-background"`
  - Section header: `<p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-4">`
  - Field grid: `gap-4`

---

## Infrastructure rules

- Everything runs in **Docker Compose** with persistent volumes and must survive a machine restart.
- Compose profiles: `core`, `voice`, `n8n`, `home`. Optional services stay optional: if a service is not configured, its feature does not appear.
- Development machine: Mac mini M4, 16 GB. Ollama runs in Docker (ARM64, CPU only: Docker does not pass the Metal GPU to containers).
- Exceptions to Docker, both on the host with Node.js and local dependencies (never global):
  - The Electron app (`electron/`).
  - The Matter server (`matter/`, installed as LaunchAgent `com.blopa.matter-server` with `npm run service:install`, running from `~/Library/Application Support/BLOPA/matter` because launchd cannot read `~/Desktop`): Docker Desktop on macOS has no real host networking / IPv6 link-local, which Matter needs. It listens only on `127.0.0.1:5580`; Home Assistant reaches it at `ws://host.docker.internal:5580/ws`. Moves back into Docker on a Linux host.
- Frontend tooling (npm, shadcn CLI, Vite dev server) runs in `node:22-slim` containers, e.g. `docker compose --profile dev up web-dev`.
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
| Web UI | Vite + React + TypeScript + Tailwind + shadcn/ui | Built in a Docker stage; FastAPI serves `web/dist` |
| Desktop app | Electron | Runs on the host; wraps `http://localhost:8000`; microphone via browser APIs |
| Automations | n8n Community Edition 2.42.7 | Profile `n8n`; webhooks via internal Docker network; editor on `127.0.0.1:5678` only |
| Home automation | Home Assistant 2026.10.1 | Profile `home`; UI on `127.0.0.1:8123` only; Matter (local) and Tuya (cloud) integrations |
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
| `BLOPA_PORT` | `8000` | Web server port |
| `BLOPA_DATA_DIR` | `/data` | SQLite location (volume `blopa_data`) |
| `N8N_URL` | `http://n8n:5678` | n8n base URL; empty disables automations |
| `HA_URL` / `HA_TOKEN` | *(empty)* | Home Assistant URL and token |
| `MATTER_URL` | `ws://host.docker.internal:5580/ws` | Matter server; enables "Agregar dispositivo" |
| `BLOPA_WHISPER_MODEL` | `small` | Transcription model |

### Security

- No router ports open. Ollama is not exposed; n8n webhooks only on the internal Docker network and its editor only on `127.0.0.1`.
- Optional `BLOPA_API_TOKEN` protects web and API access.
- Closed list of actions per device type; sensitive actions always ask for confirmation.
- Confirmation is enforced by the agent (`Tool.confirmation_for`), never left to the model.
- Tools can declare `required_for(text)`; if the model answers such a message without using one of the required tools, the agent re-asks once. Home tools use it: orders require `home_control_device`, state questions require status/list, so the model never answers house state from memory.
- Automations store only an n8n webhook path; the URL is built from `N8N_URL`.
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
   - **Sensitive action** (`confirmation_for` returns a description): stop, ask, keep the pending action; "sí" runs it, "no" cancels, anything else cancels and is answered normally.
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
| `run_automation` | Trigger a registered n8n flow | Yes, by default (per automation) |

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
│   ├── sessions.py
│   ├── auth.py
│   ├── database.py
│   ├── confirmation.py
│   ├── routes/
│   │   ├── health.py
│   │   ├── chat.py
│   │   ├── automations.py
│   │   ├── devices.py
│   │   └── accounts.py
│   ├── automations/
│   │   ├── models.py
│   │   ├── repository.py
│   │   └── runner.py
│   ├── home/
│   │   ├── client.py
│   │   ├── socket.py
│   │   ├── catalog.py
│   │   ├── devices.py
│   │   ├── matter.py
│   │   └── tuya.py
│   ├── voice.py
│   ├── concerns/
│   │   ├── conversation_memory.py
│   │   ├── mentions_home.py
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
│       ├── run_automation.py
│       └── home.py
├── web/                 Vite + React app (see React rules)
├── matter/              Matter server (host, npm)
├── electron/
│   ├── package.json
│   ├── main.js
│   └── preload.js
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
