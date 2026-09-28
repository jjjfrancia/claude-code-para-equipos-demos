"""Genera simulador-examen.html a partir de banco-preguntas/*.json y de los títulos de capítulo de index.html.

Corre con: python herramientas/armar_simulador.py
Valida cada pregunta (campos, dominio, task statement, 4 opciones, índice correcto) antes de escribir.
"""
import glob
import json
import os
import re
import sys
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS = {1: 7, 2: 5, 3: 6, 4: 6, 5: 6}   # task statements por dominio en la guía oficial


def validar(q: dict) -> list[str]:
    err = []
    for campo in ('id', 'cap', 'dominio', 'task', 'escenario', 'pregunta', 'opciones', 'correcta', 'explicacion'):
        if campo not in q:
            err.append(f'falta {campo}')
    if err:
        return err
    if q['dominio'] not in TASKS:
        err.append('dominio fuera de 1-5')
    m = re.fullmatch(r'(\d)\.(\d)', str(q['task']))
    if not m or int(m.group(1)) != q['dominio'] or not 1 <= int(m.group(2)) <= TASKS.get(q['dominio'], 0):
        err.append(f"task {q['task']} no corresponde al dominio {q['dominio']}")
    if not 1 <= q['escenario'] <= 6:
        err.append('escenario fuera de 1-6')
    if len(q['opciones']) != 4 or len(set(q['opciones'])) != 4:
        err.append('no tiene 4 opciones distintas')
    if q['correcta'] not in (0, 1, 2, 3):
        err.append('correcta fuera de 0-3')
    return err


def main() -> None:
    banco = []
    for f in sorted(glob.glob(os.path.join(RAIZ, 'banco-preguntas', 'cap*.json'))):
        banco += json.load(open(f, encoding='utf-8'))
    problemas = [(q.get('id'), e) for q in banco for e in validar(q)]
    ids = Counter(q.get('id') for q in banco)
    problemas += [(i, 'id repetido') for i, n in ids.items() if n > 1]
    if problemas:
        for p in problemas:
            print('✗', *p)
        sys.exit(1)

    index = open(os.path.join(RAIZ, 'index.html'), encoding='utf-8').read()
    capitulos = {int(n) + 1: t.strip() for n, t in re.findall(
        r'id="mtitle-(\d+)">([^<]+)</span>', index)}

    plantilla = open(os.path.join(RAIZ, 'herramientas', 'simulador-plantilla.html'), encoding='utf-8').read()
    html = (plantilla
            .replace('/*BANCO*/[]', json.dumps(banco, ensure_ascii=False))
            .replace('/*CAPITULOS*/{}', json.dumps(capitulos, ensure_ascii=False)))
    open(os.path.join(RAIZ, 'simulador-examen.html'), 'w', encoding='utf-8').write(html)

    print(f'simulador-examen.html: {len(banco)} preguntas')
    print('  por dominio:', dict(sorted(Counter(q['dominio'] for q in banco).items())))
    print('  por capítulo:', dict(sorted(Counter(q['cap'] for q in banco).items())))
    print('  posición de la correcta:', dict(sorted(Counter(q['correcta'] for q in banco).items())))


if __name__ == '__main__':
    main()
