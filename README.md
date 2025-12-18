# LLM Council

> **Note**: This is a fork of [karpathy/llm-council](https://github.com/karpathy/llm-council) with additional features and enhancements.

![llmcouncil](header.jpg)

The idea of this repo is that instead of asking a question to your favorite LLM provider (e.g. OpenAI GPT 5.1, Google Gemini 3.0 Pro, Anthropic Claude Sonnet 4.5, xAI Grok 4, eg.c), you can group them into your "LLM Council". This repo is a simple, local web app that essentially looks like ChatGPT except it uses OpenRouter to send your query to multiple LLMs, it then asks them to review and rank each other's work, and finally a Chairman LLM produces the final response.

In a bit more detail, here is what happens when you submit a query:

1. **Stage 1: First opinions**. The user query is given to all LLMs individually, and the responses are collected. The individual responses are shown in a "tab view", so that the user can inspect them all one by one.
2. **Stage 2: Review**. Each individual LLM is given the responses of the other LLMs. Under the hood, the LLM identities are anonymized so that the LLM can't play favorites when judging their outputs. The LLM is asked to rank them in accuracy and insight.
3. **Stage 3: Final response**. The designated Chairman of the LLM Council takes all of the model's responses and compiles them into a single final answer that is presented to the user.

## Vibe Code Alert

This project was 99% vibe coded as a fun Saturday hack because I wanted to explore and evaluate a number of LLMs side by side in the process of [reading books together with LLMs](https://x.com/karpathy/status/1990577951671509438). It's nice and useful to see multiple responses side by side, and also the cross-opinions of all LLMs on each other's outputs. I'm not going to support it in any way, it's provided here as is for other people's inspiration and I don't intend to improve it. Code is ephemeral now and libraries are over, ask your LLM to change it in whatever way you like.

## Enhancements in This Fork

This fork adds several features to the original project:

### 🔌 MCP Server Support (Best Feature!)
- **Native Claude Integration**: Consult the Council directly from your IDE or Claude Desktop as a tool/agent
- **Use in Any Project**: Bring the Council's wisdom to any codebase without switching windows
- **Stateless Execution**: Runs pure logic in-memory, keeping your chat history clean
- **Easy Installation**: One-line install via `uvx` (no cloning required)

### 🌓 Dark Mode Support
- **Toolbar with Theme Switcher**: New toolbar at the top with a toggle button to switch between light and dark modes
- **Persistent Theme Preference**: Your theme choice is saved to localStorage and persists across sessions
- **Smooth Transitions**: All UI elements smoothly transition between themes using CSS custom properties
- **Comprehensive Coverage**: All components (sidebar, chat interface, message stages) support both themes

### 📎 Multimodal Support
- **File Attachments**: Send images and files along with your queries
- **Supported File Types**: 
  - Images: PNG, JPEG, WebP, GIF
  - Documents: PDF, Plain text
- **Attachment Preview**: See previews of your attachments before sending
- **Model Compatibility**: Attachments are sent to multimodal-capable models in the council

### 📚 Documentation
- Added comprehensive architecture documentation in `docs/architecture-council.md`
- Detailed attachment handling guide in `docs/architecture-attachments.md`

### 🎨 UI Improvements
- Cleaner interface with better visual hierarchy
- Removed redundant title from sidebar (now only in toolbar)
- Enhanced conversation list with message counts

## Usage Modes

This project can be used in three different ways depending on your needs:

### Mode 1: Full Web App (Local)
Run the complete interface locally to visualize the 3-stage process, manage conversation history, and customize the experience.

**Prerequisites**:
- [uv](https://docs.astral.sh/uv/) installed
- Node.js & npm installed
- `.env` file with `OPENROUTER_API_KEY=sk-or-v1-...`

**Run**:
```bash
./start.sh
```
Or manually:
```bash
# Terminal 1
uv run python -m backend.main

# Terminal 2
cd frontend && npm run dev
```

### Mode 2: Portable CLI & Slash Command

Embed the Council into your own projects as a custom `claude-code` workflow (slash command or agent).

**Prerequisites**:
1.  **Running Backend**: You must have `llm-council` backend running locally (Mode 1).
2.  **Files**: Copy the following files to your target project:
    - `scripts/council_cli.py` -> `scripts/council_cli.py`
    - `docs/ask-council.md` -> `.claude/commands/ask-council.md` or as an agent `.claude/agents/ask-council.md`

**Usage**:
Once installed, you can trigger the council from within your project using:

```bash
/ask-council "Why is this code failing?"
```

The workflow will automatically:
1.  Analyze your query.
2.  Find relevant files.
3.  Consult the running LLM Council backend.
4.  Stream the collective wisdom back to you.

### Mode 3: MCP Server (Claude Integration)
Integrate the Council directly into **Claude Code** as a native tool. This runs the logic in stateless mode (in-memory) and doesn't require running a local server manually.

**Quick Install (One-Liner)**:
```bash
claude mcp add llm-council \
  -e OPENROUTER_API_KEY=sk-or-v1-YOUR-KEY \
  uvx --from git+https://github.com/NabilAttia123/llm-council-mcp.git \
  python mcp_server.py \
  --council-models "openai/gpt-5.1,google/gemini-3-pro-preview,anthropic/claude-sonnet-4.5,x-ai/grok-4.1-fast" \
  --chairman-model "openai/gpt-5.1"
```
*Note: You can customize the models directly in this command by changing the `--council-models` and `--chairman-model` flags.*

**Manual Configuration**:
If you prefer adding to `config.json` manually:

```json
{
  "mcpServers": {
    "llm-council": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/NabilAttia123/llm-council-mcp.git", 
        "python",
        "mcp_server.py",
        "--council-models", "openai/gpt-4o,anthropic/claude-3-opus",
        "--chairman-model", "anthropic/claude-3.5-sonnet"
      ],
      "env": {
        "OPENROUTER_API_KEY": "sk-or-v1-..."
      }
    }
  }
}
```

*Note: Replace `sk-or-v1-...` with your actual OpenRouter API Key.*
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/NabilAttia123/llm-council-mcp.git", 
        "python",
        "mcp_server.py",
        "--council-models", "openai/gpt-4o,anthropic/claude-3-opus",
        "--chairman-model", "anthropic/claude-opus-4-5"
      ],
      "env": {
        "OPENROUTER_API_KEY": "sk-or-v1-..."
      }
    }
  }
}
```

*Note: Replace `sk-or-v1-...` with your actual OpenRouter API Key.*

## Local Installation & Setup

(Required for **Mode 1** and **Mode 2**, but not for Mode 3)

### 1. Install Dependencies

The project uses [uv](https://docs.astral.sh/uv/) for project management.

**Backend:**
```bash
uv sync
```

**Frontend** (Mode 1 only):
```bash
cd frontend
npm install
cd ..
```

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
OPENROUTER_API_KEY=sk-or-v1-...
```

Get your API key at [openrouter.ai](https://openrouter.ai/).

### 3. Configure Models (Optional)

You can customize the council members by editing `backend/config.py`:

```python
COUNCIL_MODELS = [
    "openai/gpt-5.1",
    "google/gemini-3-pro-preview",
    "anthropic/claude-sonnet-4.5",
    "x-ai/grok-4.1-fast",
]
```

*Tip: If using **Mode 3 (MCP)**, you don't need to edit this file. You can simply pass `--council-models "model1,model2"` and `--chairman-model "model3"` directly in your `claude mcp add` command.*

## Tech Stack

- **Backend:** FastAPI (Python 3.10+), async httpx, OpenRouter API
- **Frontend:** React + Vite, react-markdown for rendering
- **MCP**: Model Context Protocol (FastMCP)
- **Package Management:** uv for Python, npm for JavaScript
