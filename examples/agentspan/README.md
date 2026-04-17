# Agentspan Examples

These examples mirror the standard openai-agents examples, with **one line changed** to run on [Agentspan](https://agentspan.ai) instead of directly against OpenAI.

Agentspan adds durability, observability, human-in-the-loop, and horizontal scaling — without touching agent or tool definitions.

## The only change required

```python
# Before — runs directly against OpenAI
from agents import Runner

# After — runs on Agentspan
from agents.extensions.agentspan import AgentspanRunner as Runner
```

## Setup

1. Install the Agentspan extra:
   ```bash
   pip install openai-agents[agentspan]
   ```

2. Start the Agentspan server (or use the hosted version):
   ```bash
   # Local dev server
   AGENTSPAN_SERVER_URL=http://localhost:6767/api
   ```

3. Run any example:
   ```bash
   python -m examples.agentspan.01_hello_world
   python -m examples.agentspan.02_tools
   python -m examples.agentspan.03_streaming
   python -m examples.agentspan.04_handoffs
   python -m examples.agentspan.05_sandbox
   ```

## What Agentspan adds

| | Standard `Runner` | `AgentspanRunner` |
|---|---|---|
| Execute agents | ✅ | ✅ |
| Durable (survives crashes) | ❌ | ✅ |
| Full execution history | ❌ | ✅ |
| Human-in-the-loop pauses | ❌ | ✅ |
| Distributed tool workers | ❌ | ✅ |
| Observability UI | ❌ | ✅ |

## Examples

| File | Based on | What it shows |
|---|---|---|
| `01_hello_world.py` | `basic/hello_world.py` | Minimal agent — one line changed |
| `02_tools.py` | `basic/tools.py` | Function tools with `@function_tool` |
| `03_streaming.py` | `basic/stream_text.py` | Streaming events via `run_streamed()` |
| `04_handoffs.py` | `agent_patterns/routing.py` | Multi-agent handoffs |
| `05_sandbox.py` | `sandbox/basic.py` | Sandbox agent (Docker/Modal) |
