# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is an **Open WebUI configuration repository** containing custom extensions (actions, tools, and prompts) for a self-hosted Open WebUI instance. The repository stores user-created functionality that extends the base Open WebUI application running in Docker.

## Architecture

### Deployment Model
- Open WebUI runs as a Docker container (image: `ghcr.io/open-webui/open-webui:main`)
- Container accessible at `http://localhost:3000` (maps to container port 8080)
- Ollama backend runs separately at `http://192.168.15.13:11434`
- Data persistence via volume mount: `./data:/app/backend/data`

### Directory Structure
```
/
├── actions/           # Action buttons that execute deterministic Python code
├── tools/             # Tool definitions (JSON exports) that provide callable functions
├── prompts/           # System prompts that guide LLM behavior
├── data/              # Persistent storage (gitignored, mounted as Docker volume)
└── docker-compose.yaml # Container orchestration configuration
```

## Component Types

### Actions (`actions/`)
Python modules that create **action buttons** in the Open WebUI interface. When clicked, they execute deterministically without LLM involvement.

**Structure:**
- Must define an `Action` class with an `async def action()` method
- Use `__event_emitter__` to send status updates and messages to the UI
- Can have `Valves` (global config) and `UserValves` (per-user config)
- Import from `open_webui.routers.*` to access internal APIs

**Event Types:**
- `status`: Shows loading/progress indicators (`"done": False/True`)
- `message`: Injects content directly into the chat
- `citation`: Adds citations/references to messages

**Dependencies:**
- If external packages are needed, list in `requirements:` docstring
- Self-healing pattern: catch ImportError and run `pip install` before importing

### Tools (`tools/`)
JSON exports containing Python code that provides **callable functions** to the LLM. Tools are invoked by the LLM during conversations.

**Structure (JSON):**
- `content`: Python code as string
- `specs`: Function signatures with name, description, parameters
- Tools class with methods decorated implicitly by Open WebUI

### Prompts (`prompts/`)
Markdown files containing system instructions for specific workflows.

**Example:** `news.md` defines a protocol for the news filtering workflow, instructing the LLM to:
1. Call the tool immediately without speaking first
2. Filter results against user preferences
3. Format output in a specific way

## Environment Configuration

### Key Settings (docker-compose.yaml)
```yaml
# LLM Backend
OLLAMA_BASE_URL: http://192.168.15.13:11434
TASK_MODEL: qwen2.5:7b-instruct-q4_K_M  # Used for all task operations

# RAG/Embeddings
RAG_EMBEDDING_MODEL: mxbai-embed-large:latest
CHUNK_SIZE: 1000
CHUNK_OVERLAP: 200
RAG_TOP_K: 5

# Web Search (Tavily)
TAVILY_API_KEY: [key in docker-compose.yaml]
RAG_WEB_SEARCH_ENGINE: tavily
RAG_WEB_SEARCH_RESULT_COUNT: 10
RAG_WEB_SEARCH_CONCURRENT_REQUESTS: 3

# Authentication
WEBUI_AUTH: False  # Authentication is disabled
```

## Development Workflow

### Testing Actions/Tools
```bash
# Restart container to load changes
docker compose restart

# View container logs
docker compose logs -f open-webui

# Stop and remove container
docker compose down

# Start in background
docker compose up -d
```

### Installing Dependencies
Actions and tools can auto-install Python packages using the self-healing pattern:
```python
try:
    import feedparser
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "feedparser"])
    import feedparser
```

### Deployment
1. Add/modify files in `actions/`, `tools/`, or `prompts/`
2. Import in Open WebUI admin interface OR place in directories
3. Restart container if needed: `docker compose restart`

## Common Patterns

### Action Button Pattern
```python
class Action:
    async def action(self, body: dict, __event_emitter__=None, __user__=None, __request__=None):
        # 1. Show status
        await __event_emitter__({"type": "status", "data": {"description": "Working...", "done": False}})

        # 2. Do work (wrap sync code with asyncio.to_thread if needed)
        result = await asyncio.to_thread(self._sync_function)

        # 3. Clear status
        await __event_emitter__({"type": "status", "data": {"done": True}})

        # 4. Send message
        await __event_emitter__({"type": "message", "data": {"content": result}})

        return None  # Prevent LLM generation
```

### Tool Pattern
```python
class Tools:
    async def my_tool(self, param: str, __event_emitter__=None) -> str:
        """Description shown to LLM"""
        if __event_emitter__:
            await __event_emitter__({"type": "status", ...})
        return "Result string"
```

## Important Notes

- **Data directory is gitignored** - contains user data, vector stores, SQLite databases
- **No authentication** - this instance runs locally with `WEBUI_AUTH=False`
- **API keys in docker-compose.yaml** - Tavily API key is committed (replace if sharing publicly)
- **Python execution context** - All Python code runs inside the Open WebUI container with access to internal APIs
- **Async required** - All action/tool methods must be async (use `asyncio.to_thread` for sync code)
