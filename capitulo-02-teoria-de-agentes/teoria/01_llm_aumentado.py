"""Ejemplo 01 · El LLM aumentado: un modelo con una tool de recuperación y el bucle de tool use escrito a mano.

Concepto (Building effective agents): el bloque básico de todo sistema agéntico es un LLM con recuperación,
tools y memoria, capaz de generar sus propias consultas de búsqueda.

Caso 1 del Marketplace de Créditos: el asistente que responde a solicitantes e inversionistas en la app, solo con
el Reglamento de Productos y Tarifario, citando la página.

Qué observar: la consulta que el MODELO decide enviar a buscar_politica no es la pregunta del cliente; la reformula
con los términos del documento, y elige en cuál de los dos documentos buscar.
Corre con: python 01_llm_aumentado.py "¿Qué necesito para pedir un préstamo?"
"""
import sys

import anthropic

from politicas_corpus import MODELO, POLITICA, TARIFARIO, buscar, cita, formatear

sys.stdout.reconfigure(encoding='utf-8')

TOOLS = [{
    'name': 'buscar_politica',
    'description': ('Busca en los documentos del Marketplace de Créditos los párrafos que responden una consulta y los '
                    'devuelve con su documento y página en el formato «[Tarifario, p. N] texto». Devuelve NO_ENCONTRADO '
                    'si ningún párrafo coincide. Úsala antes de responder cualquier pregunta sobre requisitos, tasas, '
                    'plazos, comisiones, inversiones o reclamos. Escribe la consulta con los términos que usaría el '
                    'documento (por ejemplo «requisitos solicitar préstamo personas naturales»), no la pregunta literal.'),
    'input_schema': {
        'type': 'object',
        'properties': {
            'consulta': {'type': 'string'},
            'documento': {'type': 'string', 'enum': [TARIFARIO, POLITICA],
                          'description': 'Opcional. Tarifario para clientes; Política de Créditos para la evaluación.'},
        },
        'required': ['consulta'],
    },
}]

SYSTEM = ('Eres el asistente de respuesta a clientes del Marketplace de Créditos. Respondes a solicitantes e '
          'inversionistas usando SOLO lo que devuelva buscar_politica, y terminas cada afirmación con su cita entre '
          'paréntesis, por ejemplo (Tarifario, p. 4). Nunca inventes una tasa ni una comisión. Si la herramienta '
          'devuelve NO_ENCONTRADO, dilo y ofrece derivar la consulta a un ejecutivo. Nunca pidas ni muestres el número '
          'completo de una tarjeta, una clave ni un CVV.')


def main(pregunta: str) -> None:
    client = anthropic.Anthropic()
    mensajes = [{'role': 'user', 'content': pregunta}]
    turno = 0
    while True:
        turno += 1
        r = client.messages.create(model=MODELO, max_tokens=1024, system=SYSTEM, tools=TOOLS, messages=mensajes)
        print(f'turno {turno}: stop_reason={r.stop_reason} · entrada={r.usage.input_tokens} · salida={r.usage.output_tokens}')
        if r.stop_reason != 'tool_use':
            break
        mensajes.append({'role': 'assistant', 'content': r.content})
        resultados = []
        for bloque in r.content:
            if bloque.type == 'tool_use':
                consulta, documento = bloque.input['consulta'], bloque.input.get('documento')
                parrafos = buscar(consulta, documento=documento)
                print(f'  → el modelo generó la consulta: «{consulta}» en {documento or "ambos documentos"} · '
                      f'{len(parrafos)} párrafos: {[cita(p) for p in parrafos]}')
                resultados.append({'type': 'tool_result', 'tool_use_id': bloque.id, 'content': formatear(parrafos)})
        mensajes.append({'role': 'user', 'content': resultados})
    texto = ''.join(b.text for b in r.content if b.type == 'text')
    print('\nRespuesta:\n' + texto)


if __name__ == '__main__':
    main(' '.join(sys.argv[1:]) or '¿Qué necesito para pedir un préstamo?')
