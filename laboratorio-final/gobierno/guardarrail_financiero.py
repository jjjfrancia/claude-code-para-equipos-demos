"""Laboratorio: guardarraíl financiero para agentes que pagan con stablecoins (x402). Simulación.

Reglas del banco (Política de Gobierno de Agentes):
- Límite por transacción: 0.05 USDC.
- Límite diario por agente: 10.00 USDC. Por encima, se exige re-autenticación humana.
Montos en unidades mínimas enteras (USDC tiene 6 decimales): 0.05 USDC = 50_000.

Corre con: python guardarrail_financiero.py
"""
from collections import defaultdict

LIMITE_TRANSACCION = 50_000        # 0.05 USDC
LIMITE_DIARIO = 10_000_000         # 10.00 USDC

gasto_hoy = defaultdict(int)       # wallet -> unidades gastadas hoy
bitacora = []                      # trazabilidad: cada decisión queda registrada


def usdc(u: int) -> str:
    return f"{u / 1_000_000:.3f} USDC"


def guardarrail_financiero(wallet: str, monto: int) -> dict:
    """Se ejecuta en código ANTES de firmar cualquier pago. El modelo no puede saltarlo."""
    if monto <= 0:
        decision = {"valido": False, "razon": "BLOQUEADO: monto inválido."}
    elif monto > LIMITE_TRANSACCION:
        decision = {"valido": False, "razon": f"BLOQUEADO: {usdc(monto)} excede el límite por transacción de {usdc(LIMITE_TRANSACCION)}."}
    elif gasto_hoy[wallet] + monto > LIMITE_DIARIO:
        decision = {"valido": False, "razon": "BLOQUEADO: presupuesto diario agotado. Requiere re-autenticación humana."}
    else:
        gasto_hoy[wallet] += monto
        decision = {"valido": True, "razon": f"Aprobado. Gasto de hoy: {usdc(gasto_hoy[wallet])}."}
    bitacora.append({"wallet": wallet, "monto": usdc(monto), **decision})
    return decision


if __name__ == "__main__":
    agente = "0xAgenteClienteBanco"
    for monto in (5_000, 60_000):                       # 0.005 y 0.06 USDC
        print(f"Pago de {usdc(monto)} → {guardarrail_financiero(agente, monto)['razon']}")

    print("\nSimulación de un agente en bucle que paga 0.005 USDC sin parar…")
    pagos = 0
    while guardarrail_financiero(agente, 5_000)["valido"]:
        pagos += 1
    print(f"Pagos aprobados antes del bloqueo: {pagos} · gasto del día: {usdc(gasto_hoy[agente])}")
    print(f"Última decisión: {bitacora[-1]['razon']}")
    print(f"Registros en la bitácora: {len(bitacora)}")
