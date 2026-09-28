"""Genera <carpeta>/simulador-examen.html a partir de <carpeta>/banco-preguntas/*.json.

Corre con: python herramientas/armar_simulador.py <curso>
<curso> es una clave de herramientas/cursos.json. Valida cada pregunta (campos, dominio y task statement
del examen del curso, 4 opciones distintas, índice correcto, ids únicos) antes de escribir.
"""
import glob
import json
import os
import re
import sys
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURSOS = json.load(open(os.path.join(RAIZ, 'herramientas', 'cursos.json'), encoding='utf-8'))
EXAMENES = json.load(open(os.path.join(RAIZ, 'herramientas', 'examenes.json'), encoding='utf-8'))


def validar(q: dict, examen: dict) -> list[str]:
    err = [f'falta {c}' for c in ('id', 'cap', 'dominio', 'task', 'pregunta', 'opciones', 'correcta', 'explicacion') if c not in q]
    if err:
        return err
    dom = examen['dominios'].get(str(q['dominio']))
    if not dom:
        return [f"dominio {q['dominio']} no existe en el examen"]
    if str(q['task']) not in dom['tasks']:
        err.append(f"task {q['task']} no pertenece al dominio {q['dominio']}")
    if examen['escenarios'] and str(q.get('escenario')) not in examen['escenarios']:
        err.append('escenario inválido')
    if len(q['opciones']) != 4 or len(set(q['opciones'])) != 4:
        err.append('no tiene 4 opciones distintas')
    if q['correcta'] not in (0, 1, 2, 3):
        err.append('correcta fuera de 0-3')
    return err


def main() -> None:
    clave = sys.argv[1] if len(sys.argv) > 1 else 'claude-code'
    curso = CURSOS[clave]
    examen = EXAMENES[curso['examen']]
    carpeta = os.path.normpath(os.path.join(RAIZ, curso['carpeta']))

    banco = []
    for f in sorted(glob.glob(os.path.join(carpeta, 'banco-preguntas', 'cap*.json'))):
        banco += json.load(open(f, encoding='utf-8'))
    problemas = [(q.get('id'), e) for q in banco for e in validar(q, examen)]
    problemas += [(i, 'id repetido') for i, n in Counter(q.get('id') for q in banco).items() if n > 1]
    if problemas:
        for p in problemas:
            print('✗', *p)
        sys.exit(1)

    index = open(os.path.join(carpeta, 'index.html'), encoding='utf-8').read()
    capitulos = {int(n): t.strip() for n, t in
                 re.findall(r'<div id="lp-(\d+)"[^>]*>.*?<span class="breadcrumb-lesson">([^<]*)</span>', index, re.S)}

    cfg = dict(examen, codigo=curso['examen'], subtitulo=f'Banco de {len(banco)} preguntas del curso {curso["titulo"]} · caso: Marketplace de Créditos')
    plantilla = open(os.path.join(RAIZ, 'herramientas', 'simulador-plantilla.html'), encoding='utf-8').read()
    html = (plantilla
            .replace('/*BANCO*/[]', json.dumps(banco, ensure_ascii=False))
            .replace('/*CAPITULOS*/{}', json.dumps(capitulos, ensure_ascii=False))
            .replace('/*EXAMEN*/{}', json.dumps(cfg, ensure_ascii=False)))
    open(os.path.join(carpeta, 'simulador-examen.html'), 'w', encoding='utf-8').write(html)

    print(f'  simulador {curso["examen"]}: {len(banco)} preguntas · por dominio',
          dict(sorted(Counter(q['dominio'] for q in banco).items())),
          '· correcta en', dict(sorted(Counter(q['correcta'] for q in banco).items())))


if __name__ == '__main__':
    main()
