"""El orquestador del Tutor: coordinador que reparte, especialistas que ejecutan.

Cada especialista tiene sus tools, su tope de turnos y un esquema de salida. El
coordinador NO lee prosa: valida JSON contra el esquema y decide con eso.
"""
import asyncio
import json

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

ESQUEMAS = {
    "buscar":    {"type": "object", "required": ["items"], "properties": {"items": {"type": "array"}}},
    "redactar":  {"type": "object", "required": ["respuesta", "citas"]},
    "verificar": {"type": "object", "required": ["afirmaciones_sin_soporte"]},
}

ESPECIALISTAS = {
    "buscar":    dict(allowed_tools=["mcp__documentos__leer_documento"], max_turns=4,  model="haiku"),
    "redactar":  dict(allowed_tools=[],                                  max_turns=2,  model="sonnet"),
    "verificar": dict(allowed_tools=["Bash(python tutor/verificar.py *)"], max_turns=3, model="haiku"),
}


async def correr(rol: str, prompt: str) -> dict:
    opciones = ClaudeAgentOptions(
        setting_sources=["project"],                       # CLAUDE.md, reglas, hooks y skills del repo
        output_format={"type": "json_schema", "schema": ESQUEMAS[rol]},
        max_budget_usd=0.20,
        **ESPECIALISTAS[rol],
    )
    async for m in query(prompt=prompt, options=opciones):
        if isinstance(m, ResultMessage):
            if m.subtype != "success":                     # error_max_turns, error_max_budget_usd…
                return {"error": m.subtype, "costo": m.total_cost_usd}
            return json.loads(m.result)
    return {"error": "sin_resultado"}


async def responder(pregunta: str) -> dict:
    parrafos = await correr("buscar", f"<pregunta>{pregunta}</pregunta> Devuelve los párrafos con su página y su score.")

    # PARADA TEMPRANA: sin fuente no se redacta. Ahorra una llamada y elimina la alucinación de raíz.
    if not parrafos.get("items") or max(p["score"] for p in parrafos["items"]) < 0.35:
        return {"respuesta": "No encuentro eso en el documento", "citas": []}

    borrador = await correr("redactar", f"<parrafos>{json.dumps(parrafos)}</parrafos><pregunta>{pregunta}</pregunta>")

    for intento in (1, 2):                                  # TOPE DE REINTENTOS, no «hasta que salga»
        veredicto = await correr("verificar", f"<borrador>{json.dumps(borrador)}</borrador><parrafos>{json.dumps(parrafos)}</parrafos>")
        if not veredicto.get("afirmaciones_sin_soporte"):
            return borrador
        if intento == 2:
            return escalar_a_humano(pregunta, borrador, veredicto)
        borrador = await correr("redactar", f"Corrige estas afirmaciones sin soporte: {veredicto['afirmaciones_sin_soporte']}")


asyncio.run(responder("¿Qué es el acta de constitución del proyecto?"))
