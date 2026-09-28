"""Datos simulados del banco y las herramientas de solo lectura que usan los agentes.

Ninguna función modifica los datos: el agente de atención y el de consulta solo leen (Reglamento, p. 6).
Corre con: python -m banco.datos
"""
from __future__ import annotations

import json
import os
from datetime import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
_DATOS = os.path.join(AQUI, 'datos')

CAUSAS = {
    'fondos_insuficientes': 'fondos insuficientes en la cuenta de origen',
    'limite_diario_excedido': 'límite diario de S/ 5,000 en la app excedido',
    'cuenta_destino_invalida': 'cuenta de destino inválida',
    'bloqueo_preventivo': 'bloqueo preventivo por seguridad',
}

# OTP simulado: en producción lo envía el proveedor de SMS; aquí es fijo para poder practicar.
OTP_SIMULADO = '482913'


def _cargar(nombre: str) -> list[dict]:
    with open(os.path.join(_DATOS, nombre), encoding='utf-8') as f:
        return json.load(f)


def clientes() -> list[dict]: return _cargar('clientes.json')
def operaciones() -> list[dict]: return _cargar('operaciones.json')
def reclamos() -> list[dict]: return _cargar('reclamos.json')
def solicitudes() -> list[dict]: return _cargar('solicitudes.json')


def enmascarar(valor: str, visibles: int = 4) -> str:
    limpio = ''.join(c for c in str(valor) if c.isalnum())
    return '****' + limpio[-visibles:]


def cliente(codigo: str) -> dict | None:
    return next((c for c in clientes() if c['codigo'] == codigo), None)


def cliente_publico(codigo: str) -> dict | None:
    """El cliente sin datos sensibles: lo único que puede entrar a un prompt o a un log."""
    c = cliente(codigo)
    if not c:
        return None
    return {'codigo': c['codigo'], 'nombre': c['nombre'].split()[0], 'segmento': c['segmento'],
            'cuenta': enmascarar(c['cuenta']), 'dni': enmascarar(c['dni'], 3)}


def validar_identidad(codigo: str, otp: str) -> dict:
    c = cliente(codigo)
    if not c:
        return {'valido': False, 'motivo': 'cliente no existe'}
    if otp != OTP_SIMULADO:
        return {'valido': False, 'motivo': 'OTP incorrecto'}
    return {'valido': True, 'cliente': cliente_publico(codigo)}


def operaciones_de(codigo: str, tipo: str | None = None) -> list[dict]:
    return [o for o in operaciones() if o['cliente'] == codigo and tipo in (None, o['tipo'])]


def consultar_operacion(codigo: str, fecha: str | None = None, estado: str | None = None) -> list[dict]:
    """Operaciones del cliente filtradas por fecha (AAAA-MM-DD) y estado, con la causa explicada."""
    salida = []
    for o in operaciones_de(codigo):
        if fecha and not o['fecha'].startswith(fecha):
            continue
        if estado and o['estado'] != estado:
            continue
        o = dict(o)
        if o.get('causa'):
            o['causa_explicada'] = CAUSAS[o['causa']]
        if 'destino' in o:
            o['destino'] = o['destino']
        salida.append(o)
    return salida


def buscar_duplicados(codigo: str) -> list[tuple[dict, dict]]:
    """Pares de compras con mismo comercio, monto y minuto: la evidencia de un cargo duplicado."""
    compras = operaciones_de(codigo, 'compra_tarjeta')
    pares = []
    for i, a in enumerate(compras):
        for b in compras[i + 1:]:
            if (a['comercio'], a['monto'], a['fecha']) == (b['comercio'], b['monto'], b['fecha']):
                pares.append((a, b))
    return pares


def senales_de_fraude(codigo: str) -> list[str]:
    """Las tres señales de la Política de Reclamos, p. 7, calculadas en código."""
    c = cliente(codigo)
    compras = sorted(operaciones_de(codigo, 'compra_tarjeta'), key=lambda o: o['fecha'])
    senales = []
    fmt = '%Y-%m-%d %H:%M'
    for i in range(len(compras) - 2):
        a, z = compras[i], compras[i + 2]
        minutos = (datetime.strptime(z['fecha'], fmt) - datetime.strptime(a['fecha'], fmt)).seconds / 60
        comercios = {o['comercio'] for o in compras[i:i + 3]}
        if minutos < 10 and len(comercios) == 3:
            senales.append(f'3 compras en comercios distintos en {minutos:.0f} minutos')
            break
    if any(o['pais'] != 'PE' for o in compras):
        senales.append('compras en otro país sin aviso de viaje')
    if c and any(o['monto'] > 3 * c['promedio_compra'] for o in compras):
        senales.append(f"montos mayores a 3 veces su promedio (S/ {c['promedio_compra']:.2f})")
    return senales


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print('Identidad C-1001:', validar_identidad('C-1001', OTP_SIMULADO))
    print('Rechazadas de ayer:', consultar_operacion('C-1001', '2026-09-27', 'rechazada'))
    print('Duplicados C-1001:', [(a['id'], b['id']) for a, b in buscar_duplicados('C-1001')])
    print('Señales de fraude C-1002:', senales_de_fraude('C-1002'))
