# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**DeerFlow** is a multi-agent research framework built on LangGraph that orchestrates specialized AI agents to conduct comprehensive research and generate detailed reports. The system uses a graph-based workflow architecture where agents collaborate through state management and message passing.

## Common Development Commands

### Python Backend Development

```bash
# Install dependencies using uv (recommended)
uv sync

# Run development server with hot reload
make serve
# Alternative: uv run server.py --reload

# Run console-based chat interface
uv run main.py

# Run interactive mode with predefined questions
uv run main.py --interactive

# Testing
make test
# Run specific test: pytest tests/integration/test_nodes.py

# Code quality checks
make lint       # Black format check + ruff linting
make format     # Format code with black

# Test coverage
make coverage

# LangGraph debugging (Mac)
make langgraph-dev
# Alternative: uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.12 langgraph dev --allow-blocking
```

### Frontend Development (Next.js Web UI)

```bash
# Navigate to web directory
cd web

# Install dependencies
pnpm install

# Development mode (with backend .env)
pnpm dev

# Type checking
pnpm typecheck

# Linting and formatting
pnpm lint
pnpm format:check
pnpm format:write

# Build and preview
pnpm build
pnpm preview
```

### Full Stack Development

```bash
# Bootstrap both backend and frontend in dev mode
# On macOS/Linux:
./bootstrap.sh -d

# On Windows:
bootstrap.bat -d
```

### Docker Deployment

```bash
# Backend only
docker build -t deer-flow-api .
docker run -d -t -p 127.0.0.1:8000:8000 --env-file .env --name deer-flow-api-app deer-flow-api

# Full stack with docker-compose
docker compose build
docker compose up
```

## Core Architecture

### Multi-Agent System Structure

The system follows a **modular multi-agent architecture** built on LangGraph:

1. **Coordinator**: Entry point that handles user interactions and routes research requests
2. **Planner**: Creates structured research plans with multiple steps
3. **Research Team**: 
   - **Researcher**: Web search and content crawling using tools like Tavily, Brave Search
   - **Coder**: Python code execution and data analysis using REPL tools
4. **Reporter**: Synthesizes findings into comprehensive research reports

### Key Workflow Pattern

```
START → Coordinator → [Background Investigation] → Planner → Human Feedback → Research Team → Reporter → END
```

### State Management

Central state object (`src/graph/types.py:State`) extends `MessagesState` and tracks:
- Research topic and locale
- Current plan and execution results  
- Resources and observations
- Plan iterations and feedback

### Configuration Architecture

- **Main Config**: `conf.yaml` for LLM models and core settings
- **Agent-LLM Mapping**: `src/config/agents.py` maps each agent to specific LLM types
- **Environment Variables**: `.env` for API keys and search engines
- **MCP Integration**: Model Context Protocol for dynamic tool loading

### LLM Integration

Supports multiple providers through litellm:
- **OpenAI**: GPT models and Azure OpenAI
- **Open Source**: DeepSeek, Qwen, Gemini via OpenAI-compatible APIs
- **Local**: Ollama models
- **Three-Tier System**: Basic, reasoning, and code-specific models

## Key Files and Directories

### Core Workflow
- `main.py` - Console interface entry point
- `server.py` - FastAPI web server entry point
- `src/workflow.py` - Main workflow orchestration
- `src/graph/builder.py` - LangGraph workflow construction
- `src/graph/nodes.py` - Individual agent node implementations
- `src/graph/types.py` - State definitions and type schemas

### Agents and Configuration  
- `src/agents/agents.py` - Agent factory and creation logic
- `src/config/agents.py` - Agent-to-LLM mapping configuration
- `src/config/configuration.py` - Main configuration dataclass
- `src/prompts/` - Jinja2 templates for agent prompts

### Tools and Integrations
- `src/tools/` - Built-in tools (search, crawl, python_repl, etc.)
- `src/llms/llm.py` - LLM provider abstractions
- `src/server/mcp_request.py` - MCP server integration
- `src/rag/` - RAG and knowledge base integrations

### Specialized Workflows
- `src/podcast/graph/` - Podcast generation workflow
- `src/ppt/graph/` - PowerPoint generation workflow  
- `src/prose/graph/` - Text enhancement workflow
- `src/prompt_enhancer/graph/` - Prompt improvement workflow

## Configuration Requirements

### Essential Configuration Files

1. **`.env`** (from `.env.example`):
   - `SEARCH_API=tavily` (or `duckduckgo`, `brave_search`, `arxiv`)
   - `TAVILY_API_KEY` or `BRAVE_SEARCH_API_KEY` 
   - `RAG_PROVIDER` and related keys for knowledge base integration

2. **`conf.yaml`** (from `conf.yaml.example`):
   - LLM model configurations using litellm format
   - Support for OpenAI, Azure, DeepSeek, Qwen, Gemini, Ollama, etc.
   - Model-specific settings (temperature, top_p, base_url, api_key)

### Agent-LLM Configuration

Modify `src/config/agents.py` to assign appropriate models:
```python
AGENT_LLM_MAP: dict[str, LLMType] = {
    "coordinator": "reasoning",    # Complex planning tasks
    "planner": "reasoning",       # Strategic research planning  
    "researcher": "basic",        # Information gathering
    "coder": "basic",            # Code execution
    "reporter": "basic",         # Report synthesis
}
```

## Development Best Practices

### Testing Strategy
- Unit tests in `tests/unit/` organized by module
- Integration tests in `tests/integration/` for end-to-end workflows
- Use pytest with coverage reporting
- Test configuration: `pyproject.toml` with 25% minimum coverage

### Code Quality Standards
- **Black** for code formatting with 88-character line length
- **Ruff** for comprehensive linting
- **Python 3.12+** required
- Follow existing patterns in agent creation and prompt templates

### LangGraph Development
- Use LangGraph Studio for debugging workflows: `make langgraph-dev`
- State updates via LangGraph Commands for proper node transitions
- Human-in-the-loop feedback via plan iteration system
- Enable LangSmith tracing for production monitoring

### MCP Server Integration
- Configure MCP servers in settings for dynamic tool loading
- Test MCP integration via `/api/mcp/servers` endpoints
- Agent-specific tool assignment through configuration

## API Endpoints

### Core Chat API
- `POST /api/chat` - Streaming chat with research agents
- `POST /api/chat/rag` - RAG-enhanced conversations

### Specialized Content Generation  
- `POST /api/podcast` - Generate podcast audio from reports
- `POST /api/ppt` - Create PowerPoint presentations
- `POST /api/prose` - Text enhancement and rewriting
- `POST /api/prompt-enhancer` - Improve prompt quality

### MCP and Configuration
- `GET /api/mcp/servers` - List configured MCP servers
- `POST /api/mcp/servers` - Add new MCP server
- `POST /api/config` - Update system configuration

## Important Notes

- **Non-reasoning models only**: OpenAI o1/o3 and DeepSeek R1 not yet supported
- **Context window requirements**: Deep research needs longer context models
- **Security considerations**: Evaluate MCP servers and Python REPL for production
- **Multi-modal support**: Handles text, images, and audio content generation
- **Internationalization**: Supports multiple languages via locale configuration