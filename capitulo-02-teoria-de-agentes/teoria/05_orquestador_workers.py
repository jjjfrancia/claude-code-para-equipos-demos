"""Ejemplo 05 · Orchestrator-workers: un orquestador descompone, los workers resuelven en paralelo y un sintetizador une.

Concepto (Building effective agents): a diferencia de la paralelización, «las subtareas no están predefinidas:
las determina el orquestador según la entrada».

Qué observar: el número de subpreguntas cambia con la pregunta compuesta. Cada worker busca con SU subpregunta,
así que recupera párrafos distintos, y el sintetizador conserva las citas de cada uno.
"""
import asyncio
import json
import re
import sys

import anthropic

from tutor_corpus import MODELO, MODELO_RAPIDO, buscar, formatear, paginas_citadas

sys.stdout.reconfigure(encoding='utf-8')
client = anthropic.AsyncAnthropic()


async def texto(modelo: str, system: str, usuario: str, max_tokens: int = 700) -> str:
    r = await client.messages.create(model=modelo, max_tokens=max_tokens, system=system,
                                     messages=[{'role': 'user', 'content': usuario}])
    return ''.join(b.text for b in r.content if b.type == 'text').strip()


def _json(crudo: str) -> dict:
    m = re.search(r'\{.*\}', crudo, re.S)
    return json.loads(m.group(0)) if m else {}


async def orquestar(pregunta: str) -> list[str]:
    crudo = await texto(MODELO, 'Descompón la pregunta en las subpreguntas mínimas e independientes que hay que responder '
                                'con la Guía Scrum 2020 para contestarla completa. Entre 1 y 5. '
                                'Devuelve solo JSON: {"subpreguntas": ["...", "..."]}', pregunta, 300)
    subs = _json(crudo).get('subpreguntas') or [pregunta]
    return [s for s in subs if isinstance(s, str) and s.strip()][:5]


async def worker(i: int, sub: str) -> dict:
    parrafos = buscar(sub)
    resp = await texto(MODELO_RAPIDO, 'Responde SOLO con los párrafos, en 2 a 4 frases, citando la página (p. N).',
                       f'{sub}\n\nPárrafos:\n{formatear(parrafos)}', 350)
    return {'n': i, 'subpregunta': sub, 'paginas': [p['pagina'] for p in parrafos], 'respuesta': resp}


async def main(pregunta: str) -> None:
    subs = await orquestar(pregunta)
    print(f'orquestador: {len(subs)} subpreguntas')
    resultados = await asyncio.gather(*[worker(i + 1, s) for i, s in enumerate(subs)])
    for r in resultados:
        print(f"\n[worker {r['n']}] {r['subpregunta']}\n  páginas recuperadas: {r['paginas']}\n  {r['respuesta']}")
    bloque = '\n\n'.join(f"Subpregunta: {r['subpregunta']}\nRespuesta: {r['respuesta']}" for r in resultados)
    final = await texto(MODELO, 'Une las respuestas en una sola respuesta coherente para el alumno. Conserva TODAS las citas '
                                '(p. N) exactamente. No agregues nada que no esté en las respuestas.',
                        f'Pregunta original: {pregunta}\n\n{bloque}', 900)
    print(f'\n── síntesis (páginas citadas: {sorted(paginas_citadas(final))})\n{final}')


if __name__ == '__main__':
    asyncio.run(main(' '.join(sys.argv[1:]) or
                     'Compara lo que hacen el Product Owner y el Scrum Master durante la Sprint Planning y la Sprint Review.'))
