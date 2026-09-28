# La misma tool, pero dentro del proceso del agente (sin subproceso ni red)
from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server, tool

from tutor.buscar import buscar_hibrido


@tool("leer_documento",
      "Devuelve los párrafos del PMBOK/Guía Scrum que responden a la pregunta, con su página. "
      "Úsala antes de responder cualquier pregunta de metodología. Si no hay nada por encima "
      "del umbral devuelve SIN_RESULTADOS.",
      {"pregunta": str, "k": int})
async def leer_documento(args):
    parrafos = buscar_hibrido(args["pregunta"], k=args.get("k", 4))
    texto = "\n\n".join(f"[{p.doc} p.{p.pagina}] {p.texto}" for p in parrafos) or "SIN_RESULTADOS"
    return {"content": [{"type": "text", "text": texto}]}


documentos = create_sdk_mcp_server(name="documentos", version="1.0.0", tools=[leer_documento])

opciones = ClaudeAgentOptions(
    mcp_servers={"documentos": documentos},
    allowed_tools=["mcp__documentos__leer_documento"],   # el nombre: mcp__<servidor>__<tool>
    disallowed_tools=["Bash", "Write", "Edit"],          # este agente responde; no toca el disco
)
