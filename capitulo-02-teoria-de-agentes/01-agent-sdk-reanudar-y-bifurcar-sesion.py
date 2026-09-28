import asyncio
from claude_agent_sdk import (query, ClaudeAgentOptions, ResultMessage, AssistantMessage,
                              ToolUseBlock, tool, create_sdk_mcp_server)
from tutor_corpus import buscar

@tool("buscar_documento", "Devuelve los párrafos de la Guía Scrum que responden a la pregunta, con su página",
      {"pregunta": str})
async def buscar_documento(args):
    parrafos = buscar(args["pregunta"], k=4)
    texto = "\n\n".join(f"[p. {p['pagina']}] {p['texto']}" for p in parrafos) or "NO_ENCONTRADO"
    return {"content": [{"type": "text", "text": texto}]}

tutor = create_sdk_mcp_server(name="tutor", version="1.0.0", tools=[buscar_documento])

async def main():
    opciones = ClaudeAgentOptions(
        system_prompt="Eres el Tutor. Responde SOLO con los párrafos que devuelva buscar_documento y cita la página.",
        mcp_servers={"tutor": tutor},
        allowed_tools=["mcp__tutor__buscar_documento"],   # la única acción que corre sola
        disallowed_tools=["Bash", "Write", "Edit"],        # guardrail: este agente no toca el disco
        max_turns=6, max_budget_usd=0.25,                  # condiciones de parada
        permission_mode="default", model="claude-sonnet-5",
    )
    async for m in query(prompt="¿Cuánto dura como máximo el Daily Scrum?", options=opciones):
        if isinstance(m, AssistantMessage):
            for b in m.content:
                if isinstance(b, ToolUseBlock):
                    print("→ tool:", b.name, b.input)
        elif isinstance(m, ResultMessage):
            print(m.subtype, "| turnos:", m.num_turns, "| costo USD:", m.total_cost_usd)
            if m.subtype == "success":
                print(m.result)

asyncio.run(main())
