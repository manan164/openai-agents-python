"""Sandbox agent — based on examples/sandbox/basic.py with one line changed.

Change:
    # Before
    from agents import Runner

    # After
    from agents.extensions.agentspan import AgentspanRunner as Runner

Sandbox agents run code in an isolated Docker or Modal environment. With
AgentspanRunner, the sandbox session, tool calls, and model responses are
all recorded in Agentspan — giving you a full audit trail of what the
agent executed inside the sandbox.

Requirements:
    pip install openai-agents[agentspan]
    pip install openai-agents[docker]   # for Docker backend
    pip install openai-agents[modal]    # for Modal backend
    AGENTSPAN_SERVER_URL=http://localhost:6767/api  (default)

Usage:
    python -m examples.agentspan.05_sandbox --backend docker
    python -m examples.agentspan.05_sandbox --backend modal
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Literal, cast

from openai.types.responses import ResponseTextDeltaEvent

from agents import ModelSettings
from agents.run import RunConfig
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.config import DEFAULT_PYTHON_SANDBOX_IMAGE
from agents.sandbox.entries import File

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from examples.sandbox.misc.workspace_shell import WorkspaceShellCapability

# ── Only this line changes ──────────────────────────────────────────────────
# from agents import Runner                                    # original
from agents.extensions.agentspan import AgentspanRunner as Runner  # agentspan
# ───────────────────────────────────────────────────────────────────────────

Backend = Literal["docker", "modal"]

DEFAULT_QUESTION = "Summarize this sandbox project in 2 sentences."
DEFAULT_BACKEND: Backend = "docker"


def _build_manifest(backend: Backend) -> Manifest:
    backend_label = "Docker" if backend == "docker" else "Modal"
    return Manifest(
        entries={
            "README.md": File(
                content=(
                    b"# Demo Project\n\n"
                    + (
                        f"This sandbox contains a tiny demo project for the {backend_label} "
                        "sandbox runner.\n"
                    ).encode()
                    + b"The goal is to show how Runner can prepare a sandbox workspace.\n"
                )
            ),
            "src/app.py": File(
                content=b'def greet(name: str) -> str:\n    return f"Hello, {name}!"\n'
            ),
            "docs/notes.md": File(
                content=(
                    b"# Notes\n\n"
                    b"- The example is intentionally minimal.\n"
                    b"- The model should inspect files through the shell tool.\n"
                )
            ),
        }
    )


def _build_agent(*, model: str, manifest: Manifest, backend: Backend) -> SandboxAgent:
    backend_label = "Docker" if backend == "docker" else "Modal"
    return SandboxAgent(
        name=f"{backend_label} Sandbox Assistant",
        model=model,
        instructions=(
            "Answer questions about the sandbox workspace. Inspect the project before answering, "
            "and keep the response concise. "
            "Do not guess file names like package.json or pyproject.toml. "
            "This demo intentionally contains a tiny workspace."
        ),
        default_manifest=manifest,
        capabilities=[WorkspaceShellCapability()],
        model_settings=ModelSettings(tool_choice="required"),
    )


async def main(model: str, question: str, backend: Backend) -> None:
    manifest = _build_manifest(backend)
    agent = _build_agent(model=model, manifest=manifest, backend=backend)

    # Set up sandbox client — Docker or Modal
    if backend == "docker":
        try:
            from docker import from_env as docker_from_env
            from agents.sandbox.sandboxes.docker import DockerSandboxClient, DockerSandboxClientOptions
        except ImportError as e:
            raise SystemExit(
                "Docker backend requires: pip install openai-agents[docker]\n"
                "Also ensure Docker is running on your machine."
            ) from e
        client = DockerSandboxClient(docker_from_env())
        sandbox = await client.create(
            manifest=manifest,
            options=DockerSandboxClientOptions(image=DEFAULT_PYTHON_SANDBOX_IMAGE),
        )
    else:
        try:
            from agents.extensions.sandbox import ModalSandboxClient, ModalSandboxClientOptions
        except ImportError as e:
            raise SystemExit(
                "Modal backend requires: pip install openai-agents[modal]"
            ) from e
        client = ModalSandboxClient()
        sandbox = await client.create(manifest=manifest, options=ModalSandboxClientOptions())

    await sandbox.start()

    try:
        async with sandbox:
            # AgentspanRunner.run_streamed() — identical call signature to Runner.run_streamed()
            result = Runner.run_streamed(
                agent,
                question,
                run_config=RunConfig(
                    sandbox=SandboxRunConfig(session=sandbox),
                    workflow_name=f"Agentspan {backend.title()} sandbox example",
                ),
            )
            saw_text = False
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(
                    event.data, ResponseTextDeltaEvent
                ):
                    if not saw_text:
                        print("assistant> ", end="", flush=True)
                        saw_text = True
                    print(event.data.delta, end="", flush=True)
                    continue

                if event.type == "run_item_stream_event":
                    if event.name == "tool_called":
                        if saw_text:
                            print()
                            saw_text = False
                        print("[tool call] shell")
                    elif event.name == "tool_output":
                        print("[tool output] shell")

            if saw_text:
                print()
    finally:
        await client.delete(sandbox)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agentspan sandbox agent example")
    parser.add_argument("--model", default="gpt-4o", help="Model to use")
    parser.add_argument("--question", default=DEFAULT_QUESTION, help="Prompt to send")
    parser.add_argument(
        "--backend",
        default=DEFAULT_BACKEND,
        choices=["docker", "modal"],
        help="Sandbox backend",
    )
    args = parser.parse_args()
    asyncio.run(main(args.model, args.question, cast(Backend, args.backend)))
