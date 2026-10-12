# BLOPA

Local personal assistant that speaks Spanish. It runs a language model on your own hardware with [Ollama](https://ollama.com) and does not use paid AI services. Everything runs in Docker, so nothing is installed on the host machine.

> **Status:** early development. Works from the terminal: conversation, current date and time, web search and page reading. The desktop app, home automation, n8n automations and voice are planned.

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with Docker Compose
- About 6 GB of free disk space for the model
- At least 8 GB of memory assigned to Docker

It was developed on a Mac mini M4 with 16 GB. On macOS, Ollama in Docker runs on the CPU only: Docker does not pass the Metal GPU to containers.

## Quick start

```bash
git clone git@github.com:Asdex1240/blopa.git
cd blopa
cp .env.example .env

docker compose up -d ollama
docker compose exec ollama ollama pull qwen3:8b

docker compose run --rm blopa
```

```
BLOPA: Hola, ¿en qué te ayudo? (/reset para empezar de nuevo, /salir para terminar)
Tú: Hola, me llamo Juan
BLOPA: ¡Hola, Juan! ¿En qué te puedo ayudar?  (2.0 s)
```

| Command | Action |
|---|---|
| `/reset` | Start a new conversation |
| `/salir` | Exit |

## Configuration

All settings live in `.env`.

| Variable | Default | Description |
|---|---|---|
| `COMPOSE_PROFILES` | `core` | Docker Compose services to start |
| `OLLAMA_URL` | `http://ollama:11434` | Ollama address |
| `BLOPA_MODEL` | `qwen3:8b` | Model to use |
| `BLOPA_NUM_CTX` | `4096` | Context window size |
| `BLOPA_THINK` | `false` | Qwen3 internal reasoning (more accurate but slower) |
| `BLOPA_TIMEZONE` | `America/Monterrey` | User timezone |

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
├── tools/           date_time, search_web, read_page
├── search/          search engines (DuckDuckGo)
└── concerns/        shared mixins
tests/
```

Code and infrastructure conventions are in [CLAUDE.md](CLAUDE.md).
