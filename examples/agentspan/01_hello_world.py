"""Hello world — identical to examples/basic/hello_world.py with one line changed.

Change:
    # Before
    from agents import Runner

    # After
    from agents.extensions.agentspan import AgentspanRunner as Runner

Everything else is unchanged. The agent now runs on Agentspan — each execution
is persisted, observable in the Agentspan UI, and resilient to process restarts.

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
        name="Assistant",
        instructions="You only respond in haikus.",
    )

    result = await Runner.run(agent, "Tell me about recursion in programming.")
    print(result.final_output)
    # Function calls itself,
    # Looping in smaller pieces,
    # Endless by design.


if __name__ == "__main__":
    asyncio.run(main())
