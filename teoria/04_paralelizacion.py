"""Ejemplo 04 · Parallelization: sectioning (tareas independientes a la vez) y voting (la misma tarea varias veces).

Concepto (Building effective agents): varias llamadas simultáneas con agregación por código. La guía señala que
un guardrail en una llamada separada rinde mejor que pedirle a la misma llamada que responda y se vigile.

Qué observar: las tres secciones corren a la vez (mira el tiempo total contra la suma), y la decisión final del voto
la toma el código por mayoría, no un modelo.
"""
import asyncio
import sys
import time

import anthropic

from tutor_corpus import MODELO, MODELO_RAPIDO, buscar, formatear

sys.stdout.reconfigure(encoding='utf-8')
client = anthropic.AsyncAnthropic()


async def llamar(etiqueta: str, modelo: str, system: str, usuario: str, max_tokens: int = 500) -> tuple[str, str, float]:
    t0 = time.perf_counter()
    r = await client.messages.create(model=modelo, max_tokens=max_tokens, system=system,
                                     messages=[{'role': 'user', 'content': usuario}])
    return etiqueta, ''.join(b.text for b in r.content if b.type == 'text').strip(), time.perf_counter() - t0


async def main(pregunta: str) -> None:
    parrafos = buscar(pregunta)
    contexto = f'Pregunta: {pregunta}\n\nPárrafos:\n{formatear(parrafos)}'

    # Sectioning: tres aspectos independientes, en paralelo
    t0 = time.perf_counter()
    secciones = await asyncio.gather(
        llamar('redacción', MODELO, 'Responde SOLO con los párrafos y cita la página (p. N).', contexto),
        llamar('términos clave', MODELO_RAPIDO, 'Lista los 3 términos de Scrum que el alumno debe conocer para entender la respuesta, con la página donde aparecen.', contexto),
        llamar('pregunta de repaso', MODELO_RAPIDO, 'Escribe una pregunta de repaso de opción múltiple (4 opciones) basada solo en los párrafos.', contexto),
    )
    total = time.perf_counter() - t0
    for etiqueta, texto, seg in secciones:
        print(f'── {etiqueta} ({seg:.1f} s)\n{texto}\n')
    print(f'tiempo total en paralelo: {total:.1f} s · suma de las tres: {sum(s for _, _, s in secciones):.1f} s\n')

    # Voting: tres revisores con enfoques distintos sobre la redacción
    respuesta = secciones[0][1]
    revision = f'Párrafos:\n{formatear(parrafos)}\n\nRespuesta a revisar:\n{respuesta}'
    enfoques = [
        '¿La respuesta contiene alguna afirmación que NO esté en los párrafos? Responde solo SI o NO.',
        '¿Alguna página citada no corresponde al párrafo del que sale la afirmación? Responde solo SI o NO.',
        '¿La respuesta añade ejemplos, cifras o recomendaciones que los párrafos no mencionan? Responde solo SI o NO.',
    ]
    votos = await asyncio.gather(*[llamar(f'revisor {i + 1}', MODELO_RAPIDO, e, revision, 5) for i, e in enumerate(enfoques)])
    problemas = sum(1 for _, v, _ in votos if v.upper().startswith('SI'))
    for etiqueta, v, _ in votos:
        print(f'{etiqueta}: {v}')
    print(f'\ndecisión por mayoría (código): {"BLOQUEAR, revisar a mano" if problemas >= 2 else "ENVIAR"} ({problemas}/3 marcaron problema)')


if __name__ == '__main__':
    asyncio.run(main(' '.join(sys.argv[1:]) or '¿Qué es el Incremento y cuándo se considera terminado?'))
