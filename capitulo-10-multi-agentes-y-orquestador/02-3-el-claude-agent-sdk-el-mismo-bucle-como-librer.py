import asyncio

from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, ResultMessage,
                              ToolUseBlock, query)


async def main():
    opciones = ClaudeAgentOptions(
        cwd="tutor-whatsapp",
        setting_sources=["project"],          # carga CLAUDE.md, reglas, hooks y skills del repositorio
        allowed_tools=["Read", "Grep", "Glob", "Bash(pytest *)"],
        permission_mode="default",            # lo no cubierto se deniega: no hay nadie para aprobarlo
        max_turns=20,
        max_budget_usd=1.00,
    )
    async for m in query(prompt="Corre pytest y explica por qué falla test_ac3", options=opciones):
        if isinstance(m, AssistantMessage):
            for b in m.content:
                if isinstance(b, ToolUseBlock):
                    print("→ tool:", b.name, b.input)
        elif isinstance(m, ResultMessage):
            print(m.subtype, "| turnos:", m.num_turns, "| USD:", m.total_cost_usd)
            if m.subtype == "success":
                print(m.result)


asyncio.run(main())
