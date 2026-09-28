"""Ejemplo 07 · Agente autónomo con el Claude Agent SDK: el mismo bucle, tools y gestión de contexto de Claude Code.

Concepto (Agent SDK, agent-loop): el modelo decide sus pasos; el harness decide qué tools existen, cuáles corren
solas, cuántos turnos y cuánto dinero como máximo. El ResultMessage dice CÓMO terminó (subtype) y cuánto costó.

Qué observar: cada tool call que el agente decide hacer, el subtype del resultado (success, error_max_turns,
error_max_budget_usd…), los turnos y el costo. Prueba con max_turns=1 para ver error_max_turns.
Requiere: pip install claude-agent-sdk · ANTHROPIC_API_KEY
"""
import asyncio
import sys

from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, ResultMessage, SystemMessage, TextBlock,
                              ToolUseBlock, create_sdk_mcp_server, query, tool)

from tutor_corpus import buscar, formatear

sys.stdout.reconfigure(encoding='utf-8')


@tool('buscar_documento',
      'Devuelve los párrafos de la Guía Scrum 2020 que responden la consulta, en formato «[p. N] texto», '
      'o NO_ENCONTRADO. Puedes llamarla varias veces con consultas distintas.',
      {'consulta': str})
async def buscar_documento(args):
    return {'content': [{'type': 'text', 'text': formatear(buscar(args['consulta']))}]}


tutor = create_sdk_mcp_server(name='tutor', version='1.0.0', tools=[buscar_documento])


async def main(pregunta: str, max_turns: int) -> None:
    opciones = ClaudeAgentOptions(
        system_prompt=('Eres el Tutor de proyectos. Responde SOLO con lo que devuelva buscar_documento y cita la página (p. N) '
                       'de cada afirmación. Si la pregunta tiene varias partes, busca cada una. Si no está en el documento, dilo.'),
        mcp_servers={'tutor': tutor},
        allowed_tools=['mcp__tutor__buscar_documento'],       # la única acción que corre sola
        disallowed_tools=['Bash', 'Write', 'Edit', 'WebFetch', 'WebSearch'],   # guardrail: no toca disco ni red
        max_turns=max_turns,                                   # condición de parada por turnos
        max_budget_usd=0.25,                                   # condición de parada por gasto
        model='claude-sonnet-5',
    )
    async for m in query(prompt=pregunta, options=opciones):
        if isinstance(m, SystemMessage) and m.subtype == 'init':
            print(f"sesión {m.data.get('session_id', '')[:8]}… · tools disponibles: {len(m.data.get('tools', []))}")
        elif isinstance(m, AssistantMessage):
            for b in m.content:
                if isinstance(b, ToolUseBlock):
                    print(f'→ tool: {b.name} {b.input}')
                elif isinstance(b, TextBlock) and b.text.strip():
                    print(f'  (texto) {b.text.strip()[:120]}')
        elif isinstance(m, ResultMessage):
            print(f'\nsubtype: {m.subtype} · turnos: {m.num_turns} · costo USD: {m.total_cost_usd} · stop_reason: {m.stop_reason}')
            if m.subtype == 'success':
                print('\n' + (m.result or ''))


if __name__ == '__main__':
    turnos = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 6
    texto = ' '.join(a for a in sys.argv[1:] if not a.isdigit()) or \
        '¿Cuánto dura como máximo el Daily Scrum y quién participa? ¿Y la Sprint Review?'
    asyncio.run(main(texto, turnos))
