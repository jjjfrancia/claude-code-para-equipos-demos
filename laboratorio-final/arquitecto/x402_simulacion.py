"""Laboratorio: micropagos entre agentes con el protocolo x402 (SIMULACIÓN, sin blockchain ni dinero real).

El Agente Cliente pide un reporte de crédito al Agente Evaluador del banco. El servidor del banco responde
402 Payment Required; el cliente paga 0.005 USDC (simulado), reintenta con el comprobante y recibe el reporte.

Lo que enseña, además del flujo:
- El cobro lo exige el SERVIDOR en código, antes de llegar al agente (no el prompt).
- Un comprobante solo sirve una vez (protección contra reutilización).
- El pago tiene que ir a la billetera del banco y por el monto exacto.
- Los montos se manejan en unidades mínimas enteras: USDC tiene 6 decimales, 0.005 USDC = 5000.

Corre con: python x402_simulacion.py
"""
import time
import uuid

WALLETS = {
    "agente_banco": "0xAgenteEvaluadorBanco789XYZ",
    "agente_cliente": "0xAgenteCliente123ABC",
}
PRECIO_UNIDADES = 5000          # 0.005 USDC en unidades mínimas (6 decimales)
RED = "base-sepolia"            # red de prueba: en clase no se usa dinero real

blockchain_simulada = {}        # hash -> {origen, destino, monto}


def usdc(unidades: int) -> str:
    return f"{unidades / 1_000_000:.3f} USDC"


def agente_evaluador(perfil: dict) -> str:
    """El agente (aquí simulado) solo analiza; no sabe nada de cobros."""
    return "Riesgo bajo: carga de deuda 22 % del ingreso (Política de Créditos, p. 7). Recomendación: aprobar."


class ServidorBanco:
    def __init__(self):
        self.pagos_usados = set()

    def evaluar_credito(self, perfil: dict, headers: dict | None = None) -> dict:
        headers = headers or {}
        comprobante = headers.get("X-PAYMENT")

        # 1) Sin comprobante: el servidor responde 402 con los requisitos de pago.
        if not comprobante:
            return {"status": 402, "error": "Payment Required", "accepts": [{
                "scheme": "exact", "network": RED, "maxAmountRequired": str(PRECIO_UNIDADES),
                "payTo": WALLETS["agente_banco"], "resource": "/evaluar_credito",
                "description": "Reporte de riesgo crediticio"}]}

        # 2) Verificación del pago, en código, antes de llamar al agente.
        tx = blockchain_simulada.get(comprobante)
        if tx is None:
            return {"status": 402, "error": "Pago no encontrado"}
        if comprobante in self.pagos_usados:
            return {"status": 402, "error": "Comprobante ya utilizado"}
        if tx["destino"] != WALLETS["agente_banco"]:
            return {"status": 402, "error": "El pago no fue a la billetera del banco"}
        if tx["monto"] < PRECIO_UNIDADES:
            return {"status": 402, "error": f"Monto insuficiente: {usdc(tx['monto'])}"}

        self.pagos_usados.add(comprobante)
        # 3) Solo ahora el agente recibe la solicitud.
        return {"status": 200, "X-PAYMENT-RESPONSE": comprobante, "reporte": agente_evaluador(perfil)}


def pagar(origen: str, destino: str, monto: int) -> str:
    """Simula una transferencia on-chain y devuelve su hash."""
    tx_hash = "0x" + uuid.uuid4().hex[:16]
    time.sleep(0.5)                                   # latencia de una red rápida (L2)
    blockchain_simulada[tx_hash] = {"origen": origen, "destino": destino, "monto": monto}
    return tx_hash


if __name__ == "__main__":
    banco = ServidorBanco()
    perfil = {"solicitud": "S-2087", "ingreso_neto": 4200, "deudas": 900}

    print("🤖 [Agente cliente] Pido la evaluación sin pagar…")
    r1 = banco.evaluar_credito(perfil)
    print(f"📡 [Servidor banco] HTTP {r1['status']} {r1['error']}")

    req = r1["accepts"][0]
    monto = int(req["maxAmountRequired"])
    print(f"💰 [Agente cliente] Pago {usdc(monto)} a {req['payTo']} en {req['network']}…")
    tx = pagar(WALLETS["agente_cliente"], req["payTo"], monto)
    print(f"🔗 [Blockchain simulada] Confirmada: {tx}")

    print("\n🤖 [Agente cliente] Reintento con el comprobante en X-PAYMENT…")
    r2 = banco.evaluar_credito(perfil, headers={"X-PAYMENT": tx})
    print(f"📡 [Servidor banco] HTTP {r2['status']}")
    print(f"📊 [Reporte] {r2.get('reporte')}")

    print("\n🕵 [Prueba de seguridad] Reutilizo el mismo comprobante…")
    r3 = banco.evaluar_credito(perfil, headers={"X-PAYMENT": tx})
    print(f"📡 [Servidor banco] HTTP {r3['status']} {r3['error']}")
