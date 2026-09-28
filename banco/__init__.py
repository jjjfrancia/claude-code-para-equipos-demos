"""Módulo común del caso del banco (simulado) para todas las demos del curso.

- corpus:   los tres documentos del banco (políticas y reglamento) con búsqueda y cita de página.
- datos:    clientes, operaciones, reclamos y solicitudes simuladas; herramientas de solo lectura.
- politica: las reglas inquebrantables escritas en código (cuota ≤ 30 %, montos, plazos, devolución < S/ 50).

Todo es ficticio: no hay clientes, cuentas ni normativa reales.
"""
MODELO = 'claude-sonnet-5'
MODELO_RAPIDO = 'claude-haiku-4-5-20251001'
