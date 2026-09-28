"""Corpus de políticas del Marketplace de Créditos para los ejemplos del capítulo «Teoría de agentes».

Fuentes: dos documentos FICTICIOS creados para el curso con datos/generar_documentos.py:
- «Reglamento de Productos y Tarifario» (datos/reglamento-tarifario.pdf) · se cita «Tarifario, p. N».
  Caso 1, respuesta a clientes: requisitos, tasas, plazos, comisiones, cómo invertir, cómo reclamar.
- «Política de Créditos de Consumo» (datos/politica-creditos.pdf) · se cita «Política de Créditos, p. N».
  Caso 2, aprobación de créditos: regla del 30 % (p. 7), antigüedad, montos, plazos, niveles de aprobación.

Qué hace este módulo:
- lee los dos PDF con pdfplumber (la rutina básica de extracción del curso de RAG),
- los parte en fragmentos de párrafo con su documento, su página y su sección,
- guarda los fragmentos en datos/politicas_fragmentos.json para no releer los PDF en cada corrida,
- busca por coincidencia léxica ponderada (sin embeddings, para que el ejemplo no dependa de nada más),
- y verifica que las citas «[Tarifario, p. N]» de una respuesta estén entre los fragmentos recuperados.

Para el caso 2 incluye además cuatro solicitudes ficticias (sin DNI ni nombres) y las reglas de la Política
calculadas por CÓDIGO: la cuota y el porcentaje de carga no los estima el modelo.

La búsqueda es deliberadamente simple: los ejemplos tratan del bucle agéntico, no del RAG. El capítulo
de RAG sustituye esta función por búsqueda híbrida y estructural.

Prueba rápida:  python politicas_corpus.py "cuota máxima"
"""
from __future__ import annotations

import json
import math
import os
import re
import unicodedata
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(AQUI, 'datos')
CACHE = os.path.join(DATOS, 'politicas_fragmentos.json')

TARIFARIO = 'Tarifario'
POLITICA = 'Política de Créditos'
DOCUMENTOS = {   # nombre con que se cita → archivo y título completo
    TARIFARIO: {'archivo': 'reglamento-tarifario.pdf', 'titulo': 'Reglamento de Productos y Tarifario'},
    POLITICA: {'archivo': 'politica-creditos.pdf', 'titulo': 'Política de Créditos de Consumo'},
}

MODELO = 'claude-sonnet-5'
MODELO_RAPIDO = 'claude-haiku-4-5-20251001'

_VACIAS = set('''a al algo ante antes como con contra cual cuales cuando de del desde donde durante e el ella ellas ellos en entre
es esa esas ese eso esos esta estan estas este esto estos fue ha hace hacen hay la las le les lo los mas me mi muy no nos o
para pero por porque que quien quienes se sea segun ser si sin sobre son su sus tambien te tiene tienen todo todos tu un una
unas uno unos y ya cuanto cuanta cuantos dura debe deben puede pueden quiero necesito seria pagaria'''.split())
# Sinónimos mínimos del dominio: el cliente dice «pedir» o «gano»; el documento dice «solicitar» o «rendimiento».
_SINONIMOS = {'pedir': 'solicitar requisitos', 'necesito': 'requisitos', 'gano': 'rendimiento', 'ganaria': 'rendimiento',
              'reclamar': 'reclamo', 'presento': 'presentar', 'cobran': 'comisiones', 'tarda': 'plazo'}
_TITULO = re.compile(r'^\d{1,2}\.(\d{1,2})?\s+[A-ZÁÉÍÓÚÑ¿]')   # «5. Capacidad…» o «5.1 Cuota máxima…»


def _normalizar(texto: str) -> str:
    t = unicodedata.normalize('NFD', texto.lower())
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn')


def _tokens(texto: str) -> list[str]:
    """Palabras sin tildes ni vacías, recortadas a 5 letras («invierto» e «invierte» → «invie»); cifras enteras."""
    t = re.sub(r'(?<=\d),(?=\d{3})', '', _normalizar(texto))           # «10,000» → «10000»
    return [w if w.isdigit() else w[:5] for w in re.findall(r'[a-z0-9]+', t) if w not in _VACIAS and len(w) > 2]


def _extraer(documento: str) -> list[dict]:
    """Fragmentos de párrafo de un PDF. Salta la portada (p. 1), el índice (p. 2) y el pie de página."""
    import pdfplumber

    fragmentos: list[dict] = []
    with pdfplumber.open(os.path.join(DATOS, DOCUMENTOS[documento]['archivo'])) as pdf:
        for n, pagina in enumerate(pdf.pages, 1):
            if n <= 2:
                continue
            capitulo = seccion = ''
            actual: list[str] = []

            def cerrar() -> None:
                if actual:
                    fragmentos.append({'documento': documento, 'pagina': n, 'seccion': seccion,
                                       'texto': ' '.join(actual)})
                    actual.clear()

            for linea in (pagina.extract_text() or '').splitlines():
                linea = linea.strip()
                if not linea or 'Documento ficticio creado para el curso' in linea:
                    continue
                if _TITULO.match(linea) and len(linea) < 70:      # un título abre un fragmento nuevo
                    cerrar()
                    if re.match(r'^\d{1,2}\.\s', linea):             # «5. Capacidad de pago…»: título de sección
                        capitulo = seccion = linea
                    else:                                         # «5.1 Cuota máxima…»: ruta «5. … > 5.1 …»
                        seccion = f'{capitulo} > {linea}' if capitulo else linea
                    continue
                actual.append(linea)
                if linea.endswith(('.', ':')) and sum(len(x) for x in actual) >= 350:
                    cerrar()
            cerrar()
    return fragmentos


def _cache_vencida() -> bool:
    if not os.path.exists(CACHE):
        return True
    t = os.path.getmtime(CACHE)
    fuentes = [os.path.join(DATOS, d['archivo']) for d in DOCUMENTOS.values()] + [os.path.abspath(__file__)]
    return any(os.path.getmtime(f) > t for f in fuentes)            # un PDF o este troceo cambiaron


def fragmentos(documento: str | None = None) -> list[dict]:
    """Todos los fragmentos (id, documento, pagina, seccion, texto); solo los de un documento si se indica."""
    if _cache_vencida():
        datos = [f for doc in DOCUMENTOS for f in _extraer(doc)]
        for i, f in enumerate(datos):
            f['id'] = i
        with open(CACHE, 'w', encoding='utf-8') as fh:
            json.dump(datos, fh, ensure_ascii=False, indent=1)
    else:
        with open(CACHE, encoding='utf-8') as fh:
            datos = json.load(fh)
    return [f for f in datos if documento is None or f['documento'] == documento]


def buscar(pregunta: str, k: int = 4, documento: str | None = None) -> list[dict]:
    """Los k fragmentos con mayor puntuación léxica (TF-IDF) para la pregunta. Lista vacía si ninguno coincide.

    documento: TARIFARIO o POLITICA para buscar en uno solo; None busca en los dos.
    """
    docs = fragmentos(documento)
    tok_docs = [Counter(_tokens(f"{d['seccion']} {d['texto']}")) for d in docs]
    n = len(docs)
    df = Counter(t for c in tok_docs for t in c)
    consulta = set(_tokens(' '.join([pregunta] + [v for w, v in _SINONIMOS.items() if w in _normalizar(pregunta)])))
    puntuados = []
    for d, c in zip(docs, tok_docs):
        s = sum((1 + math.log(c[t])) * math.log(1 + n / df[t]) for t in consulta if c[t])
        if s > 0:
            puntuados.append((s, d))
    puntuados.sort(key=lambda x: -x[0])
    return [d for _, d in puntuados[:k]]


def cita(f: dict) -> str:
    return f"{f['documento']}, p. {f['pagina']}"


def formatear(parrafos: list[dict]) -> str:
    """Formato poka-yoke: siempre «[Tarifario, p. N] texto» o la cadena NO_ENCONTRADO, nunca una lista vacía."""
    if not parrafos:
        return 'NO_ENCONTRADO'
    return '\n\n'.join(f"[{cita(p)}] {p['texto']}" for p in parrafos)


def corpus_completo(documento: str | None = None) -> str:
    """Los documentos enteros con marcas de documento y página: el prefijo estable del ejemplo de prompt caching."""
    nombres = [documento] if documento else list(DOCUMENTOS)
    cabecera = ' y '.join(f"{DOCUMENTOS[d]['titulo']} (se cita «{d}, p. N»)" for d in nombres)
    return f'{cabecera}. Documentos ficticios creados para el curso.\n\n' + formatear(fragmentos(documento))


# ── Verificación de citas ────────────────────────────────────────────────────
_CITA = re.compile(r'(Tarifario|Pol[ií]tica de Cr[eé]ditos)\s*,?\s*p(?:ág(?:ina)?)?\.?\s*(\d+)', re.I)


def citas(texto: str) -> set[tuple[str, int]]:
    """Las citas de un texto como pares (documento, página). Entiende «Tarifario, p. 4», «[Política de Créditos, p. 7]»
    y «(Politica de Creditos, pág. 7)»."""
    salida = set()
    for doc, pag in _CITA.findall(texto):
        salida.add((TARIFARIO if doc.lower().startswith('tarif') else POLITICA, int(pag)))
    return salida


def verificar_citas(respuesta: str, parrafos: list[dict]) -> tuple[bool, str]:
    """Gate por código: la respuesta cita al menos una página y todas sus citas están entre los fragmentos recuperados."""
    citadas = citas(respuesta)
    recuperadas = {(p['documento'], p['pagina']) for p in parrafos}
    fmt = lambda s: sorted(f'{d}, p. {n}' for d, n in s)   # noqa: E731
    if not citadas:
        return False, 'la respuesta no cita ninguna página'
    if not citadas <= recuperadas:
        return False, f'cita páginas que la búsqueda no devolvió: {fmt(citadas - recuperadas)}'
    return True, f'cita {fmt(citadas)}, todas dentro de las recuperadas'


def cifras_sin_soporte(respuesta: str, parrafos: list[dict]) -> list[str]:
    """Porcentajes y montos en soles de la respuesta que no aparecen en ningún fragmento: una tasa o comisión inventada."""
    def norm(x: str) -> str:                                  # «14.0 %» == «14 %» · «S/ 10,000» == «S/10000»
        return re.sub(r'[\s,]', '', x).replace('.0%', '%')

    fuente = norm(' '.join(p['texto'] for p in parrafos))
    cifras = re.findall(r'\d+(?:\.\d+)?\s?%|S/\s?\d{1,3}(?:,\d{3})*(?:\.\d+)?', respuesta)
    return [c for c in cifras if not re.search(r'(?<![\d.])' + re.escape(norm(c)) + r'(?![\d.])', fuente)]


# ── Caso 2 · solicitudes ficticias y reglas de la Política calculadas por código ─────────────────
TASAS = [  # (desde, hasta, TEA 6-24 meses, TEA 25-60 meses) · Tarifario, p. 6
    (1_000, 4_999, 0.220, 0.240),
    (5_000, 19_999, 0.140, 0.150),
    (20_000, 50_000, 0.125, 0.135),
]

# Datos ficticios para el curso: solo id y cifras, nunca DNI ni nombres (Política de Créditos, p. 12).
SOLICITUDES = {
    'S-1042': {'ingreso_neto': 3_500, 'deudas_mensuales': 400, 'antiguedad_meses': 24, 'monto': 15_000, 'plazo': 36},
    'S-1043': {'ingreso_neto': 3_500, 'deudas_mensuales': 600, 'antiguedad_meses': 24, 'monto': 15_000, 'plazo': 36},
    'S-1051': {'ingreso_neto': 6_800, 'deudas_mensuales': 900, 'deudas_central': 1_150, 'antiguedad_meses': 7,
               'monto': 28_000, 'plazo': 48},
    'S-1060': {'ingreso_neto': 2_400, 'deudas_mensuales': 150, 'antiguedad_meses': 4, 'monto': 6_000, 'plazo': 24},
}


def tea(monto: float, plazo: int) -> float | None:
    """TEA del Tarifario para ese monto y plazo; None si el monto está fuera de S/ 1,000-50,000."""
    for desde, hasta, corta, larga in TASAS:
        if desde <= monto <= hasta:
            return corta if plazo <= 24 else larga
    return None


def cuota(monto: float, plazo: int, tasa: float) -> float:
    """Cuota fija mensual (método francés) con la TEA convertida a tasa mensual equivalente."""
    i = (1 + tasa) ** (1 / 12) - 1
    return monto * i / (1 - (1 + i) ** -plazo)


def evaluar_reglas(s: dict) -> dict:
    """Los hechos de la solicitud frente a la Política, calculados por código. Los agentes argumentan sobre esto."""
    deudas = max(s['deudas_mensuales'], s.get('deudas_central', 0))
    monto_ok = 1_000 <= s['monto'] <= 50_000
    plazo_ok = 6 <= s['plazo'] <= 60
    tasa = tea(s['monto'], s['plazo']) if monto_ok else None
    c = cuota(s['monto'], s['plazo'], tasa) if tasa and plazo_ok else None
    carga = (c + deudas) / s['ingreso_neto'] if c else None
    hechos = {
        'monto_en_rango (S/ 1,000-50,000)': monto_ok,
        'plazo_en_rango (6-60 meses)': plazo_ok,
        'tea': f'{tasa * 100:.1f} %' if tasa else None,
        'cuota': round(c) if c else None,
        'deudas_consideradas': deudas,
        'carga_total': round(c + deudas) if c else None,
        'carga_pct': round(carga * 100, 1) if carga else None,
        'cumple_30': carga is not None and carga <= 0.30,
        'antiguedad_ok (>= 6 meses)': s['antiguedad_meses'] >= 6,
        'antiguedad_justa (6 a 8 meses)': 6 <= s['antiguedad_meses'] <= 8,
        'deudas_no_declaradas': s.get('deudas_central', 0) > s['deudas_mensuales'],
        'requiere_jefe (> S/ 20,000)': s['monto'] > 20_000,
        'plazos_que_cumplen_30': None,
    }
    if carga is not None and carga > 0.30:               # ¿algún plazo mayor, hasta 60 meses, deja la carga en 30 % o menos?
        def con_plazo(p: int) -> str:
            cp = cuota(s['monto'], p, tea(s['monto'], p))
            return f'{p} meses: cuota S/ {cp:,.0f}, carga S/ {cp + deudas:,.0f} = {(cp + deudas) / s["ingreso_neto"] * 100:.1f} %'
        cumplen = [p for p in range(s['plazo'] + 1, 61)
                   if (cuota(s['monto'], p, tea(s['monto'], p)) + deudas) / s['ingreso_neto'] <= 0.30]
        hechos['plazos_que_cumplen_30'] = [con_plazo(cumplen[0]), con_plazo(60)] if cumplen else 'ninguno hasta 60 meses'
    return hechos


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    fs = fragmentos()
    for doc in DOCUMENTOS:
        print(f"{sum(1 for f in fs if f['documento'] == doc)} fragmentos de {DOCUMENTOS[doc]['titulo']} («{doc}, p. N»)")
    pregunta = ' '.join(sys.argv[1:]) or '¿Qué necesito para pedir un préstamo?'
    print(f'\nBúsqueda: «{pregunta}»')
    resultados = buscar(pregunta)
    for p in resultados:
        print(f"- [{cita(p)}] {p['seccion']} · {p['texto'][:140]}…")
    if not resultados:
        print('NO_ENCONTRADO')
    for muestra in ([f'Respuesta con cita recuperada ({cita(resultados[0])}).',
                     f'Respuesta con una cita inventada ({cita(resultados[0])}; Tarifario, p. 99).'] if resultados else []):
        print(f'\nverificar_citas(«{muestra}») → {verificar_citas(muestra, resultados)}')
