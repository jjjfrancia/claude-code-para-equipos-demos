"""Ejemplo 11 · Memoria de sesión: reanudar una sesión (resume) y bifurcarla (fork) con el Agent SDK.

Concepto (agent-loop, sessions): la ventana de contexto no se reinicia entre turnos de una sesión. Con el
session_id del ResultMessage se reanuda la sesión y se restaura todo lo anterior (lo que se buscó, lo que se
respondió). Bifurcar crea una rama nueva desde ese punto sin modificar la original.

Qué observar: en la 2ª consulta el agente responde sobre «lo que dijiste antes» sin volver a buscar (0 tool calls),
porque el contexto se restauró. En la 3ª (fork) la sesión original no cambia: su id sigue siendo el mismo.
Requiere: pip install claude-agent-sdk · ANTHROPIC_API_KEY
"""
import asyncio
import sys

from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, ResultMessage, ToolUseBlock, create_sdk_mcp_server,
                              query, tool)

from tutor_corpus import buscar, formatear

sys.stdout.reconfigure(encoding='utf-8')


@tool('buscar_documento', 'Párrafos de la Guía Scrum 2020, formato «[p. N] texto», o NO_ENCONTRADO.', {'consulta': str})
async def buscar_documento(args):
    return {'content': [{'type': 'text', 'text': formatear(buscar(args['consulta']))}]}


def opciones(**extra) -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        system_prompt='Eres el Tutor. Busca con buscar_documento y cita la página (p. N).',
        mcp_servers={'tutor': create_sdk_mcp_server(name='tutor', version='1.0.0', tools=[buscar_documento])},
        allowed_tools=['mcp__tutor__buscar_documento'], disallowed_tools=['Bash', 'Write', 'Edit'],
        max_turns=6, max_budget_usd=0.20, model='claude-sonnet-5', **extra)


async def consultar(etiqueta: str, prompt: str, **extra) -> str | None:
    tools, sid = 0, None
    async for m in query(prompt=prompt, options=opciones(**extra)):
        if isinstance(m, AssistantMessage):
            tools += sum(1 for b in m.content if isinstance(b, ToolUseBlock))
        elif isinstance(m, ResultMessage):
            sid = m.session_id
            print(f'[{etiqueta}] session_id={sid[:8]}… · tool calls={tools} · turnos={m.num_turns} · costo USD={m.total_cost_usd}')
            print('   ' + (m.result or m.subtype)[:350].replace('\n', '\n   ') + '\n')
    return sid


async def main() -> None:
    sid = await consultar('1 · nueva', '¿Qué es el Sprint Goal y quién lo define?')
    await consultar('2 · resume', 'Resume en una sola frase lo que me respondiste antes y dime de qué página salió.', resume=sid)
    fork = await consultar('3 · fork', 'Ahora explícamelo como si fuera un alumno de primer ciclo.', resume=sid, fork_session=True)
    print(f'sesión original: {sid[:8]}… · rama nueva: {(fork or "")[:8]}… · ¿son distintas? {"SÍ" if fork and fork != sid else "NO"}')


if __name__ == '__main__':
    asyncio.run(main())
