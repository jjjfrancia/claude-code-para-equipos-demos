"""Ejemplo 06 · Evaluator-optimizer: un generador y un evaluador en bucle, con criterios binarios y tope de iteraciones.

Concepto (Building effective agents): efectivo cuando hay criterios de evaluación claros y el refinamiento
iterativo aporta valor medible. Dos señales: un humano mejoraría la respuesta con feedback, y el LLM puede darlo.

Qué observar: dos criterios los mide el CÓDIGO (longitud y páginas citadas) y uno el modelo evaluador
(¿algo fuera de los párrafos?). El bucle termina en APROBADO o tras 3 rondas: una condición de parada explícita.
"""
import sys

import anthropic

from tutor_corpus import MODELO, MODELO_RAPIDO, buscar, formatear, paginas_citadas

sys.stdout.reconfigure(encoding='utf-8')
client = anthropic.Anthropic()
MAX_RONDAS = 3
MAX_CARACTERES = 600


def llamar(modelo: str, system: str, usuario: str, max_tokens: int = 600) -> str:
    r = client.messages.create(model=modelo, max_tokens=max_tokens, system=system,
                               messages=[{'role': 'user', 'content': usuario}])
    return ''.join(b.text for b in r.content if b.type == 'text').strip()


def evaluar(respuesta: str, parrafos: list[dict]) -> list[str]:
    fallos = []
    if len(respuesta) > MAX_CARACTERES:
        fallos.append(f'C1 longitud: {len(respuesta)} caracteres, el máximo es {MAX_CARACTERES}')
    citadas, recuperadas = paginas_citadas(respuesta), {p['pagina'] for p in parrafos}
    if not citadas or not citadas <= recuperadas:
        fallos.append(f'C2 citas: citadas {sorted(citadas)}, válidas {sorted(recuperadas)}')
    juicio = llamar(MODELO_RAPIDO,
                    'Eres un evaluador estricto. Si la respuesta contiene alguna afirmación que no esté en los párrafos, '
                    'escribe «C3 soporte:» y la afirmación exacta. Si todo tiene soporte, escribe solo OK.',
                    f'Párrafos:\n{formatear(parrafos)}\n\nRespuesta:\n{respuesta}', 200)
    if not juicio.upper().startswith('OK'):
        fallos.append(juicio)
    return fallos


def main(pregunta: str) -> None:
    parrafos = buscar(pregunta)
    contexto = f'Pregunta: {pregunta}\n\nPárrafos:\n{formatear(parrafos)}'
    system = f'Responde SOLO con los párrafos, en menos de {MAX_CARACTERES} caracteres, citando la página (p. N) de cada afirmación.'
    respuesta = llamar(MODELO, system, contexto)
    for ronda in range(1, MAX_RONDAS + 1):
        fallos = evaluar(respuesta, parrafos)
        print(f'\n── ronda {ronda} ({len(respuesta)} caracteres)\n{respuesta}')
        if not fallos:
            print('\nevaluador: APROBADO')
            return
        print('evaluador: ' + ' | '.join(fallos))
        if ronda == MAX_RONDAS:
            print(f'\nparada: {MAX_RONDAS} rondas sin aprobar. La respuesta NO se envía; se escala a un humano.')
            return
        respuesta = llamar(MODELO, system, f'{contexto}\n\nTu respuesta anterior:\n{respuesta}\n\nCorrige exactamente estos fallos:\n' + '\n'.join(fallos))


if __name__ == '__main__':
    main(' '.join(sys.argv[1:]) or '¿Cuáles son las responsabilidades del Scrum Master con la organización?')
