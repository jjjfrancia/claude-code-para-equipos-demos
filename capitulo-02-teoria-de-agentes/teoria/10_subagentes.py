"""Ejemplo 10 · Subagente verificador con contexto limpio: quien redacta no es quien califica.

Concepto (sub-agents, Agent SDK subagents): un subagente corre con su propia ventana de contexto, su prompt y sus
tools, y devuelve solo su resultado al agente principal. Aquí el verificador no ve el razonamiento del redactor:
solo la respuesta y el documento, así que evalúa el resultado por sí mismo.

Qué observar: los hooks SubagentStart y SubagentStop marcan cuándo nace y termina el subagente; el verificador usa
un modelo más barato (haiku) y solo puede buscar, no escribir.
Requiere: pip install claude-agent-sdk · ANTHROPIC_API_KEY
"""
import asyncio
import sys

from claude_agent_sdk import (AgentDefinition, AssistantMessage, ClaudeAgentOptions, HookMatcher, ResultMessage,
                              ToolUseBlock, create_sdk_mcp_server, query, tool)

from tutor_corpus import buscar, formatear

sys.stdout.reconfigure(encoding='utf-8')


@tool('buscar_documento', 'Párrafos de la Guía Scrum 2020 para una consulta, formato «[p. N] texto», o NO_ENCONTRADO.',
      {'consulta': str})
async def buscar_documento(args):
    return {'content': [{'type': 'text', 'text': formatear(buscar(args['consulta']))}]}


async def al_iniciar(input_data, tool_use_id, context):
    print(f"   ▶ SubagentStart · tipo: {input_data.get('agent_type', '?')} · id: {str(input_data.get('agent_id', ''))[:8]}")
    return {}


async def al_terminar(input_data, tool_use_id, context):
    print(f"   ■ SubagentStop · tipo: {input_data.get('agent_type', '?')}")
    return {}


VERIFICADOR = AgentDefinition(
    description='Verificador de citas. Úsalo SIEMPRE antes de dar por terminada una respuesta al alumno.',
    prompt=('Recibes una respuesta del Tutor. Tu trabajo es intentar REFUTARLA contra la Guía Scrum 2020. '
            'Para cada afirmación, busca con buscar_documento y comprueba que la página citada la contiene. '
            'Devuelve solo: VEREDICTO: APROBADA o VEREDICTO: RECHAZADA, y la lista de afirmaciones sin soporte. '
            'No reescribas la respuesta y no opines sobre el estilo.'),
    tools=['mcp__tutor__buscar_documento'],
    model='haiku',
)


async def main(pregunta: str) -> None:
    opciones = ClaudeAgentOptions(
        system_prompt=('Eres el Tutor. 1) Busca y redacta una respuesta citando la página (p. N). '
                       '2) Pasa tu respuesta al subagente verificador. 3) Si la rechaza, corrige solo lo señalado y vuelve a verificar '
                       'una vez. 4) Entrega la respuesta final y el veredicto.'),
        mcp_servers={'tutor': create_sdk_mcp_server(name='tutor', version='1.0.0', tools=[buscar_documento])},
        agents={'verificador': VERIFICADOR},
        allowed_tools=['mcp__tutor__buscar_documento', 'Agent'],
        disallowed_tools=['Bash', 'Write', 'Edit'],
        hooks={'SubagentStart': [HookMatcher(hooks=[al_iniciar])], 'SubagentStop': [HookMatcher(hooks=[al_terminar])]},
        max_turns=12, max_budget_usd=0.40, model='claude-sonnet-5',
    )
    async for m in query(prompt=pregunta, options=opciones):
        if isinstance(m, AssistantMessage):
            for b in m.content:
                if isinstance(b, ToolUseBlock):
                    detalle = b.input.get('subagent_type') or b.input.get('consulta') or ''
                    print(f'→ {b.name} {detalle}')
        elif isinstance(m, ResultMessage):
            print(f'\nsubtype: {m.subtype} · turnos: {m.num_turns} · costo USD (incluye subagentes): {m.total_cost_usd}')
            if m.subtype == 'success':
                print('\n' + (m.result or ''))


if __name__ == '__main__':
    asyncio.run(main(' '.join(sys.argv[1:]) or '¿Qué compromisos tiene cada artefacto de Scrum?'))
