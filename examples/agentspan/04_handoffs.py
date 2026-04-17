"""Multi-agent handoffs — identical to examples/agent_patterns/routing.py with one line changed.

Change:
    # Before
    from agents import Runner

    # After
    from agents.extensions.agentspan import AgentspanRunner as Runner

Agentspan records every handoff decision in its execution history, so you can
replay the full agent-to-agent routing in the Agentspan UI after the run.

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

french_agent = Agent(
    name="french_agent",
    instructions="You only speak French",
)

spanish_agent = Agent(
    name="spanish_agent",
    instructions="You only speak Spanish",
)

english_agent = Agent(
    name="english_agent",
    instructions="You only speak English",
)

triage_agent = Agent(
    name="triage_agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[french_agent, spanish_agent, english_agent],
)


async def main():
    result = await Runner.run(
        triage_agent,
        input="Hello, how do I say good evening in French?",
    )
    print(result.final_output)
    # Bonsoir !


if __name__ == "__main__":
    asyncio.run(main())
