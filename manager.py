from __future__ import annotations

import asyncio
import time
from collections.abc import Sequence
from typing import Any

from rich.console import Console

from agents import RunContextWrapper, RunHooks, Runner, RunResult, Tool, Usage, custom_span, gen_trace_id, handoff, trace, Agent

from agents_tools.pdf_generation_agent import pdf_generation_agent
from agents_tools.validation_agent import validation_agent
from agents_tools.completion_agent import completion_agent
from models.Invoice import InvoiceContext

from printer import Printer


class ExampleHooks(RunHooks):
    def __init__(self):
        self.event_counter = 0

    def _usage_to_str(self, usage: Usage) -> str:
        # return f"{usage.requests} requests, {usage.input_tokens} input tokens, {usage.output_tokens} output tokens, {usage.total_tokens} total tokens"
        return f"{usage.total_tokens} tokens"

    async def on_agent_start(self, context: RunContextWrapper, agent: Agent) -> None:
        self.event_counter += 1
        print(
            f"### {self.event_counter}: [Agent] {agent.name} started. 耗费: {self._usage_to_str(context.usage)}"
        )

    async def on_agent_end(self, context: RunContextWrapper, agent: Agent, output: Any) -> None:
        self.event_counter += 1
        print(
            f"### {self.event_counter}: [Agent] {agent.name} ended with output {output}. 耗费: {self._usage_to_str(context.usage)}"
        )

    # async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
    #     self.event_counter += 1
    #     print(
    #         f"### {self.event_counter}: Tool {tool.name} started. "
    #     )

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        self.event_counter += 1
        print(
            # f"### {self.event_counter}: Tool {tool.name} ended with result {result}. 耗费: {self._usage_to_str(context.usage)}"
            f"### {self.event_counter}:\t\t[Tool] {tool.name} ended. 耗费: {self._usage_to_str(context.usage)}\n"
            f"\t\t输出：{result}."
        )

    async def on_handoff(
        self, context: RunContextWrapper, from_agent: Agent, to_agent: Agent
    ) -> None:
        self.event_counter += 1
        print(
            f"### {self.event_counter}: [Handoff]  {from_agent.name} ==> {to_agent.name}. 耗费: {self._usage_to_str(context.usage)}"
        )


hooks = ExampleHooks()
    
    
class InvoiceManager:
    """
    Orchestrates the full flow: completion, validation.
    """

    def __init__(self) -> None:
        self.console = Console()
        self.printer = Printer(self.console)

        # 编排agents
        completion_agent.handoffs = [
            handoff(agent=validation_agent),
        ]
        validation_agent.handoffs = [
            handoff(agent=pdf_generation_agent),
            handoff(agent=completion_agent),
        ]

    async def run(self, context: InvoiceContext) -> None:
        trace_id = gen_trace_id()
        with trace("Invoice manager trace", trace_id=trace_id):
            print(f"\033[4;34mView trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\033[0m")

            final_result = await Runner.run(
                starting_agent=completion_agent,
                input="请开具发票",
                context=context,
                hooks=hooks,
                max_turns=15,
            )
            
            self.printer.end()
