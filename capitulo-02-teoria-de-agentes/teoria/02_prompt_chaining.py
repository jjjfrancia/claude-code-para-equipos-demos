"""Ejemplo 02 · Prompt chaining con gate: reformular → buscar → redactar → GATE por código → adaptar a la app.

Concepto (Building effective agents): la tarea se descompone en una secuencia fija; cada llamada procesa la salida
de la anterior, y un chequeo programático («gate») entre pasos comprueba que el proceso sigue en curso.

Caso 1 del Marketplace de Créditos: una pregunta de un solicitante sobre tasas, respondida con el Tarifario.

Qué observar: el gate NO es el modelo. Es código que rechaza la respuesta si no cita página, si cita una página
que la búsqueda no devolvió o si escribe una tasa o un monto que no está en los párrafos («nunca inventa una tasa
ni una comisión»). Una respuesta rechazada nunca llega al paso 3 ni al cliente.
Corre con: python 02_prompt_chaining.py "¿Qué tasa pagaría por S/ 10,000 a 24 meses?"
"""
import sys

import anthropic

from politicas_corpus import (MODELO, MODELO_RAPIDO, TARIFARIO, buscar, cifras_sin_soporte, cita, formatear,
                              verificar_citas)

sys.stdout.reconfigure(encoding='utf-8')
client = anthropic.Anthropic()


def llamar(modelo: str, system: str, usuario: str, max_tokens: int = 700) -> str:
    r = client.messages.create(model=modelo, max_tokens=max_tokens, system=system,
                               messages=[{'role': 'user', 'content': usuario}])
    return ''.join(b.text for b in r.content if b.type == 'text').strip()


def gate(respuesta: str, parrafos: list[dict]) -> tuple[bool, str]:
    ok, motivo = verificar_citas(respuesta, parrafos)
    if not ok:
        return False, motivo
    inventadas = cifras_sin_soporte(respuesta, parrafos)
    if inventadas:
        return False, f'escribe cifras que no están en los párrafos: {inventadas}'
    return True, motivo


def main(pregunta: str) -> None:
    # Paso 1 · reformular (modelo rápido)
    consulta = llamar(MODELO_RAPIDO, 'Convierte la pregunta del cliente en una consulta de búsqueda breve con los términos '
                                     'que usaría el Reglamento de Productos y Tarifario de un banco. Devuelve solo la '
                                     'consulta, sin comillas.', pregunta, 60)
    print(f'[1] consulta: {consulta}')
    parrafos = buscar(consulta, documento=TARIFARIO)
    print(f'    búsqueda: {len(parrafos)} párrafos: {[cita(p) for p in parrafos]}')

    # Paso 2 · redactar solo con los párrafos
    respuesta = llamar(MODELO, 'Eres el asistente de respuesta a clientes del Marketplace de Créditos. Responde SOLO con '
                               'los párrafos entregados. Termina cada afirmación con su cita, por ejemplo (Tarifario, p. 6). '
                               'Nunca inventes ni calcules una tasa o una comisión que no esté escrita en los párrafos. '
                               'Si los párrafos no responden la pregunta, escribe exactamente: NO_ESTA_EN_EL_TARIFARIO.',
                       f'Pregunta: {pregunta}\n\nPárrafos:\n{formatear(parrafos)}')
    print(f'[2] borrador:\n{respuesta}\n')

    if 'NO_ESTA_EN_EL_TARIFARIO' in respuesta:
        print('No está en el Tarifario: el cliente recibe «No encuentro esa información. ¿Quieres que te derive con un '
              'ejecutivo?».')
        return

    # Gate programático
    ok, motivo = gate(respuesta, parrafos)
    print(f'[gate] {"PASA" if ok else "RECHAZA"}: {motivo}')
    if not ok:
        print('La cadena se detiene: nada llega al cliente.')
        return

    # Paso 3 · adaptar al canal
    final = llamar(MODELO_RAPIDO, 'Reescribe el texto como mensaje para el chat de la app del banco, en un máximo de 700 '
                                  'caracteres y en tono cordial. Conserva TODAS las cifras y las citas (Tarifario, p. N) '
                                  'tal como están. No agregues información.', respuesta, 400)
    ok3, motivo3 = gate(final, parrafos)
    print(f'[3] mensaje para la app ({len(final)} caracteres, gate: {"PASA" if ok3 else "RECHAZA"} · {motivo3}):\n{final}')


if __name__ == '__main__':
    main(' '.join(sys.argv[1:]) or '¿Qué tasa pagaría por S/ 10,000 a 24 meses?')
