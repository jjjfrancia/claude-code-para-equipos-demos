"""Ejemplo 02 · Prompt chaining con gate: reformular → buscar → redactar → GATE por código → resumir para WhatsApp.

Concepto (Building effective agents): la tarea se descompone en una secuencia fija; cada llamada procesa la salida
de la anterior, y un chequeo programático («gate») entre pasos comprueba que el proceso sigue en curso.

Qué observar: el gate NO es el modelo. Es código que rechaza la respuesta si no cita página o si cita una página
que la búsqueda no devolvió. Una respuesta rechazada nunca llega al paso 3.
"""
import sys

import anthropic

from tutor_corpus import MODELO, MODELO_RAPIDO, buscar, formatear, paginas_citadas

sys.stdout.reconfigure(encoding='utf-8')
client = anthropic.Anthropic()


def llamar(modelo: str, system: str, usuario: str, max_tokens: int = 700) -> str:
    r = client.messages.create(model=modelo, max_tokens=max_tokens, system=system,
                               messages=[{'role': 'user', 'content': usuario}])
    return ''.join(b.text for b in r.content if b.type == 'text').strip()


def gate(respuesta: str, parrafos: list[dict]) -> tuple[bool, str]:
    citadas = paginas_citadas(respuesta)
    recuperadas = {p['pagina'] for p in parrafos}
    if not citadas:
        return False, 'la respuesta no cita ninguna página'
    if not citadas <= recuperadas:
        return False, f'cita páginas que la búsqueda no devolvió: {sorted(citadas - recuperadas)}'
    return True, f'cita {sorted(citadas)}, todas dentro de las recuperadas {sorted(recuperadas)}'


def main(pregunta: str) -> None:
    # Paso 1 · reformular (modelo rápido)
    consulta = llamar(MODELO_RAPIDO, 'Convierte la pregunta en una consulta de búsqueda breve con los términos que usaría '
                                     'la Guía Scrum 2020. Devuelve solo la consulta, sin comillas.', pregunta, 60)
    print(f'[1] consulta: {consulta}')
    parrafos = buscar(consulta)
    print(f'    búsqueda: {len(parrafos)} párrafos, páginas {[p["pagina"] for p in parrafos]}')

    # Paso 2 · redactar solo con los párrafos
    respuesta = llamar(MODELO, 'Responde SOLO con los párrafos entregados. Termina cada afirmación con su página, por ejemplo (p. 7). '
                               'Si los párrafos no responden la pregunta, escribe exactamente: NO_ESTA_EN_EL_DOCUMENTO.',
                       f'Pregunta: {pregunta}\n\nPárrafos:\n{formatear(parrafos)}')
    print(f'[2] borrador:\n{respuesta}\n')

    # Gate programático
    ok, motivo = gate(respuesta, parrafos)
    print(f'[gate] {"PASA" if ok else "RECHAZA"}: {motivo}')
    if not ok:
        print('La cadena se detiene: nada llega al alumno.')
        return

    # Paso 3 · adaptar al canal
    final = llamar(MODELO_RAPIDO, 'Reescribe el texto para WhatsApp en un máximo de 700 caracteres. Conserva TODAS las '
                                  'referencias de página tal como están. No agregues información.', respuesta, 400)
    ok3, motivo3 = gate(final, parrafos)
    print(f'[3] mensaje para WhatsApp ({len(final)} caracteres, gate: {motivo3}):\n{final}')


if __name__ == '__main__':
    main(' '.join(sys.argv[1:]) or '¿Qué pasa en la Sprint Retrospective?')
