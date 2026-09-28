"""Ejemplo 01 · El LLM aumentado: un modelo con una tool de recuperación y el bucle de tool use escrito a mano.

Concepto (Building effective agents): el bloque básico de todo sistema agéntico es un LLM con recuperación,
tools y memoria, capaz de generar sus propias consultas de búsqueda.

Qué observar: la consulta que el MODELO decide enviar a buscar_documento no es la pregunta del alumno; la reformula.
Corre con: python 01_llm_aumentado.py "¿Quién es responsable de maximizar el valor del producto?"
"""
import sys

import anthropic

from tutor_corpus import MODELO, buscar, formatear

sys.stdout.reconfigure(encoding='utf-8')

TOOLS = [{
    'name': 'buscar_documento',
    'description': ('Busca en la Guía Scrum 2020 los párrafos que responden una consulta y los devuelve con su página '
                    'en el formato «[p. N] texto». Devuelve NO_ENCONTRADO si ningún párrafo coincide. '
                    'Úsala antes de responder cualquier pregunta sobre Scrum. Escribe la consulta con los términos '
                    'que usaría la guía (por ejemplo «Product Owner responsable valor»), no la pregunta literal.'),
    'input_schema': {'type': 'object', 'properties': {'consulta': {'type': 'string'}}, 'required': ['consulta']},
}]

SYSTEM = ('Eres el Tutor de proyectos. Respondes preguntas sobre la Guía Scrum 2020 usando SOLO lo que devuelva '
          'buscar_documento, y terminas cada afirmación con su página entre paréntesis, por ejemplo (p. 7). '
          'Si la herramienta devuelve NO_ENCONTRADO, dilo y no respondas de memoria.')


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
                consulta = bloque.input['consulta']
                parrafos = buscar(consulta)
                print(f'  → el modelo generó la consulta: «{consulta}» · {len(parrafos)} párrafos, páginas {[p["pagina"] for p in parrafos]}')
                resultados.append({'type': 'tool_result', 'tool_use_id': bloque.id, 'content': formatear(parrafos)})
        mensajes.append({'role': 'user', 'content': resultados})
    texto = ''.join(b.text for b in r.content if b.type == 'text')
    print('\nRespuesta:\n' + texto)


if __name__ == '__main__':
    main(' '.join(sys.argv[1:]) or '¿Quién es responsable de maximizar el valor del producto?')
