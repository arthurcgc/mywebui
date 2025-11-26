# MyWebUI

My personal Open WebUI setup with custom actions and tools for news aggregation, web scraping, and AI workflow automation.

## Overview

This repository contains my custom extensions for [Open WebUI](https://github.com/open-webui/open-webui), a self-hosted web interface for running Large Language Models (LLMs) with Ollama. The extensions include deterministic action buttons, callable tools, and system prompts that enhance the base Open WebUI functionality.

## Features

### 📰 News Aggregation
- **RSS News Fetcher**: Automatically pulls tech news from Kubernetes, ArgoCD, AWS, CNCF, The New Stack, and Hacker News
- **Brutalist Report Scraper**: Extracts curated tech headlines with real external links
- **Smart Filtering**: Filters news based on keywords (Kubernetes, DevOps, SRE, GitOps, Platform Engineering)
- **Customizable Timeframes**: Fetches articles from the last 48 hours

### 🧠 Memory Management
- **Add to Memory Button**: One-click action to save assistant responses to Open WebUI's memory system
- **Status Indicators**: Real-time feedback during memory operations
- **Error Handling**: Graceful error reporting with citations

### 🤖 Workflow Automation
- **Deterministic Actions**: Buttons that execute Python code without LLM involvement
- **Custom Prompts**: Pre-configured system instructions for specific workflows
- **Event Emitters**: Real-time status updates and message injection

## What's Inside

```
mywebui/
├── actions/                    # Action buttons (deterministic Python code)
│   ├── add_to_memories_action_button.py
│   └── news.py
├── tools/                      # Callable tools for LLM
│   └── tool-brutalist_scraper-export-*.json
├── prompts/                    # System prompts for workflows
│   └── news.md
├── docker-compose.yaml         # Container configuration
├── .env                        # Environment variables (not committed)
└── CLAUDE.md                   # Developer documentation
```

## Prerequisites

- Docker and Docker Compose
- [Ollama](https://ollama.ai/) running locally or on network
- Open WebUI compatible version: `>= 0.5.0`

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/mywebui.git
cd mywebui
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```bash
# Tavily API Key for web search (optional)
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. Update Docker Compose

Edit `docker-compose.yaml` to point to your Ollama instance:

```yaml
environment:
  - OLLAMA_BASE_URL=http://your-ollama-host:11434
```

### 4. Start Open WebUI

```bash
docker compose up -d
```

Access the interface at `http://localhost:3000`

### 5. Import Extensions

**Option A: Manual Import (Recommended)**
1. Go to Admin Panel → Actions
2. Upload action files from `actions/` directory
3. Go to Admin Panel → Tools
4. Import tool files from `tools/` directory

**Option B: Volume Mount**
Mount the directories in your `docker-compose.yaml`:
```yaml
volumes:
  - ./actions:/app/backend/data/actions
  - ./tools:/app/backend/data/tools
  - ./prompts:/app/backend/data/prompts
```

## Usage

### Fetching News

1. **RSS News Action**: Click the "Fetch Tech News" button in any chat to get the latest tech headlines
2. **Brutalist Scraper Tool**: Use the news prompt or ask the assistant to fetch news using the Brutalist tool
3. **Custom Filtering**: The LLM will automatically filter results based on your tech stack preferences

### Saving to Memory

1. After receiving a useful assistant response, click the "Add to Memory" action button
2. The response will be saved to your personal memory store
3. Future conversations can reference this information

## Configuration

### Customizing News Sources

Edit `actions/news.py` to modify RSS feeds:

```python
self.feeds = {
    "Your Source": "https://example.com/feed.xml",
    # Add more feeds here
}
```

### Adjusting Keywords

Modify the keyword filter in `actions/news.py`:

```python
self.keywords = [
    "kubernetes",
    "your-keyword",
    # Add more keywords
]
```

### RAG Settings

Open WebUI is configured with:
- **Embedding Model**: `mxbai-embed-large:latest`
- **Chunk Size**: 1000 tokens
- **Chunk Overlap**: 200 tokens
- **Top K Results**: 5

Adjust these in `docker-compose.yaml` under the environment section.

## Development

### Adding Custom Actions

1. Create a new Python file in `actions/` directory
2. Define an `Action` class with an `async def action()` method
3. Use `__event_emitter__` to send status updates and messages
4. Import into Open WebUI admin panel

Example structure:
```python
class Action:
    async def action(self, body: dict, __event_emitter__=None):
        await __event_emitter__({
            "type": "status",
            "data": {"description": "Working...", "done": False}
        })
        # Your code here
        return None
```

### Creating Tools

Tools provide callable functions for the LLM. See `tools/` directory for JSON export format.

### Dependencies

Actions can auto-install Python packages:
```python
try:
    import feedparser
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "feedparser"])
    import feedparser
```

## Tech Stack

- **Backend**: Open WebUI (Python/FastAPI)
- **LLM Runtime**: Ollama
- **Models**: Qwen 2.5 7B (task model), mxbai-embed-large (embeddings)
- **Search**: Tavily API
- **Container**: Docker

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_BASE_URL` | Ollama API endpoint | `http://192.168.15.13:11434` |
| `TAVILY_API_KEY` | Tavily search API key | Required for web search |
| `WEBUI_AUTH` | Enable authentication | `False` |
| `RAG_EMBEDDING_MODEL` | Embedding model name | `mxbai-embed-large:latest` |
| `TASK_MODEL` | Task execution model | `qwen2.5:7b-instruct-q4_K_M` |

## Security Notes

- **API Keys**: Never commit `.env` files or hardcode API keys
- **Authentication**: Disabled by default (`WEBUI_AUTH=False`) - enable for production
- **Network**: Configured for local network access only
- **Data**: Persistent data stored in `./data` directory (gitignored)

## Contributing

This is a personal configuration repository, but feel free to:
- Fork and adapt for your own use
- Submit issues for bugs
- Share your own extensions

## License

MIT License - Feel free to use and modify for your own projects.

## Acknowledgments

- [Open WebUI](https://github.com/open-webui/open-webui) - The amazing self-hosted LLM interface
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [Brutalist Report](https://brutalist.report/) - Curated tech news aggregator

## Resources

- [Open WebUI Documentation](https://docs.openwebui.com/)
- [Open WebUI GitHub](https://github.com/open-webui/open-webui)
- [Ollama Models](https://ollama.ai/library)
- [CLAUDE.md](./CLAUDE.md) - Developer documentation for working with this repository

---

**Note**: This is a personal configuration. Customize settings, models, and endpoints to match your infrastructure.
