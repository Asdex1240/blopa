# BLOPA

Local personal assistant that speaks Spanish. It runs a language model on your own hardware with [Ollama](https://ollama.com) and does not use paid AI services. Everything runs in Docker, so nothing is installed on the host machine.

> **Status:** early development. Works from the browser, the macOS desktop app and the terminal: conversation, current date and time, web search and page reading. Home automation, n8n automations and voice are planned.

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with Docker Compose
- About 3 GB of free disk space for the model
- At least 8 GB of memory assigned to Docker

It was developed on a Mac mini M4 with 16 GB. On macOS, Ollama in Docker runs on the CPU only: Docker does not pass the Metal GPU to containers.

## Quick start

```bash
git clone git@github.com:Asdex1240/blopa.git
cd blopa
cp .env.example .env

docker compose up -d ollama
docker compose exec ollama ollama pull qwen3:4b-instruct

docker compose up -d --build
```

Open **http://localhost:8000** in a browser, or from another device on the home network at `http://<your-mac-ip>:8000`.

### Desktop app (macOS)

Requires Node.js. Electron is installed locally inside `electron/`, not globally.

```bash
cd electron
npm install
npm start
```

The app connects to `http://localhost:8000`; set `BLOPA_URL` to point it somewhere else. On first launch macOS asks for microphone access.

### Frontend development

The web UI is a Vite + React + Tailwind + shadcn/ui app in `web/`. The production build happens inside Docker. For live reload while editing:

```bash
docker compose --profile dev up web-dev
```

Then open **http://localhost:5173**; API calls are proxied to the `blopa` container.

### n8n automations

n8n runs locally with the `n8n` profile (enabled by default in `.env.example`). The editor is only reachable from this machine at **http://localhost:5678**; the first visit asks you to create the local owner account.

Workflows in `n8n/workflows/` can be imported and published from the command line:

| Workflow | Webhook | What it does |
|---|---|---|
| `blopa-ping.json` | `blopa-ping` | Echoes the text it receives; connection test |
| `clima.json` | `clima` | Current weather and 3-day forecast from Open-Meteo for the city in the text (Monterrey by default) |

```bash
docker compose exec n8n n8n import:workflow --input=/workflows/clima.json
docker compose exec n8n n8n publish:workflow --id=blopaClima000001
docker compose restart n8n
```

BLOPA reaches webhooks through the internal Docker network, e.g. `http://n8n:5678/webhook/blopa-ping`.

To let BLOPA launch a workflow, register it in **Automatizaciones** with a name, a description (BLOPA reads it to decide when to use it) and the webhook path. Automations ask for confirmation by default: BLOPA describes the action and waits for "sí" / "no", or the "Sí, hazlo" / "No" buttons. Every run, from chat or panel, is recorded in the history.

### Terminal

```bash
docker compose run --rm blopa python -m app.cli
```

| Command | Action |
|---|---|
| `/reset` | Start a new conversation |
| `/salir` | Exit |

### HTTP API

| Method | Route | Description |
|---|---|---|
| `GET` | `/health` | Model and service status |
| `GET` | `/chat/messages` | Current conversation |
| `POST` | `/chat/messages` | Send `{"text": "..."}`; returns the reply and the tools used |
| `DELETE` | `/chat/messages` | Start a new conversation |
| `GET` / `POST` | `/automations` | List or register n8n automations |
| `PATCH` / `DELETE` | `/automations/{id}` | Edit or remove an automation |
| `GET` / `POST` | `/automations/{id}/runs` | History of one automation, or run it now |
| `GET` | `/automation-runs` | Latest runs of all automations |

Each client gets its own conversation through a session cookie. When `BLOPA_API_TOKEN` is set, chat routes require `Authorization: Bearer <token>`.

## Configuration

All settings live in `.env`.

| Variable | Default | Description |
|---|---|---|
| `COMPOSE_PROFILES` | `core,n8n` | Docker Compose services to start |
| `OLLAMA_URL` | `http://ollama:11434` | Ollama address |
| `BLOPA_MODEL` | `qwen3:4b-instruct` | Model to use |
| `BLOPA_NUM_CTX` | `4096` | Context window size |
| `BLOPA_MAX_TOKENS` | `400` | Max tokens per model response (stops runaway generation) |
| `BLOPA_THINK` | `false` | Qwen3 internal reasoning (more accurate but slower) |
| `BLOPA_TIMEZONE` | `America/Monterrey` | User timezone |
| `BLOPA_API_TOKEN` | *(empty)* | Protects the chat API; recommended outside development |
| `BLOPA_BIND` | `0.0.0.0` | `127.0.0.1` for this machine only, `0.0.0.0` for the home network |
| `BLOPA_PORT` | `8000` | Web server port |
| `BLOPA_DATA_DIR` | `/data` | SQLite location inside the container (volume `blopa_data`) |
| `N8N_URL` | `http://n8n:5678` | n8n base URL; empty disables automations |

To use a native Ollama install instead of the container, set `OLLAMA_URL=http://host.docker.internal:11434`.

## Tests

The tests use a mock model and run in a container with no network access:

```bash
docker compose --profile test run --rm --build tests
```

## Project layout

```
app/
├── config.py        settings from .env
├── llm.py           Ollama client
├── agent.py         conversation and tool loop
├── system_prompt.py assistant personality and rules
├── errors.py        user-facing errors
├── url_guard.py     blocks local network addresses
├── factory.py       wires the agent together
├── cli.py           terminal interface
├── server.py        HTTP API and web interface
├── sessions.py      one conversation per client
├── auth.py          optional access token
├── database.py      SQLite schema
├── confirmation.py  yes / no detection for sensitive actions
├── routes/          health, chat and automations endpoints
├── automations/     repository and n8n webhook runner
├── tools/           date_time, search_web, read_page, run_automation
├── search/          search engines (DuckDuckGo)
└── concerns/        shared mixins
web/                 browser interface (Vite + React + Tailwind + shadcn/ui)
electron/            macOS desktop app
n8n/workflows/       n8n workflows versioned with the project
tests/
```

Code and infrastructure conventions are in [CLAUDE.md](CLAUDE.md).
