"""Corpus del Tutor para los ejemplos del capítulo «Teoría de agentes».

Fuente: La Guía de Scrum 2020, Ken Schwaber y Jeff Sutherland, versión en español (Latinoamérica),
descargada de https://scrumguides.org. Licencia Creative Commons Attribution Share-Alike 4.0.

Qué hace este módulo:
- lee el PDF con pdfplumber (la rutina básica de extracción del curso de RAG),
- lo parte en fragmentos de párrafo con su número de página del PDF,
- guarda los fragmentos en datos/guia_fragmentos.json para no releer el PDF en cada corrida,
- y busca por coincidencia léxica ponderada (sin embeddings, para que el ejemplo no dependa de nada más).

La búsqueda es deliberadamente simple: los ejemplos tratan del bucle agéntico, no del RAG. El capítulo
de RAG sustituye esta función por búsqueda híbrida y estructural.
"""
from __future__ import annotations

import json
import math
import os
import re
import unicodedata
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(AQUI, 'datos', 'guia-scrum-2020-es.pdf')
CACHE = os.path.join(AQUI, 'datos', 'guia_fragmentos.json')
FUENTE = 'Guía Scrum 2020'

MODELO = 'claude-sonnet-5'
MODELO_RAPIDO = 'claude-haiku-4-5-20251001'

_VACIAS = set('''a al algo ante antes como con contra cual cuales cuando de del desde donde durante e el ella ellas ellos en entre
es esa esas ese eso esos esta estan estas este esto estos fue ha hace hacen hay la las le les lo los mas me mi muy no nos o
para pero por porque que quien quienes se sea segun ser si sin sobre son su sus tambien te tiene tienen todo todos tu un una
unas uno unos y ya cuanto cuanta cuantos cual es dura debe deben puede pueden'''.split())


def _normalizar(texto: str) -> str:
    t = unicodedata.normalize('NFD', texto.lower())
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn')


def _tokens(texto: str) -> list[str]:
    return [w for w in re.findall(r'[a-z0-9]+', _normalizar(texto)) if w not in _VACIAS and len(w) > 2]


def _extraer() -> list[dict]:
    import pdfplumber

    fragmentos: list[dict] = []
    with pdfplumber.open(PDF) as pdf:
        for n, pagina in enumerate(pdf.pages, 1):
            texto = (pagina.extract_text() or '').strip()
            if n == 3 or len(texto) < 200:          # p. 3 es el índice; p. 1 la portada
                continue
            actual: list[str] = []
            for linea in texto.splitlines():
                linea = linea.strip()
                if not linea:
                    continue
                actual.append(linea)
                cierra = linea.endswith(('.', ':', ';')) or linea.startswith('●')
                if cierra and sum(len(x) for x in actual) >= 350:
                    fragmentos.append({'pagina': n, 'texto': ' '.join(actual)})
                    actual = []
            if actual:
                fragmentos.append({'pagina': n, 'texto': ' '.join(actual)})
    for i, f in enumerate(fragmentos):
        f['id'] = i
    return fragmentos


def fragmentos() -> list[dict]:
    """Todos los fragmentos del documento, con id, página del PDF y texto."""
    if os.path.exists(CACHE) and os.path.getmtime(CACHE) >= os.path.getmtime(PDF):
        with open(CACHE, encoding='utf-8') as f:
            return json.load(f)
    datos = _extraer()
    with open(CACHE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    return datos


def buscar(pregunta: str, k: int = 4) -> list[dict]:
    """Los k fragmentos con mayor puntuación léxica (TF-IDF) para la pregunta. Lista vacía si ninguno coincide."""
    docs = fragmentos()
    tok_docs = [Counter(_tokens(d['texto'])) for d in docs]
    n = len(docs)
    df = Counter(t for c in tok_docs for t in c)
    consulta = set(_tokens(pregunta))
    puntuados = []
    for d, c in zip(docs, tok_docs):
        s = sum((1 + math.log(c[t])) * math.log(1 + n / df[t]) for t in consulta if c[t])
        if s > 0:
            puntuados.append((s, d))
    puntuados.sort(key=lambda x: -x[0])
    return [d for _, d in puntuados[:k]]


def formatear(parrafos: list[dict]) -> str:
    """Formato poka-yoke: siempre «[p. N] texto» o la cadena NO_ENCONTRADO, nunca una lista vacía."""
    if not parrafos:
        return 'NO_ENCONTRADO'
    return '\n\n'.join(f"[p. {p['pagina']}] {p['texto']}" for p in parrafos)


def corpus_completo() -> str:
    """El documento entero con marcas de página: el prefijo estable del ejemplo de prompt caching."""
    return f'{FUENTE} (Schwaber y Sutherland, CC BY-SA 4.0)\n\n' + formatear(fragmentos())


def paginas_citadas(texto: str) -> set[int]:
    return {int(x) for x in re.findall(r'p\.\s*(\d+)', texto)}


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    fs = fragmentos()
    print(f'{len(fs)} fragmentos de {FUENTE}')
    for p in buscar(' '.join(sys.argv[1:]) or '¿Cuánto dura el Daily Scrum?'):
        print(f"- p. {p['pagina']}: {p['texto'][:160]}…")
