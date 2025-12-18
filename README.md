# LLM Council

> **Note**: This is a fork of [karpathy/llm-council](https://github.com/karpathy/llm-council) with additional features and enhancements.

![llmcouncil](header.jpg)

## Why Use an LLM Council?

When you're stuck on a tricky problem in Claude Code or any other MCP-supporting CLI tool, get a second opinion from multiple frontier models at once. The LLM Council queries GPT-5.1, Gemini 3 Pro, Claude Sonnet 4.5, and Grok 4 simultaneously, has them critique each other's responses, and synthesizes the best insights into a single actionable answer.

**The 3-Stage Process:**

1. **Stage 1: First Opinions** - Your query is sent to all council members (e.g., GPT-5.1, Gemini 3 Pro, Claude Sonnet 4.5, Grok 4). Each responds independently.
2. **Stage 2: Peer Review** - Each model reviews and ranks the other responses (anonymized to prevent bias), evaluating accuracy and insight.
3. **Stage 3: Chairman's Verdict** - A designated Chairman LLM synthesizes all responses and reviews into a single, refined final answer.

This approach reduces hallucinations, surfaces diverse perspectives, and produces more reliable outputs for complex questions.

## Enhancements in This Fork

### MCP Server Support
- **Native Claude Integration**: Consult the Council directly from Claude Code as a tool
- **Use in Any Project**: Bring the Council's wisdom to any codebase without switching windows
- **Stateless Execution**: Runs pure logic in-memory, keeping your chat history clean
- **Easy Installation**: One-line install via `uvx` (no cloning required)

### Dark Mode Support
- **Toolbar with Theme Switcher**: Toggle button to switch between light and dark modes
- **Persistent Theme Preference**: Your theme choice is saved to localStorage
- **Smooth Transitions**: All UI elements smoothly transition between themes

### Multimodal Support
- **File Attachments**: Send images and files along with your queries
- **Supported File Types**: Images (PNG, JPEG, WebP, GIF), Documents (PDF, Plain text)

### Documentation
- Comprehensive architecture documentation in `docs/architecture-council.md`
- Detailed attachment handling guide in `docs/architecture-attachments.md`

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
  -- uvx --from git+ssh://git@github.com/NabilAttia123/llm-council-mcp.git \
  llm-council \
  --council-models "openai/gpt-5.1,google/gemini-3-pro-preview,anthropic/claude-sonnet-4.5,x-ai/grok-4.1-fast" \
  --chairman-model "openai/gpt-5.1"
```
*Note: You can customize the models directly in this command by changing the `--council-models` and `--chairman-model` flags.*

**Manual Configuration**:
If you prefer adding to your Claude settings manually:

```json
{
  "mcpServers": {
    "llm-council": {
      "command": "uvx",
      "args": [
        "--from",
        "git+ssh://git@github.com/NabilAttia123/llm-council-mcp.git",
        "llm-council",
        "--council-models", "openai/gpt-5.1,google/gemini-3-pro-preview,anthropic/claude-sonnet-4.5,x-ai/grok-4.1-fast",
        "--chairman-model", "openai/gpt-5.1"
      ],
      "env": {
        "OPENROUTER_API_KEY": "sk-or-v1-YOUR-KEY"
      }
    }
  }
}
```

*Note: Replace `sk-or-v1-YOUR-KEY` with your actual OpenRouter API Key from [openrouter.ai](https://openrouter.ai/).*

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