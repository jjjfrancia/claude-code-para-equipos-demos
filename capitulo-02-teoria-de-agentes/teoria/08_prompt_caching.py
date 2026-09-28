"""Ejemplo 08 · Prompt caching medido: el documento entero como bloque cacheado del system prompt.

Concepto (API de Anthropic, prompt caching): la API reutiliza el prefijo idéntico de una petición anterior.
El breakpoint (cache_control) va en el último bloque que NO cambia entre peticiones. Escribir la caché cuesta
1,25× el precio de entrada (TTL 5 min); leerla cuesta 0,1×.

Qué observar: la primera llamada escribe la caché (cache_creation > 0, cache_read = 0); la segunda la lee
(cache_creation = 0, cache_read > 0). Si llamas con más de 5 minutos de diferencia, la caché ya expiró.
"""
import sys

import anthropic

from tutor_corpus import MODELO, corpus_completo

sys.stdout.reconfigure(encoding='utf-8')
client = anthropic.Anthropic()
DOCUMENTO = corpus_completo()


def preguntar(pregunta: str) -> anthropic.types.Usage:
    r = client.messages.create(
        model=MODELO, max_tokens=500,
        system=[
            {'type': 'text', 'text': 'Eres el Tutor. Responde solo con el documento y cita la página (p. N).'},
            {'type': 'text', 'text': DOCUMENTO, 'cache_control': {'type': 'ephemeral'}},   # breakpoint
        ],
        messages=[{'role': 'user', 'content': pregunta}],                                  # lo único que cambia
    )
    u = r.usage
    print(f'«{pregunta}»')
    print(f'  escritos en caché: {u.cache_creation_input_tokens or 0:>6} | leídos de caché: {u.cache_read_input_tokens or 0:>6} '
          f'| entrada normal: {u.input_tokens:>4} | salida: {u.output_tokens}')
    print('  ' + ''.join(b.text for b in r.content if b.type == 'text').strip()[:300] + '\n')
    return u


if __name__ == '__main__':
    print(f'documento: {len(DOCUMENTO):,} caracteres\n')
    preguntar('¿Quién es responsable de maximizar el valor del producto?')
    u2 = preguntar('¿Cuánto dura el Sprint como máximo?')
    leidos, normales = u2.cache_read_input_tokens or 0, u2.input_tokens
    if leidos:
        sin_cache = leidos + normales
        con_cache = leidos * 0.1 + normales
        print(f'entrada de la 2ª llamada: {sin_cache} tokens equivalentes sin caché · {con_cache:.0f} con caché · '
              f'ahorro {100 * (1 - con_cache / sin_cache):.0f} % del costo de entrada')
    else:
        print('La 2ª llamada no leyó de la caché: revisa que el bloque cacheado supere el mínimo del modelo '
              'y que nada antes del breakpoint haya cambiado.')
