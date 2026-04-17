"""Streaming — identical to examples/basic/stream_text.py with one line changed.

Change:
    # Before
    from agents import Runner

    # After
    from agents.extensions.agentspan import AgentspanRunner as Runner

AgentspanRunner.run_streamed() returns an Agentspan AsyncAgentStream.
Events are yielded as they arrive from the Agentspan server's SSE endpoint.

Note: Agentspan event types differ slightly from openai-agents StreamEvents.
For simple streaming output, iterate and check event.type == "done" or "message".
Full event type reference: https://docs.agentspan.ai/python-sdk/api-reference

Requirements:
    pip install openai-agents[agentspan]
    AGENTSPAN_SERVER_URL=http://localhost:6767/api  (default)
"""

import asyncio

from agents import Agent

# ── Only this line changes ──────────────────────────────────────────────────
# from agents import Runner                                    # original
from agents.extensions.agentspan import AgentspanRunner as Runner  # agentspan
# ───────────────────────────────────────────────────────────────────────────


async def main():
    agent = Agent(
        name="Joker",
        instructions="You are a helpful assistant.",
    )

    stream = await Runner.run_streamed(agent, input="Please tell me 5 jokes.")

    # Agentspan streams AgentEvent objects. Print content as it arrives.
    async for event in stream:
        if event.type in ("thinking", "message"):
            print(event.content or "", end="", flush=True)
        elif event.type == "done":
            # Final output is also available on the result after iteration.
            break

    result = await stream.get_result()
    print("\n\nFinal output:", result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
