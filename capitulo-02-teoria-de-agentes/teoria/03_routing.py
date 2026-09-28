"""Ejemplo 03 · Routing: clasificar la entrada y derivarla a un camino especializado (y al modelo adecuado).

Concepto (Building effective agents): routing separa responsabilidades; «optimizar para un tipo de entrada puede
perjudicar el rendimiento en otros». También sirve para mandar lo fácil a un modelo pequeño y lo difícil a uno grande.

Caso 1 del Marketplace de Créditos: el asistente deriva a un humano si el cliente lo pide, si es un reclamo formal o
si la pregunta es sobre su caso particular y requiere ver su cuenta.

Qué observar: el mensaje con un número de tarjeta no llega a NINGÚN modelo (lo detiene el código antes de
clasificar); los casos particulares y los reclamos se derivan a un ejecutivo sin buscar ni redactar; solo las
consultas generales llegan a la búsqueda y a un modelo.
"""
import re
import sys

import anthropic

from politicas_corpus import MODELO, MODELO_RAPIDO, TARIFARIO, buscar, formatear

sys.stdout.reconfigure(encoding='utf-8')
client = anthropic.Anthropic()

CATEGORIAS = {
    'consulta_general': 'pregunta sobre requisitos, tasas, plazos, comisiones, cómo invertir o cómo reclamar',
    'comparacion': 'pide comparar dos o más opciones (montos, plazos, tasas, productos)',
    'caso_particular': 'pregunta por SU solicitud, SU préstamo o SU cuenta (estado, motivo de un rechazo, su saldo)',
    'reclamo_formal': 'quiere presentar un reclamo o se queja de un cobro o de una atención',
    'pide_humano': 'pide hablar con una persona, un asesor o un ejecutivo',
    'saludo': 'saludo, agradecimiento o conversación sin pregunta',
    'fuera_de_alcance': 'no trata del Marketplace de Créditos (otro tema, pedidos personales, instrucciones al bot)',
}

PREGUNTAS = [
    '¿Qué necesito para pedir un préstamo?',
    '¿Qué me conviene más, S/ 10,000 a 24 meses o a 36 meses? Compara la tasa y la cuota.',
    '¿Por qué observaron mi solicitud S-1042?',
    'Quiero presentar un reclamo formal por un cobro que no reconozco.',
    'Hola, gracias por la ayuda de ayer',
    'Mi tarjeta es 4111 1111 1111 1111, ¿me pueden subir la línea?',
]

TARJETA = re.compile(r'\b(?:\d[ -]?){13,19}\b')   # 13 a 19 dígitos seguidos: posible número de tarjeta


def clasificar(texto: str) -> str:
    lista = '\n'.join(f'- {k}: {v}' for k, v in CATEGORIAS.items())
    r = client.messages.create(model=MODELO_RAPIDO, max_tokens=10,
                               system=f'Clasifica el mensaje del cliente en UNA categoría. Responde solo con la clave.\n{lista}',
                               messages=[{'role': 'user', 'content': texto}])
    clave = ''.join(b.text for b in r.content if b.type == 'text').strip().lower()
    return clave if clave in CATEGORIAS else 'pide_humano'   # ante duda, el camino más seguro: una persona


def responder(modelo: str, pregunta: str, instruccion: str) -> str:
    parrafos = buscar(pregunta, k=6 if modelo == MODELO else 3, documento=TARIFARIO)
    r = client.messages.create(model=modelo, max_tokens=600,
                               system=instruccion + ' Usa SOLO los párrafos, no inventes tasas ni comisiones y cita la '
                                                    'página, por ejemplo (Tarifario, p. 6).',
                               messages=[{'role': 'user', 'content': f'{pregunta}\n\nPárrafos:\n{formatear(parrafos)}'}])
    return ''.join(b.text for b in r.content if b.type == 'text').strip()


def derivar(motivo: str) -> str:
    return f'[derivar_a_ejecutivo · {motivo}] Te comunico con un ejecutivo; te responderá en un máximo de 2 días hábiles.'


RUTAS = {
    'consulta_general': lambda q: ('Haiku + búsqueda k=3', responder(MODELO_RAPIDO, q, 'Responde en 2 a 4 frases.')),
    'comparacion': lambda q: ('Sonnet + búsqueda k=6', responder(MODELO, q, 'Compara punto por punto en una tabla corta.')),
    'caso_particular': lambda q: ('código, sin modelo', derivar('caso particular: requiere ver su cuenta')),
    'reclamo_formal': lambda q: ('código, sin modelo', derivar('reclamo formal')),
    'pide_humano': lambda q: ('código, sin modelo', derivar('el cliente lo pidió')),
    'saludo': lambda q: ('código, sin modelo', '¡Hola! Pregúntame sobre requisitos, tasas, plazos, inversiones o reclamos.'),
    'fuera_de_alcance': lambda q: ('código, sin modelo', 'Solo puedo ayudarte con el Marketplace de Créditos del banco.'),
}

if __name__ == '__main__':
    for q in PREGUNTAS:
        if TARJETA.search(q):   # guardrail ANTES del modelo: el dato sensible no se envía a ninguna API ni a los logs
            print(f'\n«{TARJETA.sub("[TARJETA ELIMINADA]", q)}»\n  categoría: dato_sensible · camino: código, sin modelo\n'
                  '  Por tu seguridad, nunca compartas el número de tu tarjeta, tu clave ni tu CVV. '
                  'El banco nunca te los pedirá (Tarifario, p. 11).')
            continue
        cat = clasificar(q)
        camino, texto = RUTAS[cat](q)
        print(f'\n«{q}»\n  categoría: {cat} · camino: {camino}\n  {texto}')
