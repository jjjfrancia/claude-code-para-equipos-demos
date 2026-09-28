"""Los documentos del banco: se parten por página y se buscan por coincidencia léxica (TF-IDF, sin embeddings).

Formato de cita del curso: «[Política de Créditos, p. 7] texto». Si nada coincide, la cadena NO_ENCONTRADO.
Corre con: python -m banco.corpus "¿cuál es la cuota máxima?"
"""
from __future__ import annotations

import math
import os
import re
import unicodedata
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(AQUI, 'documentos')

TITULOS = {
    'politica-de-creditos.md': 'Política de Créditos',
    'politica-de-reclamos.md': 'Política de Reclamos',
    'reglamento-de-atencion.md': 'Reglamento de Atención',
}

_VACIAS = set('''a al algo ante antes como con contra cual cuales cuando de del desde donde durante e el ella ellas ellos en
entre es esa esas ese eso esos esta estan estas este esto estos fue ha hace hacen hay la las le les lo los mas me mi muy no nos
o para pero por porque que quien quienes se sea segun ser si sin sobre son su sus tambien te tiene tienen todo todos tu un una
unas uno unos y ya puede pueden debe deben cuanto cuanta'''.split())


def _normalizar(texto: str) -> str:
    t = unicodedata.normalize('NFD', texto.lower())
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn')


def _tokens(texto: str) -> list[str]:
    return [w for w in re.findall(r'[a-z0-9]+', _normalizar(texto)) if w not in _VACIAS and len(w) > 2]


def fragmentos() -> list[dict]:
    """Una entrada por página: {id, documento, pagina, texto}."""
    salida = []
    for archivo, titulo in TITULOS.items():
        with open(os.path.join(DOCS, archivo), encoding='utf-8') as f:
            contenido = f.read()
        for m in re.finditer(r'^## Página (\d+)\n(.+?)(?=^## Página |\Z)', contenido, re.M | re.S):
            salida.append({'id': len(salida), 'documento': titulo, 'pagina': int(m.group(1)),
                           'texto': m.group(2).strip()})
    return salida


def buscar(consulta: str, k: int = 3, documento: str | None = None) -> list[dict]:
    """Las k páginas con mayor puntuación para la consulta; lista vacía si ninguna coincide."""
    docs = [d for d in fragmentos() if documento in (None, d['documento'])]
    cuentas = [Counter(_tokens(d['texto'])) for d in docs]
    df = Counter(t for c in cuentas for t in c)
    n = len(docs)
    q = set(_tokens(consulta))
    puntuados = []
    for d, c in zip(docs, cuentas):
        s = sum((1 + math.log(c[t])) * math.log(1 + n / df[t]) for t in q if c[t])
        if s > 0:
            puntuados.append((s, d))
    puntuados.sort(key=lambda x: -x[0])
    return [d for _, d in puntuados[:k]]


def formatear(paginas: list[dict]) -> str:
    if not paginas:
        return 'NO_ENCONTRADO'
    return '\n\n'.join(f"[{p['documento']}, p. {p['pagina']}] {p['texto']}" for p in paginas)


def texto_completo(documento: str | None = None) -> str:
    """Todo el corpus (o un documento) con marcas de página: el prefijo estable para prompt caching."""
    return formatear([d for d in fragmentos() if documento in (None, d['documento'])])


def citas(texto: str) -> set[tuple[str, int]]:
    """Las citas «Documento, p. N» que aparecen en un texto."""
    return {(d.strip(), int(p)) for d, p in re.findall(r'(Política de Créditos|Política de Reclamos|Reglamento de Atención),\s*p\.\s*(\d+)', texto)}


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print(formatear(buscar(' '.join(sys.argv[1:]) or '¿cuál es la cuota máxima respecto del ingreso?')))
