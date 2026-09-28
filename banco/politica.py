"""Las reglas inquebrantables del banco, escritas en código y no en el prompt.

Un agente puede recomendar lo que quiera; estas funciones deciden si la recomendación es admisible.
Corre con: python -m banco.politica
"""
from __future__ import annotations

TEA = 0.15                       # Política de Créditos, p. 8
CARGA_MAXIMA = 0.30              # p. 7
MONTO_MIN, MONTO_MAX = 1_000, 50_000   # p. 2
PLAZO_MIN, PLAZO_MAX = 6, 60           # p. 3
UMBRAL_AUTOMATICO = 20_000             # p. 9
DEVOLUCION_AUTOMATICA_MAX = 50.00      # Política de Reclamos, p. 3 (estrictamente menor)


def cuota(monto: float, plazo: int, tea: float = TEA) -> float:
    """Cuota fija mensual (sistema francés) con la TEA convertida a tasa mensual."""
    i = (1 + tea) ** (1 / 12) - 1
    return round(monto * i / (1 - (1 + i) ** -plazo), 2)


def carga(solicitud: dict, plazo: int | None = None, monto: float | None = None) -> float:
    c = cuota(monto or solicitud['monto'], plazo or solicitud['plazo'])
    return (c + solicitud['deudas_mensuales'] + solicitud.get('deudas_no_declaradas', 0)) / solicitud['ingreso_neto']


def verificar_credito(s: dict) -> dict:
    """Aplica la política completa. Devuelve {cumple, violaciones, revision_humana, jefe, cuota, carga}."""
    violaciones, revision = [], []
    if not MONTO_MIN <= s['monto'] <= MONTO_MAX:
        violaciones.append(f"monto S/ {s['monto']:,} fuera de S/ 1,000–50,000 (Política de Créditos, p. 2)")
    if not PLAZO_MIN <= s['plazo'] <= PLAZO_MAX:
        violaciones.append(f"plazo {s['plazo']} meses fuera de 6–60 (Política de Créditos, p. 3)")
    minimo = 6 if s['tipo_empleo'] == 'dependiente' else 12
    if s['antiguedad_meses'] < minimo:
        violaciones.append(f"antigüedad {s['antiguedad_meses']} meses < {minimo} (Política de Créditos, p. 4)")
    if not s.get('documentos_completos', True):
        revision.append('documentos incompletos (Política de Créditos, p. 5)')
    if s['central_riesgo'] != 'Normal':
        revision.append(f"central de riesgo «{s['central_riesgo']}» (Política de Créditos, p. 6)")
    if s.get('deudas_no_declaradas'):
        revision.append(f"deudas no declaradas S/ {s['deudas_no_declaradas']}/mes (Política de Créditos, p. 6)")
    c = cuota(s['monto'], s['plazo'])
    k = carga(s)
    if k > CARGA_MAXIMA:
        violaciones.append(f'carga {k:.0%} > 30 % del ingreso (Política de Créditos, p. 7)')
    return {'cumple': not violaciones, 'violaciones': violaciones, 'revision_humana': revision,
            'jefe_de_creditos': s['monto'] > UMBRAL_AUTOMATICO, 'cuota': c, 'carga': round(k, 4)}


def plazo_minimo_que_cumple(s: dict) -> int | None:
    """El menor plazo (6–60) con el que la carga queda ≤ 30 %: la contrapropuesta del agente flexible."""
    for p in range(max(s['plazo'], PLAZO_MIN), PLAZO_MAX + 1):
        if carga(s, plazo=p) <= CARGA_MAXIMA:
            return p
    return None


def decision_admisible(s: dict, decision: str, condiciones: dict | None = None) -> tuple[bool, str]:
    """Filtro final sobre lo que dice el juez. decision ∈ aprobar | aprobar_con_condiciones | rechazar | escalar."""
    if decision in ('rechazar', 'escalar'):
        return True, 'ok'
    ajustada = dict(s, **(condiciones or {}))
    v = verificar_credito(ajustada)
    if not v['cumple']:
        return False, 'viola la política: ' + '; '.join(v['violaciones'])
    if v['revision_humana']:
        return False, 'requiere revisión humana: ' + '; '.join(v['revision_humana'])
    if v['jefe_de_creditos']:
        return False, 'más de S/ 20,000: aprueba el analista y el jefe de créditos (Política de Créditos, p. 9)'
    return True, 'ok'


def verificar_devolucion(monto: float, categoria: str) -> tuple[bool, str]:
    """Lo que hace cumplir el hook antes de ejecutar una devolución (Política de Reclamos, p. 3 y 4)."""
    if categoria != 'cargo_duplicado':
        return False, f'categoría {categoria}: se escala a un analista (Política de Reclamos, p. 4)'
    if monto >= DEVOLUCION_AUTOMATICA_MAX:
        return False, f'S/ {monto:.2f} ≥ S/ 50.00: se escala a un analista (Política de Reclamos, p. 4)'
    return True, 'ok'


if __name__ == '__main__':
    import sys
    from banco import datos
    sys.stdout.reconfigure(encoding='utf-8')
    for s in datos.solicitudes():
        v = verificar_credito(s)
        print(s['id'], f"cuota S/ {v['cuota']:.2f}", f"carga {v['carga']:.0%}", v['violaciones'] or 'cumple',
              v['revision_humana'] or '', 'jefe' if v['jefe_de_creditos'] else '',
              f"plazo que cumple: {plazo_minimo_que_cumple(s)}")
    print(verificar_devolucion(38.90, 'cargo_duplicado'), verificar_devolucion(80.00, 'cargo_duplicado'))
