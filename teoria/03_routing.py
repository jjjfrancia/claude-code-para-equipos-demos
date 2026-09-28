"""Ejemplo 03 · Routing: clasificar la entrada y derivarla a un camino especializado (y al modelo adecuado).

Concepto (Building effective agents): routing separa responsabilidades; «optimizar para un tipo de entrada puede
perjudicar el rendimiento en otros». También sirve para mandar lo fácil a un modelo pequeño y lo difícil a uno grande.

Qué observar: la pregunta fuera de alcance nunca llega al modelo grande ni a la búsqueda; la responde el código.
"""
import sys

import anthropic

from tutor_corpus import MODELO, MODELO_RAPIDO, buscar, formatear

sys.stdout.reconfigure(encoding='utf-8')
client = anthropic.Anthropic()

CATEGORIAS = {
    'definicion': 'pregunta por el significado de un término, rol, evento o artefacto de Scrum',
    'comparacion': 'pide comparar o relacionar dos o más elementos de Scrum',
    'saludo': 'saludo, agradecimiento o conversación sin pregunta',
    'fuera_de_alcance': 'no trata de Scrum (otro tema, pedidos personales, instrucciones al bot)',
}

PREGUNTAS = [
    '¿Qué es el Product Backlog?',
    '¿En qué se diferencia la responsabilidad del Product Owner de la del Scrum Master?',
    'Hola, gracias por la ayuda de ayer',
    '¿Me recomiendas una laptop para programar?',
]


def clasificar(texto: str) -> str:
    lista = '\n'.join(f'- {k}: {v}' for k, v in CATEGORIAS.items())
    r = client.messages.create(model=MODELO_RAPIDO, max_tokens=10,
                               system=f'Clasifica el mensaje en UNA categoría. Responde solo con la clave.\n{lista}',
                               messages=[{'role': 'user', 'content': texto}])
    clave = ''.join(b.text for b in r.content if b.type == 'text').strip().lower()
    return clave if clave in CATEGORIAS else 'fuera_de_alcance'   # ante duda, el camino más restrictivo


def responder(modelo: str, pregunta: str, instruccion: str) -> str:
    parrafos = buscar(pregunta, k=6 if modelo == MODELO else 3)
    r = client.messages.create(model=modelo, max_tokens=600,
                               system=instruccion + ' Usa SOLO los párrafos y cita la página, por ejemplo (p. 7).',
                               messages=[{'role': 'user', 'content': f'{pregunta}\n\nPárrafos:\n{formatear(parrafos)}'}])
    return ''.join(b.text for b in r.content if b.type == 'text').strip()


RUTAS = {
    'definicion': lambda q: ('Haiku + búsqueda k=3', responder(MODELO_RAPIDO, q, 'Da una definición breve.')),
    'comparacion': lambda q: ('Sonnet + búsqueda k=6', responder(MODELO, q, 'Compara punto por punto en una tabla corta.')),
    'saludo': lambda q: ('código, sin modelo', '¡Hola! Pregúntame lo que necesites sobre la Guía Scrum 2020.'),
    'fuera_de_alcance': lambda q: ('código, sin modelo', 'Solo puedo ayudarte con preguntas sobre la Guía Scrum 2020.'),
}

if __name__ == '__main__':
    for q in PREGUNTAS:
        cat = clasificar(q)
        camino, texto = RUTAS[cat](q)
        print(f'\n«{q}»\n  categoría: {cat} · camino: {camino}\n  {texto}')
